from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

from ..db.base import Base


class Chapter(Base):
    """篇章模型（相当于原课程概念）"""
    __tablename__ = "chapters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)  # 篇章名称
    description = Column(Text, nullable=True)  # 篇章描述
    teacher_id = Column(Integer, nullable=False, index=True)  # 教师ID，关联users表
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

