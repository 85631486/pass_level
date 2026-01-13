"""User management schemas."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator


class UserCreateAdmin(BaseModel):
    """Schema for admin creating a user."""
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    student_id: Optional[str] = None
    nickname: str
    password: str
    role: str = "student"  # student, teacher, admin
    class_name: Optional[str] = None  # 班级
    notes: Optional[str] = None  # 备注

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

    @field_validator("role")
    @classmethod
    def validate_role(cls, value: str) -> str:
        if value not in ["student", "teacher", "admin"]:
            raise ValueError("Role must be student, teacher, or admin")
        return value


class UserUpdateAdmin(BaseModel):
    """Schema for admin updating a user."""
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    student_id: Optional[str] = None
    nickname: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    class_name: Optional[str] = None  # 班级
    notes: Optional[str] = None  # 备注

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

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        if len(value) < 6:
            raise ValueError("Password must be at least 6 characters")
        return value

    @field_validator("role")
    @classmethod
    def validate_role(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and value not in ["student", "teacher", "admin"]:
            raise ValueError("Role must be student, teacher, or admin")
        return value


class UserListResponse(BaseModel):
    """Response schema for user list."""
    id: int
    email: Optional[str]
    phone: Optional[str]
    student_id: Optional[str]
    nickname: str
    role: str
    is_active: bool
    class_name: Optional[str] = None  # 班级
    notes: Optional[str] = None  # 备注
    created_at: datetime

    class Config:
        from_attributes = True


class UserListPaginated(BaseModel):
    """Paginated user list response."""
    items: list[UserListResponse]
    total: int
    skip: int
    limit: int

