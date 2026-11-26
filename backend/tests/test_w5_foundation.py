import uuid
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateTable, CreateIndex

from app.core.config import settings
from app.core.security import create_access_token, decode_access_token
from app.db.database import Base, get_db, engine
from app.main import app
from app.models import User, NoticeDocument


class _FakeResult:
    def __init__(self, value):
        self._value = value

    def scalar_one_or_none(self):
        return self._value


class _InMemoryAsyncSession:
    """Minimal async session double for testing auth endpoints without a live DB."""

    def __init__(self):
        self.users_by_email: dict[str, User] = {}

    async def execute(self, stmt):
        # Extract email from compiled WHERE clause parameter if present
        compiled = stmt.compile(dialect=postgresql.dialect())
        email = next(iter(compiled.params.values()), None)
        return _FakeResult(self.users_by_email.get(email))

    def add(self, obj):
        if isinstance(obj, User):
            if obj.id is None:
                obj.id = uuid.uuid4()
            self.users_by_email[obj.email] = obj

    async def commit(self):
        return None

    async def refresh(self, obj):
        return None


@pytest.fixture()
def client_with_fake_db():
    fake_db = _InMemoryAsyncSession()

    async def _override_get_db():
        yield fake_db

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as client:
        yield client, fake_db
    app.dependency_overrides.clear()


def test_jwt_settings_and_token_roundtrip():
    assert settings.SECRET_KEY
    assert settings.ALGORITHM == "HS256"
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES > 0
    assert settings.ALLOWED_EMAIL_DOMAIN == "iut-dhaka.edu"

    token = create_access_token(
        subject="zahin@iut-dhaka.edu",
        expires_delta=timedelta(minutes=5),
        extra_claims={"role": "CR"},
    )
    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == "zahin@iut-dhaka.edu"
    assert payload["role"] == "CR"

    assert decode_access_token("not.a.valid.jwt") is None


def test_postgresql_models_and_ddl():
    assert "postgresql+asyncpg" in str(engine.url)

    users_ddl = str(CreateTable(User.__table__).compile(dialect=postgresql.dialect()))
    docs_ddl = str(CreateTable(NoticeDocument.__table__).compile(dialect=postgresql.dialect()))

    assert "CREATE TABLE users" in users_ddl
    assert "email VARCHAR(255) NOT NULL" in users_ddl

    assert "CREATE TABLE documents" in docs_ddl
    assert "notice_metadata JSONB NOT NULL" in docs_ddl
    assert "FOREIGN KEY(uploader_id) REFERENCES users (id)" in docs_ddl
    assert "FOREIGN KEY(verified_by) REFERENCES users (id)" in docs_ddl

    gin_indexes = [idx for idx in NoticeDocument.__table__.indexes if idx.name == "ix_documents_metadata_gin"]
    assert len(gin_indexes) == 1
    gin_ddl = str(CreateIndex(gin_indexes[0]).compile(dialect=postgresql.dialect()))
    assert "USING gin" in gin_ddl


def test_health_endpoint(client_with_fake_db):
    client, _ = client_with_fake_db
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert "PostgreSQL" in data["database"]


def test_dev_login_valid_iut_email_and_me(client_with_fake_db):
    client, fake_db = client_with_fake_db
    resp = client.post(
        f"{settings.API_V1_STR}/auth/dev-login",
        params={"email": "zahin002@iut-dhaka.edu", "role": "CR"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["token_type"] == "bearer"
    assert body["user"]["email"] == "zahin002@iut-dhaka.edu"
    assert body["user"]["role"] == "CR"
    assert "zahin002@iut-dhaka.edu" in fake_db.users_by_email

    me_resp = client.get(
        f"{settings.API_V1_STR}/auth/me",
        headers={"Authorization": f"Bearer {body['access_token']}"},
    )
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == "zahin002@iut-dhaka.edu"


def test_dev_login_rejects_non_iut_email(client_with_fake_db):
    client, _ = client_with_fake_db
    resp = client.post(
        f"{settings.API_V1_STR}/auth/dev-login",
        params={"email": "outsider@gmail.com"},
    )
    assert resp.status_code == 403


def test_me_requires_valid_jwt(client_with_fake_db):
    client, _ = client_with_fake_db
    assert client.get(f"{settings.API_V1_STR}/auth/me").status_code == 401
    assert (
        client.get(
            f"{settings.API_V1_STR}/auth/me",
            headers={"Authorization": "Bearer invalid-token"},
        ).status_code
        == 401
    )


def test_google_login_domain_validation(client_with_fake_db):
    client, _ = client_with_fake_db

    with patch(
        "app.api.v1.auth._verify_google_credentials",
        new=AsyncMock(return_value={"email": "student@iut-dhaka.edu", "name": "IUT Student"}),
    ):
        ok_resp = client.post(
            f"{settings.API_V1_STR}/auth/google/login",
            json={"id_token": "fake-google-id-token"},
        )
        assert ok_resp.status_code == 200
        assert ok_resp.json()["user"]["email"] == "student@iut-dhaka.edu"
        assert ok_resp.json()["user"]["role"] == "STUDENT"

    with patch(
        "app.api.v1.auth._verify_google_credentials",
        new=AsyncMock(return_value={"email": "user@gmail.com", "name": "External User"}),
    ):
        bad_resp = client.post(
            f"{settings.API_V1_STR}/auth/google/login",
            json={"id_token": "fake-google-id-token"},
        )
        assert bad_resp.status_code == 403
