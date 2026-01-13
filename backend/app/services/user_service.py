"""User management service."""
from typing import List, Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..core.security import get_password_hash
from ..models.user import User


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_users(
        self,
        role: Optional[str] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[List[User], int]:
        """Get users with optional filtering."""
        query = self.db.query(User)

        # Filter by role
        if role:
            query = query.filter(User.role == role)

        # Search by email, phone, student_id, or nickname
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    User.email.like(search_pattern),
                    User.phone.like(search_pattern),
                    User.student_id.like(search_pattern),
                    User.nickname.like(search_pattern),
                )
            )

        # Get total count
        total = query.count()

        # Apply pagination
        users = query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()

        return users, total

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return self.db.query(User).filter(User.id == user_id).first()

    def create_user(
        self,
        email: Optional[str],
        phone: Optional[str],
        student_id: Optional[str],
        nickname: str,
        password: str,
        role: str = "student",
        class_name: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> User:
        """Create a new user."""
        if not email and not phone and not student_id:
            raise ValueError("Email, phone, or student_id is required")

        # Check for existing user
        if email and self.db.query(User).filter(User.email == email).first():
            raise ValueError("Email already registered")

        if phone and self.db.query(User).filter(User.phone == phone).first():
            raise ValueError("Phone already registered")

        if student_id and self.db.query(User).filter(User.student_id == student_id).first():
            raise ValueError("Student ID already registered")

        # Validate role
        if role not in ["student", "teacher", "admin"]:
            raise ValueError("Invalid role. Must be student, teacher, or admin")

        user = User(
            email=email,
            phone=phone,
            student_id=student_id,
            nickname=nickname,
            hashed_password=get_password_hash(password),
            role=role,
            is_active=True,
            class_name=class_name,
            notes=notes,
        )
        self.db.add(user)
        self.db.flush()
        self.db.refresh(user)
        return user

    def update_user(
        self,
        user_id: int,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        student_id: Optional[str] = None,
        nickname: Optional[str] = None,
        password: Optional[str] = None,
        role: Optional[str] = None,
        is_active: Optional[bool] = None,
        class_name: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> User:
        """Update user information."""
        user = self.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        if email is not None:
            # Check if email is already taken by another user
            existing = self.db.query(User).filter(User.email == email, User.id != user_id).first()
            if existing:
                raise ValueError("Email already registered")
            user.email = email

        if phone is not None:
            # Check if phone is already taken by another user
            existing = self.db.query(User).filter(User.phone == phone, User.id != user_id).first()
            if existing:
                raise ValueError("Phone already registered")
            user.phone = phone

        if student_id is not None:
            # Check if student_id is already taken by another user
            existing = self.db.query(User).filter(User.student_id == student_id, User.id != user_id).first()
            if existing:
                raise ValueError("Student ID already registered")
            user.student_id = student_id

        if nickname is not None:
            user.nickname = nickname

        if password is not None:
            user.hashed_password = get_password_hash(password)

        if role is not None:
            if role not in ["student", "teacher", "admin"]:
                raise ValueError("Invalid role. Must be student, teacher, or admin")
            user.role = role

        if is_active is not None:
            user.is_active = is_active

        self.db.flush()
        self.db.refresh(user)
        return user

    def delete_user(self, user_id: int) -> bool:
        """Delete a user (soft delete by setting is_active=False)."""
        user = self.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        # Soft delete
        user.is_active = False
        self.db.flush()
        return True

