from typing import Optional
from sqlalchemy import or_
from sqlalchemy.orm import Session
from ..core.security import get_password_hash, verify_password
from ..models.user import User
from ..schemas.auth import UserCreate

class AuthError(Exception):
    """Custom exception for authentication errors."""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def _get_user_by_identifier(self, identifier: str) -> Optional[User]:
        """Get user by email, phone, or student_id."""
        return (
            self.db.query(User)
            .filter(
                or_(
                    User.email == identifier,
                    User.phone == identifier,
                    User.student_id == identifier
                )
            )
            .first()
        )

    def register_user(self, payload: UserCreate) -> User:
        """Register a new student user (students can only register as students)."""
        if not payload.email and not payload.phone and not payload.student_id:
            raise AuthError("Email, phone, or student_id is required", 400)
        if payload.email and self.db.query(User).filter(User.email == payload.email).first():
            raise AuthError("Email already registered", 400)
        if payload.phone and self.db.query(User).filter(User.phone == payload.phone).first():
            raise AuthError("Phone already registered", 400)
        if payload.student_id and self.db.query(User).filter(User.student_id == payload.student_id).first():
            raise AuthError("Student ID already registered", 400)

        user = User(
            email=payload.email,
            phone=payload.phone,
            student_id=payload.student_id,
            nickname=payload.nickname,
            hashed_password=get_password_hash(payload.password),
            role="student",  # Students can only register as students
        )
        self.db.add(user)
        self.db.flush()
        self.db.refresh(user)
        return user

    def create_teacher(self, payload) -> User:
        """Create a teacher account (admin only)."""
        if not payload.email and not payload.phone:
            raise AuthError("Email or phone is required", 400)
        if payload.email and self.db.query(User).filter(User.email == payload.email).first():
            raise AuthError("Email already registered", 400)
        if payload.phone and self.db.query(User).filter(User.phone == payload.phone).first():
            raise AuthError("Phone already registered", 400)

        user = User(
            email=payload.email,
            phone=payload.phone,
            nickname=payload.nickname,
            hashed_password=get_password_hash(payload.password),
            role="teacher",
        )
        self.db.add(user)
        self.db.flush()
        self.db.refresh(user)
        return user

    def authenticate(self, identifier: str, password: str) -> User:
        user = self._get_user_by_identifier(identifier)
        if not user or not verify_password(password, user.hashed_password):
            raise AuthError("Incorrect email/phone/student_id or password", 401)
        if not user.is_active:
            raise AuthError("User is inactive", 400)
        return user
