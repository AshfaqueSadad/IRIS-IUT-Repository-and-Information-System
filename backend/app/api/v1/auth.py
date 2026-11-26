from typing import Optional
import uuid
import httpx
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.security import create_access_token, decode_access_token
from app.schemas.user import UserRole, UserResponse, GoogleLoginRequest, Token
from app.models.user import User
from app.db.database import get_db

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/dev-login")


def validate_iut_email_domain(email: str) -> str:
    """Ensure the email belongs to the allowed university domain (@iut-dhaka.edu)."""
    normalized = email.strip().lower()
    allowed_suffix = f"@{settings.ALLOWED_EMAIL_DOMAIN.lower()}"
    if not normalized.endswith(allowed_suffix):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Only @{settings.ALLOWED_EMAIL_DOMAIN} accounts are permitted.",
        )
    return normalized


async def _get_or_create_user(
    db: AsyncSession,
    email: str,
    full_name: str,
    default_role: UserRole = UserRole.STUDENT,
    department: Optional[str] = None,
    batch: Optional[str] = None,
) -> UserResponse:
    """Look up user in PostgreSQL by email, or create a new record if first login."""
    result = await db.execute(select(User).where(User.email == email))
    user_row = result.scalar_one_or_none()
    if user_row is None:
        user_row = User(
            id=uuid.uuid4(),
            email=email,
            full_name=full_name,
            role=default_role.value,
            department=department,
            batch=batch,
            is_active=True,
        )
        db.add(user_row)
        await db.commit()
        await db.refresh(user_row)
    return UserResponse.model_validate(user_row)


async def _verify_google_credentials(payload: GoogleLoginRequest) -> dict:
    """Verify Google ID token or authorization code with Google OAuth2 endpoints."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        if payload.id_token:
            resp = await client.get(
                "https://oauth2.googleapis.com/tokeninfo",
                params={"id_token": payload.id_token},
            )
            if resp.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid Google ID token.",
                )
            data = resp.json()
            if settings.GOOGLE_CLIENT_ID and data.get("aud") != settings.GOOGLE_CLIENT_ID:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Google token audience mismatch.",
                )
            return data

        if payload.code:
            if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Google OAuth client credentials are not configured.",
                )
            token_resp = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": payload.code,
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "redirect_uri": payload.redirect_uri or "postmessage",
                    "grant_type": "authorization_code",
                },
            )
            if token_resp.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Failed to exchange Google authorization code.",
                )
            id_token = token_resp.json().get("id_token")
            if not id_token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Google token response missing id_token.",
                )
            info_resp = await client.get(
                "https://oauth2.googleapis.com/tokeninfo",
                params={"id_token": id_token},
            )
            if info_resp.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid Google ID token.",
                )
            return info_resp.json()

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Either id_token or code must be provided.",
    )


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    email: Optional[str] = payload.get("sub")
    if not email:
        raise credentials_exception

    validate_iut_email_domain(email)

    result = await db.execute(select(User).where(User.email == email))
    user_row = result.scalar_one_or_none()
    if user_row is not None:
        if not user_row.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive.",
            )
        return UserResponse.model_validate(user_row)

    raise credentials_exception


def require_role(allowed_roles: list[UserRole]):
    def role_checker(current_user: UserResponse = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted for role {current_user.role}",
            )
        return current_user

    return role_checker


@router.post("/google/login", response_model=Token)
async def google_login(
    payload: GoogleLoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """Authenticate via Google OAuth 2.0 (restricted to @iut-dhaka.edu) and issue a JWT."""
    google_info = await _verify_google_credentials(payload)
    raw_email = google_info.get("email")
    if not raw_email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google account email not available.",
        )

    email = validate_iut_email_domain(raw_email)
    full_name = google_info.get("name") or email.split("@")[0].replace(".", " ").title()

    user = await _get_or_create_user(db, email=email, full_name=full_name)
    token = create_access_token(
        subject=user.email,
        extra_claims={"role": user.role.value, "uid": str(user.id)},
    )
    return Token(access_token=token, token_type="bearer", user=user)


@router.get("/me", response_model=UserResponse)
async def read_current_user(current_user: UserResponse = Depends(get_current_user)):
    """Return the authenticated user's profile."""
    return current_user


@router.post("/dev-login", response_model=Token)
async def dev_login(
    email: str = "test.student@iut-dhaka.edu",
    role: UserRole = UserRole.CR,
    db: AsyncSession = Depends(get_db),
):
    """Developer login endpoint for local testing and demonstration."""
    normalized_email = validate_iut_email_domain(email)
    full_name = normalized_email.split("@")[0].replace(".", " ").title()

    user = await _get_or_create_user(
        db,
        email=normalized_email,
        full_name=full_name,
        default_role=role,
        department="CSE",
        batch="2023",
    )
    token = create_access_token(
        subject=user.email,
        extra_claims={"role": user.role.value, "uid": str(user.id)},
    )
    return Token(access_token=token, token_type="bearer", user=user)
