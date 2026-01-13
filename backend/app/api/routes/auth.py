import logging
from datetime import timedelta

from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from ...core.config import get_settings
from ...core.security import create_access_token, login_required
from ...db.session import get_db
from ...schemas.auth import TeacherCreate, Token, UserCreate, UserLogin, UserRead
from ...services.auth import AuthService

auth_bp = Blueprint("auth", __name__, url_prefix="/api/v1/auth")
settings = get_settings()
logger = logging.getLogger(__name__)


@auth_bp.route("/register", methods=["POST"])
def register_user():
    """Register a new user."""
    logger.info(f"Register request received: {request.method} {request.path}")
    
    if not request.is_json:
        logger.warning("Request is not JSON")
        return jsonify({"detail": "Content-Type must be application/json"}), 400
    
    data = request.get_json()
    if not data:
        logger.warning("Request body is empty")
        return jsonify({"detail": "Request body is required"}), 400
    
    logger.info(f"Register data: {dict((k, v if k != 'password' else '***') for k, v in data.items())}")
    
    try:
        payload = UserCreate(**data)
    except ValidationError as e:
        logger.warning(f"Validation error: {e.errors()}")
        return jsonify({"detail": e.errors()}), 400
    except Exception as e:
        logger.error(f"Invalid request data: {e}", exc_info=True)
        return jsonify({"detail": f"Invalid request data: {str(e)}"}), 400

    db = get_db()
    service = AuthService(db)
    try:
        user = service.register_user(payload)
        db.commit()
        logger.info(f"User registered successfully: {user.id}")
        return jsonify(UserRead.model_validate(user).model_dump()), 201
    except Exception as e:
        db.rollback()
        status_code = getattr(e, "status_code", 400)
        error_msg = getattr(e, "message", str(e))
        logger.error(f"Registration failed: {error_msg}", exc_info=True)
        return jsonify({"detail": error_msg}), status_code


@auth_bp.route("/login", methods=["POST"])
def login():
    """Login and get access token."""
    if not request.is_json:
        return jsonify({"detail": "Content-Type must be application/json"}), 400
    
    data = request.get_json()
    if not data:
        return jsonify({"detail": "Request body is required"}), 400
    
    try:
        payload = UserLogin(**data)
    except ValidationError as e:
        return jsonify({"detail": e.errors()}), 400
    except Exception as e:
        return jsonify({"detail": f"Invalid request data: {str(e)}"}), 400

    db = get_db()
    service = AuthService(db)
    try:
        user = service.authenticate(payload.identifier, payload.password)
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        token = create_access_token(subject=str(user.id), expires_delta=access_token_expires)
        # Return token with user role information
        response_data = Token(access_token=token).model_dump()
        response_data["user"] = UserRead.model_validate(user).model_dump()
        return jsonify(response_data)
    except Exception as e:
        status_code = getattr(e, "status_code", 401)
        error_msg = getattr(e, "message", str(e))
        return jsonify({"detail": error_msg}), status_code


@auth_bp.route("/me", methods=["GET"])
@login_required
def read_current_user():
    """Get current user information."""
    from flask import g
    return jsonify(UserRead.model_validate(g.current_user).model_dump())


@auth_bp.route("/admin/create-teacher", methods=["POST"])
@login_required
def create_teacher():
    """Create a teacher account (admin only)."""
    from flask import g
    
    # Check if user is admin
    if g.current_user.role != "admin":
        return jsonify({"detail": "Only admin can create teacher accounts"}), 403
    
    if not request.is_json:
        return jsonify({"detail": "Content-Type must be application/json"}), 400
    
    data = request.get_json()
    if not data:
        return jsonify({"detail": "Request body is required"}), 400
    
    try:
        payload = TeacherCreate(**data)
    except ValidationError as e:
        return jsonify({"detail": e.errors()}), 400
    except Exception as e:
        return jsonify({"detail": f"Invalid request data: {str(e)}"}), 400

    db = get_db()
    service = AuthService(db)
    try:
        teacher = service.create_teacher(payload)
        db.commit()
        logger.info(f"Teacher created successfully: {teacher.id}")
        return jsonify(UserRead.model_validate(teacher).model_dump()), 201
    except Exception as e:
        db.rollback()
        status_code = getattr(e, "status_code", 400)
        error_msg = getattr(e, "message", str(e))
        logger.error(f"Teacher creation failed: {error_msg}", exc_info=True)
        return jsonify({"detail": error_msg}), status_code

