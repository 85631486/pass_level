from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, Text, ForeignKey, JSON

from ..db.base import Base


class TaskPhaseQuestionRel(Base):
    """环节与闯关考题关联关系模型"""
    __tablename__ = "task_phase_question_rels"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False, index=True)  # 所属任务ID
    relation_config = Column(JSON, nullable=True)  # 关联规则配置（JSON格式）
    # 例如：{"type": "all_completed", "phases": [1, 2, 3]} 或 {"type": "threshold", "threshold": 0.8}
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

