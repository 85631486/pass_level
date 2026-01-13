from datetime import datetime, timedelta
from functools import wraps
from typing import Optional

from flask import g, request
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from ..core.config import get_settings
from ..db.session import get_db
from ..models.user import User


# Use Argon2 instead of bcrypt to avoid 72-byte limit and improve security
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
settings = get_settings()


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    to_encode = {"sub": subject, "exp": expire}
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password using Argon2."""
    return pwd_context.hash(password)


def get_token_from_header() -> Optional[str]:
    """Extract Bearer token from Authorization header."""
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header[7:]
    return None


def get_current_user() -> User:
    """Get current authenticated user from token."""
    from flask import abort

    token = get_token_from_header()
    if not token:
        abort(401, description="Could not validate credentials")

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id: str | None = payload.get("sub")
        if user_id is None:
            abort(401, description="Could not validate credentials")
    except JWTError:
        abort(401, description="Could not validate credentials")

    db: Session = get_db()
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user or not user.is_active:
        abort(401, description="Could not validate credentials")
    return user


def login_required(f):
    """Decorator to require authentication for a route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        g.current_user = get_current_user()
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator to require admin role for a route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import abort
        g.current_user = get_current_user()
        if g.current_user.role != "admin":
            abort(403, description="Admin access required")
        return f(*args, **kwargs)
    return decorated_function

