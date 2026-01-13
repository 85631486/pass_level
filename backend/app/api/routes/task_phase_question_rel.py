"""
环节与考题关联 API
"""
import logging

from flask import Blueprint, jsonify, request, g

from ...core.exceptions import ValidationError, NotFoundError
from ...core.security import login_required
from ...db.session import get_db
from ...services.level_service import LevelService
from ...services.chapter_service import ChapterService
from ...services.task_service import TaskService
from ...models.task_phase_question_rel import TaskPhaseQuestionRel

task_phase_question_rel_bp = Blueprint("task_phase_question_rel", __name__, url_prefix="/api/v1")
logger = logging.getLogger(__name__)


def _check_task_permission(db, current_user, task_id: int):
    task = TaskService.get_task(db, task_id)
    if not task:
        return None, ("任务不存在", 404)

    level = LevelService.get_level(db, task.level_id)
    chapter = ChapterService.get_chapter(db, level.chapter_id)
    if current_user.role != "admin" and chapter.teacher_id != current_user.id:
        return None, ("无权操作此任务", 403)

    return task, None


@task_phase_question_rel_bp.route("/tasks/<int:task_id>/phase-question-relation", methods=["GET"])
@login_required
def get_phase_question_relation(task_id: int):
    """获取任务下的环节-考题关联配置"""
    try:
        current_user = g.current_user
        db = get_db()

        task, err = _check_task_permission(db, current_user, task_id)
        if err:
            msg, code = err
            return jsonify({"detail": msg}), code

        rel = (
            db.query(TaskPhaseQuestionRel)
            .filter(TaskPhaseQuestionRel.task_id == task_id)
            .first()
        )
        if not rel:
            return jsonify({"task_id": task_id, "relation_config": None}), 200

        return (
            jsonify(
                {
                    "task_id": rel.task_id,
                    "relation_config": rel.relation_config,
                }
            ),
            200,
        )
    except Exception as e:
        logger.error(f"Error getting phase-question relation: {e}", exc_info=True)
        return jsonify({"detail": str(e)}), 500


@task_phase_question_rel_bp.route("/tasks/<int:task_id>/phase-question-relation", methods=["PUT"])
@login_required
def set_phase_question_relation(task_id: int):
    """设置任务下的环节-考题关联配置"""
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

        relation_config = data.get("relation_config")
        # relation_config 结构由前端按约定传入，例如：
        # {"type": "all_completed", "phases": [1, 2, 3]} 或 {"type": "threshold", "threshold": 0.8}

        rel = (
            db.query(TaskPhaseQuestionRel)
            .filter(TaskPhaseQuestionRel.task_id == task_id)
            .first()
        )
        if not rel:
            rel = TaskPhaseQuestionRel(task_id=task_id, relation_config=relation_config)
            db.add(rel)
        else:
            rel.relation_config = relation_config

        db.commit()
        return jsonify({"detail": "关联关系已保存"}), 200
    except ValidationError as e:
        return jsonify({"detail": e.message}), e.code
    except Exception as e:
        logger.error(f"Error setting phase-question relation: {e}", exc_info=True)
        return jsonify({"detail": str(e)}), 500

















