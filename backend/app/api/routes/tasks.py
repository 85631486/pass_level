"""
任务管理 API
"""
import logging

from flask import Blueprint, jsonify, request, g

from ...core.exceptions import ValidationError, NotFoundError
from ...core.security import login_required
from ...db.session import get_db
from ...services.level_service import LevelService
from ...services.chapter_service import ChapterService
from ...services.task_service import TaskService

tasks_bp = Blueprint("tasks", __name__, url_prefix="/api/v1")
logger = logging.getLogger(__name__)


@tasks_bp.route("/levels/<int:level_id>/tasks", methods=["GET"])
@login_required
def get_tasks(level_id: int):
    """获取关卡下的任务列表"""
    try:
        current_user = g.current_user
        db = get_db()

        level = LevelService.get_level(db, level_id)
        if not level:
            return jsonify({"detail": "关卡不存在"}), 404

        chapter = ChapterService.get_chapter(db, level.chapter_id)
        if current_user.role != "admin" and chapter.teacher_id != current_user.id:
            return jsonify({"detail": "无权访问此关卡"}), 403

        tasks = TaskService.get_tasks_by_level(db, level_id)
        data = [
            {
                "id": t.id,
                "level_id": t.level_id,
                "name": t.name,
                "description": t.description,
                "objective": t.objective,
                "created_at": t.created_at.isoformat(),
                "updated_at": t.updated_at.isoformat(),
            }
            for t in tasks
        ]
        return jsonify(data), 200
    except Exception as e:
        logger.error(f"Error getting tasks: {e}", exc_info=True)
        return jsonify({"detail": str(e)}), 500


@tasks_bp.route("/levels/<int:level_id>/tasks", methods=["POST"])
@login_required
def create_task(level_id: int):
    """创建任务"""
    if not request.is_json:
        return jsonify({"detail": "Content-Type must be application/json"}), 400

    data = request.get_json()
    if not data:
        return jsonify({"detail": "Request body is required"}), 400

    try:
        current_user = g.current_user
        db = get_db()

        level = LevelService.get_level(db, level_id)
        if not level:
            return jsonify({"detail": "关卡不存在"}), 404

        chapter = ChapterService.get_chapter(db, level.chapter_id)
        if current_user.role != "admin" and chapter.teacher_id != current_user.id:
            return jsonify({"detail": "无权操作此关卡"}), 403

        task = TaskService.create_task(
            db=db,
            level_id=level_id,
            name=data.get("name", ""),
            description=data.get("description"),
            objective=data.get("objective"),
        )
        return (
            jsonify(
                {
                    "id": task.id,
                    "level_id": task.level_id,
                    "name": task.name,
                    "description": task.description,
                    "objective": task.objective,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat(),
                }
            ),
            201,
        )
    except ValidationError as e:
        return jsonify({"detail": e.message}), e.code
    except Exception as e:
        logger.error(f"Error creating task: {e}", exc_info=True)
        return jsonify({"detail": str(e)}), 500


@tasks_bp.route("/tasks/<int:task_id>", methods=["GET"])
@login_required
def get_task(task_id: int):
    """获取任务详情"""
    try:
        current_user = g.current_user
        db = get_db()

        task = TaskService.get_task(db, task_id)
        if not task:
            return jsonify({"detail": "任务不存在"}), 404

        level = LevelService.get_level(db, task.level_id)
        chapter = ChapterService.get_chapter(db, level.chapter_id)
        if current_user.role != "admin" and chapter.teacher_id != current_user.id:
            return jsonify({"detail": "无权访问此任务"}), 403

        return (
            jsonify(
                {
                    "id": task.id,
                    "level_id": task.level_id,
                    "name": task.name,
                    "description": task.description,
                    "objective": task.objective,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat(),
                }
            ),
            200,
        )
    except Exception as e:
        logger.error(f"Error getting task: {e}", exc_info=True)
        return jsonify({"detail": str(e)}), 500


@tasks_bp.route("/tasks/<int:task_id>", methods=["PUT"])
@login_required
def update_task(task_id: int):
    """更新任务"""
    if not request.is_json:
        return jsonify({"detail": "Content-Type must be application/json"}), 400

    data = request.get_json()
    if not data:
        return jsonify({"detail": "Request body is required"}), 400

    try:
        current_user = g.current_user
        db = get_db()

        task = TaskService.get_task(db, task_id)
        if not task:
            return jsonify({"detail": "任务不存在"}), 404

        level = LevelService.get_level(db, task.level_id)
        chapter = ChapterService.get_chapter(db, level.chapter_id)
        if current_user.role != "admin" and chapter.teacher_id != current_user.id:
            return jsonify({"detail": "无权修改此任务"}), 403

        task = TaskService.update_task(
            db=db,
            task_id=task_id,
            name=data.get("name"),
            description=data.get("description"),
            objective=data.get("objective"),
        )
        return (
            jsonify(
                {
                    "id": task.id,
                    "level_id": task.level_id,
                    "name": task.name,
                    "description": task.description,
                    "objective": task.objective,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat(),
                }
            ),
            200,
        )
    except NotFoundError as e:
        return jsonify({"detail": e.message}), e.code
    except ValidationError as e:
        return jsonify({"detail": e.message}), e.code
    except Exception as e:
        logger.error(f"Error updating task: {e}", exc_info=True)
        return jsonify({"detail": str(e)}), 500


@tasks_bp.route("/tasks/<int:task_id>", methods=["DELETE"])
@login_required
def delete_task(task_id: int):
    """删除任务"""
    try:
        current_user = g.current_user
        db = get_db()

        task = TaskService.get_task(db, task_id)
        if not task:
            return jsonify({"detail": "任务不存在"}), 404

        level = LevelService.get_level(db, task.level_id)
        chapter = ChapterService.get_chapter(db, level.chapter_id)
        if current_user.role != "admin" and chapter.teacher_id != current_user.id:
            return jsonify({"detail": "无权删除此任务"}), 403

        TaskService.delete_task(db, task_id)
        return jsonify({"detail": "任务删除成功"}), 200
    except NotFoundError as e:
        return jsonify({"detail": e.message}), e.code
    except Exception as e:
        logger.error(f"Error deleting task: {e}", exc_info=True)
        return jsonify({"detail": str(e)}), 500

















