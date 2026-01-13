from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text, ForeignKey

from ..db.base import Base


class Task(Base):
    """任务模型"""
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    level_id = Column(Integer, ForeignKey("levels.id"), nullable=False, index=True)  # 所属关卡ID
    name = Column(String(255), nullable=False)  # 任务名称
    description = Column(Text, nullable=True)  # 任务描述
    objective = Column(Text, nullable=True)  # 任务目标
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

