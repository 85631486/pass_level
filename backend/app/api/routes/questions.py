"""
题目管理 API
"""
import logging

from flask import Blueprint, jsonify, request, g

from ...core.exceptions import ValidationError, NotFoundError
from ...core.security import login_required
from ...db.session import get_db
from ...services.level_service import LevelService
from ...services.chapter_service import ChapterService
from ...services.question_service import QuestionService

questions_bp = Blueprint("questions", __name__, url_prefix="/api/v1")
logger = logging.getLogger(__name__)


def _check_level_permission(db, current_user, level_id: int):
    level = LevelService.get_level(db, level_id)
    if not level:
        return None, ("关卡不存在", 404)

    chapter = ChapterService.get_chapter(db, level.chapter_id)
    if current_user.role != "admin" and chapter.teacher_id != current_user.id:
        return None, ("无权操作此关卡", 403)

    return level, None


@questions_bp.route("/levels/<int:level_id>/questions", methods=["GET"])
@login_required
def get_questions(level_id: int):
    """获取关卡题目列表（用于关卡编辑页面）"""
    try:
        current_user = g.current_user
        db = get_db()

        level, err = _check_level_permission(db, current_user, level_id)
        if err:
            msg, code = err
            return jsonify({"detail": msg}), code

        questions = QuestionService.get_questions_by_level(db, level_id)
        data = [
            {
                "id": q.id,
                "level_id": q.level_id,
                "question_type": q.question_type,
                "title": q.title,
                "content": q.content,
                "options": q.options,
                "correct_answer": q.correct_answer,
                "answer_analysis": q.answer_analysis,
                "difficulty": q.difficulty,
                "score": q.score,
                "knowledge_point": q.knowledge_point,
                "tags": q.tags,
                "created_at": q.created_at.isoformat(),
                "updated_at": q.updated_at.isoformat(),
            }
            for q in questions
        ]
        return jsonify(data), 200
    except Exception as e:
        logger.error(f"Error getting questions: {e}", exc_info=True)
        return jsonify({"detail": str(e)}), 500


@questions_bp.route("/levels/<int:level_id>/questions", methods=["POST"])
@login_required
def create_question(level_id: int):
    """创建题目，并自动关联到关卡（可选关联到任务）"""
    if not request.is_json:
        return jsonify({"detail": "Content-Type must be application/json"}), 400

    data = request.get_json()
    if not data:
        return jsonify({"detail": "Request body is required"}), 400

    try:
        current_user = g.current_user
        db = get_db()

        level, err = _check_level_permission(db, current_user, level_id)
        if err:
            msg, code = err
            return jsonify({"detail": msg}), code

        question = QuestionService.create_question(
            db=db,
            level_id=level_id,
            question_type=data.get("question_type", ""),
            title=data.get("title", ""),
            content=data.get("content"),
            options=data.get("options"),
            correct_answer=data.get("correct_answer"),
            answer_analysis=data.get("answer_analysis"),
            difficulty=data.get("difficulty", "medium"),
            score=data.get("score", 10.0),
            knowledge_point=data.get("knowledge_point"),
            tags=data.get("tags"),
            task_id=data.get("task_id"),
            order=data.get("order", 0),
        )
        return (
            jsonify(
                {
                    "id": question.id,
                    "level_id": question.level_id,
                    "question_type": question.question_type,
                    "title": question.title,
                    "content": question.content,
                    "options": question.options,
                    "correct_answer": question.correct_answer,
                    "answer_analysis": question.answer_analysis,
                    "difficulty": question.difficulty,
                    "score": question.score,
                    "knowledge_point": question.knowledge_point,
                    "tags": question.tags,
                    "created_at": question.created_at.isoformat(),
                    "updated_at": question.updated_at.isoformat(),
                }
            ),
            201,
        )
    except ValidationError as e:
        return jsonify({"detail": e.message}), e.code
    except Exception as e:
        logger.error(f"Error creating question: {e}", exc_info=True)
        return jsonify({"detail": str(e)}), 500


@questions_bp.route("/questions/<int:question_id>", methods=["GET"])
@login_required
def get_question(question_id: int):
    """获取题目详情"""
    try:
        current_user = g.current_user
        db = get_db()

        question = QuestionService.get_question(db, question_id)
        if not question:
            return jsonify({"detail": "题目不存在"}), 404

        level, err = _check_level_permission(db, current_user, question.level_id)
        if err:
            msg, code = err
            return jsonify({"detail": msg}), code

        return (
            jsonify(
                {
                    "id": question.id,
                    "level_id": question.level_id,
                    "question_type": question.question_type,
                    "title": question.title,
                    "content": question.content,
                    "options": question.options,
                    "correct_answer": question.correct_answer,
                    "answer_analysis": question.answer_analysis,
                    "difficulty": question.difficulty,
                    "score": question.score,
                    "knowledge_point": question.knowledge_point,
                    "tags": question.tags,
                    "created_at": question.created_at.isoformat(),
                    "updated_at": question.updated_at.isoformat(),
                }
            ),
            200,
        )
    except Exception as e:
        logger.error(f"Error getting question: {e}", exc_info=True)
        return jsonify({"detail": str(e)}), 500


@questions_bp.route("/questions/<int:question_id>", methods=["PUT"])
@login_required
def update_question(question_id: int):
    """更新题目"""
    if not request.is_json:
        return jsonify({"detail": "Content-Type must be application/json"}), 400

    data = request.get_json()
    if not data:
        return jsonify({"detail": "Request body is required"}), 400

    try:
        current_user = g.current_user
        db = get_db()

        question = QuestionService.get_question(db, question_id)
        if not question:
            return jsonify({"detail": "题目不存在"}), 404

        level, err = _check_level_permission(db, current_user, question.level_id)
        if err:
            msg, code = err
            return jsonify({"detail": msg}), code

        question = QuestionService.update_question(
            db=db,
            question_id=question_id,
            question_type=data.get("question_type"),
            title=data.get("title"),
            content=data.get("content"),
            options=data.get("options"),
            correct_answer=data.get("correct_answer"),
            answer_analysis=data.get("answer_analysis"),
            difficulty=data.get("difficulty"),
            score=data.get("score"),
            knowledge_point=data.get("knowledge_point"),
            tags=data.get("tags"),
        )
        return (
            jsonify(
                {
                    "id": question.id,
                    "level_id": question.level_id,
                    "question_type": question.question_type,
                    "title": question.title,
                    "content": question.content,
                    "options": question.options,
                    "correct_answer": question.correct_answer,
                    "answer_analysis": question.answer_analysis,
                    "difficulty": question.difficulty,
                    "score": question.score,
                    "knowledge_point": question.knowledge_point,
                    "tags": question.tags,
                    "created_at": question.created_at.isoformat(),
                    "updated_at": question.updated_at.isoformat(),
                }
            ),
            200,
        )
    except NotFoundError as e:
        return jsonify({"detail": e.message}), e.code
    except ValidationError as e:
        return jsonify({"detail": e.message}), e.code
    except Exception as e:
        logger.error(f"Error updating question: {e}", exc_info=True)
        return jsonify({"detail": str(e)}), 500


@questions_bp.route("/questions/<int:question_id>", methods=["DELETE"])
@login_required
def delete_question(question_id: int):
    """删除题目"""
    try:
        current_user = g.current_user
        db = get_db()

        question = QuestionService.get_question(db, question_id)
        if not question:
            return jsonify({"detail": "题目不存在"}), 404

        level, err = _check_level_permission(db, current_user, question.level_id)
        if err:
            msg, code = err
            return jsonify({"detail": msg}), code

        QuestionService.delete_question(db, question_id)
        return jsonify({"detail": "题目删除成功"}), 200
    except NotFoundError as e:
        return jsonify({"detail": e.message}), e.code
    except Exception as e:
        logger.error(f"Error deleting question: {e}", exc_info=True)
        return jsonify({"detail": str(e)}), 500

















