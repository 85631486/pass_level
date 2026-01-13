"""
篇章服务
"""
from typing import Optional, List
from sqlalchemy.orm import Session

from ..models.chapter import Chapter
from ..core.exceptions import NotFoundError, ValidationError


class ChapterService:
    """篇章服务类"""

    @staticmethod
    def get_chapter(db: Session, chapter_id: int) -> Optional[Chapter]:
        """获取篇章"""
        return db.query(Chapter).filter(Chapter.id == chapter_id).first()

    @staticmethod
    def get_chapters(db: Session, teacher_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[Chapter]:
        """获取篇章列表"""
        query = db.query(Chapter)
        if teacher_id:
            query = query.filter(Chapter.teacher_id == teacher_id)
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def create_chapter(db: Session, name: str, description: Optional[str], teacher_id: int) -> Chapter:
        """创建篇章"""
        if not name:
            raise ValidationError("篇章名称不能为空")
        
        chapter = Chapter(
            name=name,
            description=description,
            teacher_id=teacher_id
        )
        db.add(chapter)
        db.commit()
        db.refresh(chapter)
        return chapter

    @staticmethod
    def update_chapter(db: Session, chapter_id: int, name: Optional[str] = None, description: Optional[str] = None) -> Chapter:
        """更新篇章"""
        chapter = ChapterService.get_chapter(db, chapter_id)
        if not chapter:
            raise NotFoundError("篇章不存在")
        
        if name is not None:
            chapter.name = name
        if description is not None:
            chapter.description = description
        
        db.commit()
        db.refresh(chapter)
        return chapter

    @staticmethod
    def delete_chapter(db: Session, chapter_id: int) -> bool:
        """删除篇章"""
        chapter = ChapterService.get_chapter(db, chapter_id)
        if not chapter:
            raise NotFoundError("篇章不存在")
        
        db.delete(chapter)
        db.commit()
        return True

