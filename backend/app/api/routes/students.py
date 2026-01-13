"""
学生相关API
"""
import logging
from flask import Blueprint, jsonify

from ...core.security import login_required
from flask import g
from ...db.session import get_db
from ...services.student_service import StudentService

students_bp = Blueprint("students", __name__, url_prefix="/api/v1/students")
logger = logging.getLogger(__name__)


@students_bp.route("/<int:user_id>/profile", methods=["GET"])
@login_required
def get_student_profile(user_id: int):
    """获取学生档案和技能树"""
    try:
        current_user = g.current_user
        db = get_db()
        
        # 学生只能查看自己的档案，教师和管理员可以查看所有
        if current_user.role == "student" and current_user.id != user_id:
            return jsonify({"detail": "无权访问此档案"}), 403
        
        profile_data = StudentService.get_profile(db, user_id)
        if not profile_data:
            return jsonify({"detail": "学生档案不存在"}), 404
        
        return jsonify(profile_data), 200
    except Exception as e:
        logger.error(f"Error getting student profile: {e}", exc_info=True)
        return jsonify({"detail": str(e)}), 500

