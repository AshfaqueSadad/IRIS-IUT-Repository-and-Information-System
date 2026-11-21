from enum import Enum
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserRole(str, Enum):
    STUDENT = "STUDENT"
    CR = "CR"
    FACULTY = "FACULTY"
    OFFICIAL = "OFFICIAL"
    ADMIN = "ADMIN"


class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole = UserRole.STUDENT
    department: Optional[str] = None
    batch: Optional[str] = None
    is_active: bool = True


class UserCreate(UserBase):
    pass


class UserInDB(UserBase):
    id: str = Field(..., alias="_id")


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserBase
