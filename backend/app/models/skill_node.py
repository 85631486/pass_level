from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text, ForeignKey

from ..db.base import Base


class SkillNode(Base):
    """技能树节点模型"""
    __tablename__ = "skill_nodes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)  # 技能节点名称
    description = Column(Text, nullable=True)  # 技能描述
    parent_id = Column(Integer, ForeignKey("skill_nodes.id"), nullable=True, index=True)  # 父节点ID（树形结构）
    order = Column(Integer, default=0, nullable=False)  # 排序
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

