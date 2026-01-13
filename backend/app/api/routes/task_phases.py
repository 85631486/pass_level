"""
任务环节管理 API
"""
import logging

from flask import Blueprint, jsonify, request, g

from ...core.exceptions import ValidationError, NotFoundError
from ...core.security import login_required
from ...db.session import get_db
from ...services.level_service import LevelService
from ...services.chapter_service import ChapterService
from ...services.task_service import TaskService
from ...services.task_phase_service import TaskPhaseService

task_phases_bp = Blueprint("task_phases", __name__, url_prefix="/api/v1")
logger = logging.getLogger(__name__)


def _check_task_permission(db, current_user, task_id: int):
    """内部工具：检查当前用户对任务的权限"""
    task = TaskService.get_task(db, task_id)
    if not task:
        return None, ("任务不存在", 404)

    level = LevelService.get_level(db, task.level_id)
    chapter = ChapterService.get_chapter(db, level.chapter_id)
    if current_user.role != "admin" and chapter.teacher_id != current_user.id:
        return None, ("无权操作此任务", 403)

    return task, None


@task_phases_bp.route("/tasks/<int:task_id>/phases", methods=["GET"])
@login_required
def get_phases(task_id: int):
    """获取任务下的环节列表"""
    try:
        current_user = g.current_user
        db = get_db()

        task, err = _check_task_permission(db, current_user, task_id)
        if err:
            msg, code = err
            return jsonify({"detail": msg}), code

        phases = TaskPhaseService.get_phases_by_task(db, task_id)
        data = [
            {
                "id": p.id,
                "task_id": p.task_id,
                "phase_name": p.phase_name,
                "order": p.order,
                "is_required": p.is_required,
                "created_at": p.created_at.isoformat(),
                "updated_at": p.updated_at.isoformat(),
            }
            for p in phases
        ]
        return jsonify(data), 200
    except Exception as e:
        logger.error(f"Error getting phases: {e}", exc_info=True)
        return jsonify({"detail": str(e)}), 500


@task_phases_bp.route("/tasks/<int:task_id>/phases", methods=["POST"])
@login_required
def create_phase(task_id: int):
    """创建任务环节"""
    if not request.is_json:
        return jsonify({"detail": "Content-Type must be application/json"}), 400

    data = request.get_json()
    if not data:
        return jsonify({"detail": "Request body is required"}), 400

    try:
        current_user = g.current_user
        db = get_db()

        task, err = _check_task_permission(db, current_user, task_id)
        if err:
            msg, code = err
            return jsonify({"detail": msg}), code

        phase = TaskPhaseService.create_phase(
            db=db,
            task_id=task_id,
            phase_name=data.get("phase_name", ""),
            order=data.get("order", 0),
            is_required=data.get("is_required", True),
        )
        return (
            jsonify(
                {
                    "id": phase.id,
                    "task_id": phase.task_id,
                    "phase_name": phase.phase_name,
                    "order": phase.order,
                    "is_required": phase.is_required,
                    "created_at": phase.created_at.isoformat(),
                    "updated_at": phase.updated_at.isoformat(),
                }
            ),
            201,
        )
    except ValidationError as e:
        return jsonify({"detail": e.message}), e.code
    except Exception as e:
        logger.error(f"Error creating phase: {e}", exc_info=True)
        return jsonify({"detail": str(e)}), 500


@task_phases_bp.route("/tasks/<int:task_id>/phases/<int:phase_id>", methods=["PUT"])
@login_required
def update_phase(task_id: int, phase_id: int):
    """更新任务环节"""
    if not request.is_json:
        return jsonify({"detail": "Content-Type must be application/json"}), 400

    data = request.get_json()
    if not data:
        return jsonify({"detail": "Request body is required"}), 400

    try:
        current_user = g.current_user
        db = get_db()

        task, err = _check_task_permission(db, current_user, task_id)
        if err:
            msg, code = err
            return jsonify({"detail": msg}), code

        phase = TaskPhaseService.get_phase(db, phase_id)
        if not phase or phase.task_id != task.id:
            return jsonify({"detail": "任务环节不存在"}), 404

        phase = TaskPhaseService.update_phase(
            db=db,
            phase_id=phase_id,
            phase_name=data.get("phase_name"),
            order=data.get("order"),
            is_required=data.get("is_required"),
        )
        return (
            jsonify(
                {
                    "id": phase.id,
                    "task_id": phase.task_id,
                    "phase_name": phase.phase_name,
                    "order": phase.order,
                    "is_required": phase.is_required,
                    "created_at": phase.created_at.isoformat(),
                    "updated_at": phase.updated_at.isoformat(),
                }
            ),
            200,
        )
    except NotFoundError as e:
        return jsonify({"detail": e.message}), e.code
    except ValidationError as e:
        return jsonify({"detail": e.message}), e.code
    except Exception as e:
        logger.error(f"Error updating phase: {e}", exc_info=True)
        return jsonify({"detail": str(e)}), 500


@task_phases_bp.route("/tasks/<int:task_id>/phases/<int:phase_id>", methods=["DELETE"])
@login_required
def delete_phase(task_id: int, phase_id: int):
    """删除任务环节"""
    try:
        current_user = g.current_user
        db = get_db()

        task, err = _check_task_permission(db, current_user, task_id)
        if err:
            msg, code = err
            return jsonify({"detail": msg}), code

        phase = TaskPhaseService.get_phase(db, phase_id)
        if not phase or phase.task_id != task.id:
            return jsonify({"detail": "任务环节不存在"}), 404

        TaskPhaseService.delete_phase(db, phase_id)
        return jsonify({"detail": "任务环节删除成功"}), 200
    except NotFoundError as e:
        return jsonify({"detail": e.message}), e.code
    except Exception as e:
        logger.error(f"Error deleting phase: {e}", exc_info=True)
        return jsonify({"detail": str(e)}), 500

















