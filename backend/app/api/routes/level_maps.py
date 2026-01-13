"""
地图管理API
"""
import logging
from flask import Blueprint, jsonify, request

from ...core.exceptions import NotFoundError
from ...core.security import login_required
from flask import g
from ...db.session import get_db
from ...schemas.level_map import LevelMapRead, LevelMapUpdate
from ...services.level_map_service import LevelMapService
from ...services.chapter_service import ChapterService

level_maps_bp = Blueprint("level_maps", __name__, url_prefix="/api/v1/chapters")
logger = logging.getLogger(__name__)


@level_maps_bp.route("/<int:chapter_id>/map", methods=["GET"])
@login_required
def get_map(chapter_id: int):
    """获取地图配置"""
    try:
        current_user = g.current_user
        db = get_db()
        
        # 检查篇章权限
        chapter = ChapterService.get_chapter(db, chapter_id)
        if not chapter:
            return jsonify({"detail": "篇章不存在"}), 404
        
        if current_user.role != "admin" and chapter.teacher_id != current_user.id:
            return jsonify({"detail": "无权访问此篇章"}), 403
        
        level_map = LevelMapService.get_map_by_chapter(db, chapter_id)
        if not level_map:
            # 如果地图不存在，返回空配置
            return jsonify({
                "id": None,
                "chapter_id": chapter_id,
                "map_config_json": None
            }), 200
        
        return jsonify(LevelMapRead.model_validate(level_map).model_dump()), 200
    except Exception as e:
        logger.error(f"Error getting map: {e}", exc_info=True)
        return jsonify({"detail": str(e)}), 500


@level_maps_bp.route("/<int:chapter_id>/map", methods=["PUT"])
@login_required
def update_map(chapter_id: int):
    """更新地图配置（思维导图数据，包含关卡节点创建/更新）"""
    if not request.is_json:
        return jsonify({"detail": "Content-Type must be application/json"}), 400
    
    data = request.get_json()
    if not data:
        return jsonify({"detail": "Request body is required"}), 400
    
    try:
        current_user = g.current_user
        db = get_db()
        
        # 检查篇章权限
        chapter = ChapterService.get_chapter(db, chapter_id)
        if not chapter:
            return jsonify({"detail": "篇章不存在"}), 404
        
        if current_user.role != "admin" and chapter.teacher_id != current_user.id:
            return jsonify({"detail": "无权修改此篇章"}), 403
        
        map_config_json = data.get("map_config_json")
        if map_config_json is not None and not isinstance(map_config_json, str):
            # 如果是dict，转换为JSON字符串
            import json
            map_config_json = json.dumps(map_config_json, ensure_ascii=False)
        
        level_map = LevelMapService.create_or_update_map(
            db=db,
            chapter_id=chapter_id,
            map_config_json=map_config_json
        )
        db.commit()
        logger.info(f"Map updated for chapter {chapter_id} by user {current_user.id}")
        return jsonify(LevelMapRead.model_validate(level_map).model_dump()), 200
    except Exception as e:
        logger.error(f"Error updating map: {e}", exc_info=True)
        return jsonify({"detail": str(e)}), 500

