from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.security import create_access_token
from app.schemas.user import UserBase, UserRole, Token
from app.models.user import User
from app.db.database import get_db

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/token")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> UserBase:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    try:
        result = await db.execute(select(User).where(User.email == email))
        user_row = result.scalar_one_or_none()
        if user_row:
            return UserBase.model_validate(user_row)
    except Exception:
        pass

    # Development / fallback user
    return UserBase(
        email=email,
        full_name=email.split("@")[0].replace(".", " ").title(),
        role=UserRole.STUDENT,
        department="CSE"
    )


def require_role(allowed_roles: list[UserRole]):
    def role_checker(current_user: UserBase = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted for role {current_user.role}"
            )
        return current_user
    return role_checker


@router.post("/dev-login", response_model=Token)
async def dev_login(
    email: str = "test.student@iut-dhaka.edu",
    role: UserRole = UserRole.CR,
    db: AsyncSession = Depends(get_db)
):
    """Developer login endpoint for local testing and demonstration."""
    if not email.endswith(f"@{settings.ALLOWED_EMAIL_DOMAIN}"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Only @{settings.ALLOWED_EMAIL_DOMAIN} accounts are permitted."
        )

    user = UserBase(
        email=email,
        full_name=email.split("@")[0].replace(".", " ").title(),
        role=role,
        department="CSE",
        batch="2023"
    )
    token = create_access_token(subject=user.email)
    return Token(access_token=token, token_type="bearer", user=user)
