from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Boolean, ForeignKey

from ..db.base import Base


class TaskPhase(Base):
    """任务环节模型"""
    __tablename__ = "task_phases"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False, index=True)  # 所属任务ID
    phase_name = Column(String(255), nullable=False)  # 环节名称
    order = Column(Integer, default=0, nullable=False)  # 环节顺序
    is_required = Column(Boolean, default=True, nullable=False)  # 是否必做
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

