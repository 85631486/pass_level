"""
关卡管理API
"""
import logging
from flask import Blueprint, jsonify, request

from ...core.exceptions import NotFoundError, ValidationError
from ...core.security import login_required
from flask import g
from ...db.session import get_db
from ...schemas.level import LevelCreate, LevelUpdate, LevelRead, CourseDataUpdate, CourseDataResponse
from ...services.level_service import LevelService
from ...services.chapter_service import ChapterService
from ...services.treasure_chest_service import TreasureChestService
from ...services.ai_service import AIService
from ...schemas.treasure_chest import TreasureChestCreate, TreasureChestUpdate, TreasureChestRead
import json
from datetime import datetime

levels_bp = Blueprint("levels", __name__, url_prefix="/api/v1")
logger = logging.getLogger(__name__)


@levels_bp.route("/chapters/<int:chapter_id>/levels", methods=["GET"])
@login_required
def get_levels(chapter_id: int):
    """获取篇章下的关卡列表"""
    try:
        current_user = g.current_user
        db = get_db()
        
        # 检查篇章权限
        chapter = ChapterService.get_chapter(db, chapter_id)
        if not chapter:
            return jsonify({"detail": "篇章不存在"}), 404
        
        if current_user.role != "admin" and chapter.teacher_id != current_user.id:
            return jsonify({"detail": "无权访问此篇章"}), 403
        
        levels = LevelService.get_levels_by_chapter(db, chapter_id)
        return jsonify([LevelRead.model_validate(level).model_dump() for level in levels]), 200
    except Exception as e:
        logger.error(f"Error getting levels: {e}", exc_info=True)
        return jsonify({"detail": str(e)}), 500


@levels_bp.route("/chapters/<int:chapter_id>/levels", methods=["POST"])
@login_required
def create_level(chapter_id: int):
    """创建关卡（在地图编辑器中）"""
    if not request.is_json:
        return jsonify({"detail": "Content-Type must be application/json"}), 400
    
    data = request.get_json()
    if not data:
        return jsonify({"detail": "Request body is required"}), 400
    
    try:
        payload = LevelCreate(**data)
    except Exception as e:
        return jsonify({"detail": f"Invalid request data: {str(e)}"}), 400
    
    try:
        current_user = g.current_user
        db = get_db()
        
        # 检查篇章权限
        chapter = ChapterService.get_chapter(db, chapter_id)
        if not chapter:
            return jsonify({"detail": "篇章不存在"}), 404
        
        if current_user.role != "admin" and chapter.teacher_id != current_user.id:
            return jsonify({"detail": "无权在此篇章创建关卡"}), 403
        
        # 确保chapter_id一致
        if payload.chapter_id != chapter_id:
            return jsonify({"detail": "篇章ID不匹配"}), 400
        
        level = LevelService.create_level(
            db=db,
            chapter_id=chapter_id,
            name=payload.name,
            description=payload.description,
            order=payload.order,
            allow_skip=payload.allow_skip,
        )
        db.commit()
        logger.info(f"Level created: {level.id} in chapter {chapter_id} by user {current_user.id}")
        return jsonify(LevelRead.model_validate(level).model_dump()), 201
    except ValidationError as e:
        return jsonify({"detail": e.message}), e.code
    except Exception as e:
        logger.error(f"Error creating level: {e}", exc_info=True)
        return jsonify({"detail": str(e)}), 500


@levels_bp.route("/levels/<int:level_id>", methods=["GET"])
@login_required
def get_level(level_id: int):
    """获取关卡详情"""
    try:
        current_user = g.current_user
        db = get_db()
        
        level = LevelService.get_level(db, level_id)
        if not level:
            return jsonify({"detail": "关卡不存在"}), 404
        
        # 检查篇章权限
        chapter = ChapterService.get_chapter(db, level.chapter_id)
        if current_user.role != "admin" and chapter.teacher_id != current_user.id:
            return jsonify({"detail": "无权访问此关卡"}), 403
        
        return jsonify(LevelRead.model_validate(level).model_dump()), 200
    except Exception as e:
        logger.error(f"Error getting level: {e}", exc_info=True)
        return jsonify({"detail": str(e)}), 500


@levels_bp.route("/levels/<int:level_id>", methods=["PUT"])
@login_required
def update_level(level_id: int):
    """更新关卡基本信息"""
    if not request.is_json:
        return jsonify({"detail": "Content-Type must be application/json"}), 400
    
    data = request.get_json()
    if not data:
        return jsonify({"detail": "Request body is required"}), 400
    
    try:
        payload = LevelUpdate(**data)
    except Exception as e:
        return jsonify({"detail": f"Invalid request data: {str(e)}"}), 400
    
    try:
        current_user = g.current_user
        db = get_db()
        
        level = LevelService.get_level(db, level_id)
        if not level:
            return jsonify({"detail": "关卡不存在"}), 404
        
        # 检查篇章权限
        chapter = ChapterService.get_chapter(db, level.chapter_id)
        if current_user.role != "admin" and chapter.teacher_id != current_user.id:
            return jsonify({"detail": "无权修改此关卡"}), 403
        
        level = LevelService.update_level(
            db=db,
            level_id=level_id,
            name=payload.name,
            description=payload.description,
            order=payload.order,
            is_visible=payload.is_visible,
            teaching_guide_md=payload.teaching_guide_md,
            allow_skip=payload.allow_skip,
            course_data_json=payload.course_data_json,
        )
        db.commit()
        logger.info(f"Level updated: {level_id} by user {current_user.id}")
        return jsonify(LevelRead.model_validate(level).model_dump()), 200
    except NotFoundError as e:
        return jsonify({"detail": e.message}), e.code
    except ValidationError as e:
        return jsonify({"detail": e.message}), e.code
    except Exception as e:
        logger.error(f"Error updating level: {e}", exc_info=True)
        return jsonify({"detail": str(e)}), 500


@levels_bp.route("/levels/<int:level_id>", methods=["DELETE"])
@login_required
def delete_level(level_id: int):
    """删除关卡"""
    try:
        current_user = g.current_user
        db = get_db()
        
        level = LevelService.get_level(db, level_id)
        if not level:
            return jsonify({"detail": "关卡不存在"}), 404
        
        # 检查篇章权限
        chapter = ChapterService.get_chapter(db, level.chapter_id)
        if current_user.role != "admin" and chapter.teacher_id != current_user.id:
            return jsonify({"detail": "无权删除此关卡"}), 403
        
        LevelService.delete_level(db, level_id)
        db.commit()
        logger.info(f"Level deleted: {level_id} by user {current_user.id}")
        return jsonify({"detail": "关卡删除成功"}), 200
    except NotFoundError as e:
        return jsonify({"detail": e.message}), e.code
    except Exception as e:
        logger.error(f"Error deleting level: {e}", exc_info=True)
        return jsonify({"detail": str(e)}), 500


@levels_bp.route("/levels/<int:level_id>/treasure-chests", methods=["POST"])
@login_required
def create_treasure_chest(level_id: int):
    """在关卡设置宝箱"""
    if not request.is_json:
        return jsonify({"detail": "Content-Type must be application/json"}), 400
    
    data = request.get_json()
    if not data:
        return jsonify({"detail": "Request body is required"}), 400
    
    try:
        payload = TreasureChestCreate(**data)
    except Exception as e:
        return jsonify({"detail": f"Invalid request data: {str(e)}"}), 400
    
    try:
        current_user = g.current_user
        db = get_db()
        
        level = LevelService.get_level(db, level_id)
        if not level:
            return jsonify({"detail": "关卡不存在"}), 404
        
        # 检查篇章权限
        chapter = ChapterService.get_chapter(db, level.chapter_id)
        if current_user.role != "admin" and chapter.teacher_id != current_user.id:
            return jsonify({"detail": "无权在此关卡设置宝箱"}), 403
        
        # 确保level_id一致
        if payload.level_id != level_id:
            return jsonify({"detail": "关卡ID不匹配"}), 400
        
        chest = TreasureChestService.create_chest(
            db=db,
            level_id=level_id,
            name=payload.name,
            position_x=payload.position_x,
            position_y=payload.position_y,
            reward_config=payload.reward_config
        )
        db.commit()
        logger.info(f"Treasure chest created: {chest.id} in level {level_id} by user {current_user.id}")
        return jsonify(TreasureChestRead.model_validate(chest).model_dump()), 201
    except ValidationError as e:
        return jsonify({"detail": e.message}), e.code
    except Exception as e:
        logger.error(f"Error creating treasure chest: {e}", exc_info=True)
        return jsonify({"detail": str(e)}), 500


@levels_bp.route("/levels/<int:level_id>/course-data", methods=["GET"])
@login_required
def get_course_data(level_id: int):
    """获取关卡的课程数据（JSON）"""
    try:
        current_user = g.current_user
        db = get_db()
        
        level = LevelService.get_level(db, level_id)
        if not level:
            return jsonify({"detail": "关卡不存在"}), 404
        
        # 检查篇章权限
        chapter = ChapterService.get_chapter(db, level.chapter_id)
        if current_user.role != "admin" and chapter.teacher_id != current_user.id:
            return jsonify({"detail": "无权访问此关卡"}), 403
        
        # 如果有保存的JSON，返回JSON；否则从MD生成
        if level.course_data_json:
            try:
                course_data = json.loads(level.course_data_json)
                return jsonify(course_data), 200
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON in course_data_json for level {level_id}")
                # 如果JSON无效，继续尝试从MD生成
        
        # 如果没有JSON，尝试从MD生成
        if level.teaching_guide_md:
            ai_service = AIService(db)
            course_data = ai_service.teaching_guide_to_course_json(level.teaching_guide_md)
            if course_data:
                # 保存生成的JSON
                level.course_data_json = json.dumps(course_data, ensure_ascii=False)
                level.last_md_sync = datetime.utcnow()
                level.edit_mode = 'md'
                db.commit()
                return jsonify(course_data), 200
        
        # 都没有，返回空结构
        return jsonify({"steps": [], "meta": {}}), 200
    except Exception as e:
        logger.error(f"Error getting course data: {e}", exc_info=True)
        return jsonify({"detail": str(e)}), 500


@levels_bp.route("/levels/<int:level_id>/course-data", methods=["PUT"])
@login_required
def update_course_data(level_id: int):
    """更新关卡的课程数据（JSON）"""
    if not request.is_json:
        return jsonify({"detail": "Content-Type must be application/json"}), 400
    
    data = request.get_json()
    if not data:
        return jsonify({"detail": "Request body is required"}), 400
    
    try:
        payload = CourseDataUpdate(**data)
    except Exception as e:
        return jsonify({"detail": f"Invalid request data: {str(e)}"}), 400
    
    try:
        current_user = g.current_user
        db = get_db()
        
        level = LevelService.get_level(db, level_id)
        if not level:
            return jsonify({"detail": "关卡不存在"}), 404
        
        # 检查篇章权限
        chapter = ChapterService.get_chapter(db, level.chapter_id)
        if current_user.role != "admin" and chapter.teacher_id != current_user.id:
            return jsonify({"detail": "无权修改此关卡"}), 403
        
        # 验证JSON结构
        if not isinstance(payload.course_data, dict):
            return jsonify({"detail": "course_data must be a JSON object"}), 400
        
        # 保存JSON数据
        level.course_data_json = json.dumps(payload.course_data, ensure_ascii=False)
        level.last_json_edit = datetime.utcnow()
        level.edit_mode = 'json'
        
        db.commit()
        logger.info(f"Course data updated for level {level_id} by user {current_user.id}")
        return jsonify({"detail": "保存成功", "course_data": payload.course_data}), 200
    except Exception as e:
        logger.error(f"Error updating course data: {e}", exc_info=True)
        return jsonify({"detail": str(e)}), 500


@levels_bp.route("/levels/<int:level_id>/sync-md", methods=["POST"])
@login_required
def sync_to_md(level_id: int):
    """将JSON数据同步回MD（可选功能）"""
    try:
        current_user = g.current_user
        db = get_db()
        
        level = LevelService.get_level(db, level_id)
        if not level:
            return jsonify({"detail": "关卡不存在"}), 404
        
        # 检查篇章权限
        chapter = ChapterService.get_chapter(db, level.chapter_id)
        if current_user.role != "admin" and chapter.teacher_id != current_user.id:
            return jsonify({"detail": "无权修改此关卡"}), 403
        
        if not level.course_data_json:
            return jsonify({"detail": "没有可同步的JSON数据"}), 400
        
        # 调用AI将JSON转回MD（需要实现这个方法）
        ai_service = AIService(db)
        try:
            course_data = json.loads(level.course_data_json)
            # 注意：这个方法需要在AIService中实现
            # md_content = ai_service.course_json_to_md(course_data)
            # 暂时返回提示信息
            return jsonify({
                "detail": "JSON到MD同步功能待实现",
                "note": "此功能需要实现 course_json_to_md 方法"
            }), 501
        except json.JSONDecodeError:
            return jsonify({"detail": "JSON数据格式错误"}), 400
    except Exception as e:
        logger.error(f"Error syncing to MD: {e}", exc_info=True)
        return jsonify({"detail": str(e)}), 500

