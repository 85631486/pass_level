"""
地图服务
"""
from typing import Optional
from sqlalchemy.orm import Session

from ..models.level_map import LevelMap
from ..core.exceptions import NotFoundError


class LevelMapService:
    """地图服务类"""

    @staticmethod
    def get_map_by_chapter(db: Session, chapter_id: int) -> Optional[LevelMap]:
        """获取篇章的地图配置"""
        return db.query(LevelMap).filter(LevelMap.chapter_id == chapter_id).first()

    @staticmethod
    def create_or_update_map(db: Session, chapter_id: int, map_config_json: Optional[str] = None) -> LevelMap:
        """创建或更新地图配置"""
        level_map = LevelMapService.get_map_by_chapter(db, chapter_id)
        
        if level_map:
            # 更新
            if map_config_json is not None:
                level_map.map_config_json = map_config_json
            db.commit()
            db.refresh(level_map)
            return level_map
        else:
            # 创建
            level_map = LevelMap(
                chapter_id=chapter_id,
                map_config_json=map_config_json
            )
            db.add(level_map)
            db.commit()
            db.refresh(level_map)
            return level_map

    @staticmethod
    def delete_map(db: Session, chapter_id: int) -> bool:
        """删除地图配置"""
        level_map = LevelMapService.get_map_by_chapter(db, chapter_id)
        if not level_map:
            raise NotFoundError("地图配置不存在")
        
        db.delete(level_map)
        db.commit()
        return True

