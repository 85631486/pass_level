from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text, ForeignKey

from ..db.base import Base


class SkillCard(Base):
    """技能卡片模型"""
    __tablename__ = "skill_cards"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False, index=True)  # 所属任务ID
    title = Column(String(255), nullable=False)  # 卡片标题
    content = Column(Text, nullable=True)  # 卡片内容（支持图文、视频）
    skill_name = Column(String(255), nullable=True)  # 技能名称
    order = Column(Integer, default=0, nullable=False)  # 排序
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

