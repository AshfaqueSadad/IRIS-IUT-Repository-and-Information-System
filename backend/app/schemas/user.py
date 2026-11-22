from enum import Enum
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, ConfigDict


class UserRole(str, Enum):
    STUDENT = "STUDENT"
    CR = "CR"
    FACULTY = "FACULTY"
    OFFICIAL = "OFFICIAL"
    ADMIN = "ADMIN"


class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email: EmailStr
    full_name: str
    role: UserRole = UserRole.STUDENT
    department: Optional[str] = None
    batch: Optional[str] = None
    is_active: bool = True


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: UUID


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserBase
