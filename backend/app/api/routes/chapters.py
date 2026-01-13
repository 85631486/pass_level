"""
篇章管理API
"""
import logging
from flask import Blueprint, jsonify, request, g

from ...core.exceptions import NotFoundError, ValidationError
from ...core.security import login_required, get_current_user
from ...db.session import get_db
from ...schemas.chapter import ChapterCreate, ChapterUpdate, ChapterRead
from ...services.chapter_service import ChapterService

chapters_bp = Blueprint("chapters", __name__, url_prefix="/api/v1/chapters")
logger = logging.getLogger(__name__)


@chapters_bp.route("", methods=["GET"])
@login_required
def get_chapters():
    """获取篇章列表"""
    try:
        current_user = g.current_user
        db = get_db()
        
        # 教师只能看到自己的篇章，管理员可以看到所有
        teacher_id = None if current_user.role == "admin" else current_user.id
        
        chapters = ChapterService.get_chapters(db, teacher_id=teacher_id)
        return jsonify([ChapterRead.model_validate(chapter).model_dump() for chapter in chapters]), 200
    except Exception as e:
        logger.error(f"Error getting chapters: {e}", exc_info=True)
        return jsonify({"detail": str(e)}), 500


@chapters_bp.route("", methods=["POST"])
@login_required
def create_chapter():
    """创建篇章"""
    if not request.is_json:
        return jsonify({"detail": "Content-Type must be application/json"}), 400
    
    data = request.get_json()
    if not data:
        return jsonify({"detail": "Request body is required"}), 400
    
    try:
        payload = ChapterCreate(**data)
    except Exception as e:
        return jsonify({"detail": f"Invalid request data: {str(e)}"}), 400
    
    try:
        current_user = g.current_user
        # 只有教师和管理员可以创建篇章
        if current_user.role not in ["teacher", "admin"]:
            return jsonify({"detail": "只有教师和管理员可以创建篇章"}), 403
        
        db = get_db()
        chapter = ChapterService.create_chapter(
            db=db,
            name=payload.name,
            description=payload.description,
            teacher_id=current_user.id
        )
        db.commit()
        logger.info(f"Chapter created: {chapter.id} by user {current_user.id}")
        return jsonify(ChapterRead.model_validate(chapter).model_dump()), 201
    except ValidationError as e:
        return jsonify({"detail": e.message}), e.code
    except Exception as e:
        logger.error(f"Error creating chapter: {e}", exc_info=True)
        return jsonify({"detail": str(e)}), 500


@chapters_bp.route("/<int:chapter_id>", methods=["GET"])
@login_required
def get_chapter(chapter_id: int):
    """获取篇章详情"""
    try:
        current_user = g.current_user
        db = get_db()
        
        chapter = ChapterService.get_chapter(db, chapter_id)
        if not chapter:
            return jsonify({"detail": "篇章不存在"}), 404
        
        # 检查权限：教师只能查看自己的篇章，管理员可以查看所有
        if current_user.role != "admin" and chapter.teacher_id != current_user.id:
            return jsonify({"detail": "无权访问此篇章"}), 403
        
        return jsonify(ChapterRead.model_validate(chapter).model_dump()), 200
    except Exception as e:
        logger.error(f"Error getting chapter: {e}", exc_info=True)
        return jsonify({"detail": str(e)}), 500


@chapters_bp.route("/<int:chapter_id>", methods=["PUT"])
@login_required
def update_chapter(chapter_id: int):
    """更新篇章"""
    if not request.is_json:
        return jsonify({"detail": "Content-Type must be application/json"}), 400
    
    data = request.get_json()
    if not data:
        return jsonify({"detail": "Request body is required"}), 400
    
    try:
        payload = ChapterUpdate(**data)
    except Exception as e:
        return jsonify({"detail": f"Invalid request data: {str(e)}"}), 400
    
    try:
        current_user = g.current_user
        db = get_db()
        
        chapter = ChapterService.get_chapter(db, chapter_id)
        if not chapter:
            return jsonify({"detail": "篇章不存在"}), 404
        
        # 检查权限
        if current_user.role != "admin" and chapter.teacher_id != current_user.id:
            return jsonify({"detail": "无权修改此篇章"}), 403
        
        chapter = ChapterService.update_chapter(
            db=db,
            chapter_id=chapter_id,
            name=payload.name,
            description=payload.description
        )
        db.commit()
        logger.info(f"Chapter updated: {chapter_id} by user {current_user.id}")
        return jsonify(ChapterRead.model_validate(chapter).model_dump()), 200
    except NotFoundError as e:
        return jsonify({"detail": e.message}), e.code
    except ValidationError as e:
        return jsonify({"detail": e.message}), e.code
    except Exception as e:
        logger.error(f"Error updating chapter: {e}", exc_info=True)
        return jsonify({"detail": str(e)}), 500


@chapters_bp.route("/<int:chapter_id>", methods=["DELETE"])
@login_required
def delete_chapter(chapter_id: int):
    """删除篇章"""
    try:
        current_user = g.current_user
        db = get_db()
        
        chapter = ChapterService.get_chapter(db, chapter_id)
        if not chapter:
            return jsonify({"detail": "篇章不存在"}), 404
        
        # 检查权限
        if current_user.role != "admin" and chapter.teacher_id != current_user.id:
            return jsonify({"detail": "无权删除此篇章"}), 403
        
        ChapterService.delete_chapter(db, chapter_id)
        db.commit()
        logger.info(f"Chapter deleted: {chapter_id} by user {current_user.id}")
        return jsonify({"detail": "篇章删除成功"}), 200
    except NotFoundError as e:
        return jsonify({"detail": e.message}), e.code
    except Exception as e:
        logger.error(f"Error deleting chapter: {e}", exc_info=True)
        return jsonify({"detail": str(e)}), 500

