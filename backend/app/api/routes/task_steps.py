"""
任务步骤管理 API
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
from ...services.task_step_service import TaskStepService

task_steps_bp = Blueprint("task_steps", __name__, url_prefix="/api/v1")
logger = logging.getLogger(__name__)


def _check_phase_permission(db, current_user, task_id: int, phase_id: int):
    """内部工具：检查当前用户对某个环节的权限"""
    task = TaskService.get_task(db, task_id)
    if not task:
        return None, None, ("任务不存在", 404)

    level = LevelService.get_level(db, task.level_id)
    chapter = ChapterService.get_chapter(db, level.chapter_id)
    if current_user.role != "admin" and chapter.teacher_id != current_user.id:
        return None, None, ("无权操作此任务", 403)

    phase = TaskPhaseService.get_phase(db, phase_id)
    if not phase or phase.task_id != task.id:
        return None, None, ("任务环节不存在", 404)

    return task, phase, None


@task_steps_bp.route("/tasks/<int:task_id>/phases/<int:phase_id>/steps", methods=["GET"])
@login_required
def get_steps(task_id: int, phase_id: int):
    """获取某环节下的步骤列表"""
    try:
        current_user = g.current_user
        db = get_db()

        task, phase, err = _check_phase_permission(db, current_user, task_id, phase_id)
        if err:
            msg, code = err
            return jsonify({"detail": msg}), code

        steps = TaskStepService.get_steps_by_phase(db, phase_id)
        data = [
            {
                "id": s.id,
                "phase_id": s.phase_id,
                "step_name": s.step_name,
                "content": s.content,
                "requirements": s.requirements,
                "submission_type": s.submission_type,
                "validation_rules": s.validation_rules,
                "order": s.order,
                "created_at": s.created_at.isoformat(),
                "updated_at": s.updated_at.isoformat(),
            }
            for s in steps
        ]
        return jsonify(data), 200
    except Exception as e:
        logger.error(f"Error getting steps: {e}", exc_info=True)
        return jsonify({"detail": str(e)}), 500


@task_steps_bp.route("/tasks/<int:task_id>/phases/<int:phase_id>/steps", methods=["POST"])
@login_required
def create_step(task_id: int, phase_id: int):
    """创建步骤"""
    if not request.is_json:
        return jsonify({"detail": "Content-Type must be application/json"}), 400

    data = request.get_json()
    if not data:
        return jsonify({"detail": "Request body is required"}), 400

    try:
        current_user = g.current_user
        db = get_db()

        task, phase, err = _check_phase_permission(db, current_user, task_id, phase_id)
        if err:
            msg, code = err
            return jsonify({"detail": msg}), code

        step = TaskStepService.create_step(
            db=db,
            phase_id=phase_id,
            step_name=data.get("step_name", ""),
            content=data.get("content"),
            requirements=data.get("requirements"),
            submission_type=data.get("submission_type", "text"),
            validation_rules=data.get("validation_rules"),
            order=data.get("order", 0),
        )
        return (
            jsonify(
                {
                    "id": step.id,
                    "phase_id": step.phase_id,
                    "step_name": step.step_name,
                    "content": step.content,
                    "requirements": step.requirements,
                    "submission_type": step.submission_type,
                    "validation_rules": step.validation_rules,
                    "order": step.order,
                    "created_at": step.created_at.isoformat(),
                    "updated_at": step.updated_at.isoformat(),
                }
            ),
            201,
        )
    except ValidationError as e:
        return jsonify({"detail": e.message}), e.code
    except Exception as e:
        logger.error(f"Error creating step: {e}", exc_info=True)
        return jsonify({"detail": str(e)}), 500


@task_steps_bp.route("/tasks/<int:task_id>/phases/<int:phase_id>/steps/<int:step_id>", methods=["PUT"])
@login_required
def update_step(task_id: int, phase_id: int, step_id: int):
    """更新步骤"""
    if not request.is_json:
        return jsonify({"detail": "Content-Type must be application/json"}), 400

    data = request.get_json()
    if not data:
        return jsonify({"detail": "Request body is required"}), 400

    try:
        current_user = g.current_user
        db = get_db()

        task, phase, err = _check_phase_permission(db, current_user, task_id, phase_id)
        if err:
            msg, code = err
            return jsonify({"detail": msg}), code

        step = TaskStepService.get_step(db, step_id)
        if not step or step.phase_id != phase.id:
            return jsonify({"detail": "步骤不存在"}), 404

        step = TaskStepService.update_step(
            db=db,
            step_id=step_id,
            step_name=data.get("step_name"),
            content=data.get("content"),
            requirements=data.get("requirements"),
            submission_type=data.get("submission_type"),
            validation_rules=data.get("validation_rules"),
            order=data.get("order"),
        )
        return (
            jsonify(
                {
                    "id": step.id,
                    "phase_id": step.phase_id,
                    "step_name": step.step_name,
                    "content": step.content,
                    "requirements": step.requirements,
                    "submission_type": step.submission_type,
                    "validation_rules": step.validation_rules,
                    "order": step.order,
                    "created_at": step.created_at.isoformat(),
                    "updated_at": step.updated_at.isoformat(),
                }
            ),
            200,
        )
    except NotFoundError as e:
        return jsonify({"detail": e.message}), e.code
    except ValidationError as e:
        return jsonify({"detail": e.message}), e.code
    except Exception as e:
        logger.error(f"Error updating step: {e}", exc_info=True)
        return jsonify({"detail": str(e)}), 500


@task_steps_bp.route("/tasks/<int:task_id>/phases/<int:phase_id>/steps/<int:step_id>", methods=["DELETE"])
@login_required
def delete_step(task_id: int, phase_id: int, step_id: int):
    """删除步骤"""
    try:
        current_user = g.current_user
        db = get_db()

        task, phase, err = _check_phase_permission(db, current_user, task_id, phase_id)
        if err:
            msg, code = err
            return jsonify({"detail": msg}), code

        step = TaskStepService.get_step(db, step_id)
        if not step or step.phase_id != phase.id:
            return jsonify({"detail": "步骤不存在"}), 404

        TaskStepService.delete_step(db, step_id)
        return jsonify({"detail": "步骤删除成功"}), 200
    except NotFoundError as e:
        return jsonify({"detail": e.message}), e.code
    except Exception as e:
        logger.error(f"Error deleting step: {e}", exc_info=True)
        return jsonify({"detail": str(e)}), 500

















