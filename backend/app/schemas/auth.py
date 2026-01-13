from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator


class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    student_id: Optional[str] = None
    nickname: str

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        digits = "".join(filter(str.isdigit, value))
        if len(digits) < 6:
            raise ValueError("Phone must contain at least 6 digits")
        return value

    @field_validator("student_id")
    @classmethod
    def validate_student_id(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        if len(value.strip()) < 3:
            raise ValueError("Student ID must be at least 3 characters")
        return value.strip()


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    identifier: str
    password: str


class UserRead(UserBase):
    id: int
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TeacherCreate(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    nickname: str
    password: str

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        digits = "".join(filter(str.isdigit, value))
        if len(digits) < 6:
            raise ValueError("Phone must contain at least 6 digits")
        return value


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

