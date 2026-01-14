"""
关卡服务
"""
from typing import Optional, List
from sqlalchemy.orm import Session

from ..models.level import Level
from ..core.exceptions import NotFoundError, ValidationError


class LevelService:
    """关卡服务类"""

    @staticmethod
    def get_level(db: Session, level_id: int) -> Optional[Level]:
        """获取关卡"""
        return db.query(Level).filter(Level.id == level_id).first()

    @staticmethod
    def get_levels_by_chapter(db: Session, chapter_id: int, skip: int = 0, limit: int = 100) -> List[Level]:
        """获取篇章下的关卡列表"""
        return db.query(Level).filter(Level.chapter_id == chapter_id).order_by(Level.order).offset(skip).limit(limit).all()

    @staticmethod
    def create_level(
        db: Session,
        chapter_id: int,
        name: str,
        description: Optional[str] = None,
        order: int = 0,
        allow_skip: bool = False,
    ) -> Level:
        """创建关卡"""
        if not name:
            raise ValidationError("关卡名称不能为空")
        
        level = Level(
            chapter_id=chapter_id,
            name=name,
            description=description,
            order=order,
            allow_skip=allow_skip,
        )
        db.add(level)
        db.commit()
        db.refresh(level)
        return level

    @staticmethod
    def update_level(
        db: Session,
        level_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        order: Optional[int] = None,
        is_visible: Optional[bool] = None,
        teaching_guide_md: Optional[str] = None,
        allow_skip: Optional[bool] = None,
        course_data_json: Optional[str] = None,
    ) -> Level:
        """更新关卡"""
        level = LevelService.get_level(db, level_id)
        if not level:
            raise NotFoundError("关卡不存在")
        
        if name is not None:
            level.name = name
        if description is not None:
            level.description = description
        if order is not None:
            level.order = order
        if is_visible is not None:
            level.is_visible = is_visible
        if teaching_guide_md is not None:
            level.teaching_guide_md = teaching_guide_md
        if allow_skip is not None:
            level.allow_skip = allow_skip
        if course_data_json is not None:
            level.course_data_json = course_data_json
        
        db.commit()
        db.refresh(level)
        return level

    @staticmethod
    def delete_level(db: Session, level_id: int) -> bool:
        """删除关卡"""
        level = LevelService.get_level(db, level_id)
        if not level:
            raise NotFoundError("关卡不存在")
        
        db.delete(level)
        db.commit()
        return True

    @staticmethod
    def publish_level(db: Session, level_id: int) -> Level:
        """发布关卡"""
        level = LevelService.get_level(db, level_id)
        if not level:
            raise NotFoundError("关卡不存在")
        
        from datetime import datetime
        level.is_published = True
        level.is_visible = True
        level.published_at = datetime.utcnow()
        
        db.commit()
        db.refresh(level)
        return level

    @staticmethod
    def unpublish_level(db: Session, level_id: int) -> Level:
        """取消发布关卡"""
        level = LevelService.get_level(db, level_id)
        if not level:
            raise NotFoundError("关卡不存在")
        
        level.is_published = False
        level.is_visible = False
        
        db.commit()
        db.refresh(level)
        return level

