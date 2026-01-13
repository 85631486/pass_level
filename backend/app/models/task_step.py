from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text, ForeignKey, JSON

from ..db.base import Base


class TaskStep(Base):
    """任务步骤模型"""
    __tablename__ = "task_steps"

    id = Column(Integer, primary_key=True, index=True)
    phase_id = Column(Integer, ForeignKey("task_phases.id"), nullable=False, index=True)  # 所属环节ID
    step_name = Column(String(255), nullable=False)  # 步骤名称
    content = Column(Text, nullable=True)  # 步骤内容
    requirements = Column(Text, nullable=True)  # 操作要求
    submission_type = Column(String(64), nullable=False, default="text")  # 提交项类型：text, file, link, code等
    validation_rules = Column(JSON, nullable=True)  # 提交项校验规则（JSON格式）
    order = Column(Integer, default=0, nullable=False)  # 步骤顺序
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

