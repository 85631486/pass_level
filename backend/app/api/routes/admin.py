"""Admin API routes."""
import logging

from flask import Blueprint, jsonify, request

from ...core.security import admin_required, login_required
from ...db.session import get_db
from ...schemas.auth import UserRead
from ...schemas.user import UserCreateAdmin, UserListPaginated, UserListResponse, UserUpdateAdmin
from ...services.user_service import UserService

admin_bp = Blueprint("admin", __name__, url_prefix="/api/v1/admin")
logger = logging.getLogger(__name__)


@admin_bp.route("/users", methods=["GET"])
@admin_required
def list_users():
    """Get list of users with optional filtering."""
    # GET requests use query parameters
    role = request.args.get("role") or None
    search = request.args.get("search") or None
    try:
        skip = int(request.args.get("skip", 0))
        limit = int(request.args.get("limit", 100))
    except (ValueError, TypeError):
        skip = 0
        limit = 100

    db = get_db()
    service = UserService(db)
    try:
        users, total = service.get_users(role=role, search=search, skip=skip, limit=limit)
        items = [UserListResponse.model_validate(user).model_dump() for user in users]
        return jsonify(
            UserListPaginated(items=items, total=total, skip=skip, limit=limit).model_dump()
        )
    except Exception as e:
        logger.error(f"Error listing users: {e}", exc_info=True)
        return jsonify({"detail": str(e)}), 500


@admin_bp.route("/users", methods=["POST"])
@admin_required
def create_user():
    """Create a new user (admin only)."""
    if not request.is_json:
        return jsonify({"detail": "Content-Type must be application/json"}), 400

    data = request.get_json()
    if not data:
        return jsonify({"detail": "Request body is required"}), 400

    try:
        payload = UserCreateAdmin(**data)
    except Exception as e:
        return jsonify({"detail": str(e)}), 400

    db = get_db()
    service = UserService(db)
    try:
        user = service.create_user(
            email=payload.email,
            phone=payload.phone,
            student_id=payload.student_id,
            nickname=payload.nickname,
            password=payload.password,
            role=payload.role,
            class_name=payload.class_name,
            notes=payload.notes,
        )
        db.commit()
        logger.info(f"User created by admin: {user.id} ({user.role})")
        return jsonify(UserRead.model_validate(user).model_dump()), 201
    except ValueError as e:
        db.rollback()
        return jsonify({"detail": str(e)}), 400
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating user: {e}", exc_info=True)
        return jsonify({"detail": str(e)}), 500


@admin_bp.route("/users/<int:user_id>", methods=["GET"])
@admin_required
def get_user(user_id: int):
    """Get user details."""
    db = get_db()
    service = UserService(db)
    try:
        user = service.get_user_by_id(user_id)
        if not user:
            return jsonify({"detail": "User not found"}), 404
        return jsonify(UserRead.model_validate(user).model_dump())
    except Exception as e:
        logger.error(f"Error getting user: {e}", exc_info=True)
        return jsonify({"detail": str(e)}), 500


@admin_bp.route("/users/<int:user_id>", methods=["PUT"])
@admin_required
def update_user(user_id: int):
    """Update user information."""
    if not request.is_json:
        return jsonify({"detail": "Content-Type must be application/json"}), 400

    data = request.get_json()
    if not data:
        return jsonify({"detail": "Request body is required"}), 400

    try:
        payload = UserUpdateAdmin(**data)
    except Exception as e:
        return jsonify({"detail": str(e)}), 400

    db = get_db()
    service = UserService(db)
    try:
        user = service.update_user(
            user_id=user_id,
            email=payload.email,
            phone=payload.phone,
            student_id=payload.student_id,
            nickname=payload.nickname,
            password=payload.password,
            role=payload.role,
            is_active=payload.is_active,
            class_name=payload.class_name,
            notes=payload.notes,
        )
        db.commit()
        logger.info(f"User updated by admin: {user_id}")
        return jsonify(UserRead.model_validate(user).model_dump())
    except ValueError as e:
        db.rollback()
        return jsonify({"detail": str(e)}), 400
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating user: {e}", exc_info=True)
        return jsonify({"detail": str(e)}), 500


@admin_bp.route("/users/<int:user_id>", methods=["DELETE"])
@admin_required
def delete_user(user_id: int):
    """Delete a user (soft delete)."""
    db = get_db()
    service = UserService(db)
    try:
        service.delete_user(user_id)
        db.commit()
        logger.info(f"User deleted by admin: {user_id}")
        return jsonify({"detail": "User deleted successfully"}), 200
    except ValueError as e:
        db.rollback()
        return jsonify({"detail": str(e)}), 404
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting user: {e}", exc_info=True)
        return jsonify({"detail": str(e)}), 500

