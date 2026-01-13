from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, ForeignKey, Float

from ..db.base import Base


class StudentSkill(Base):
    """学生技能模型"""
    __tablename__ = "student_skills"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)  # 用户ID
    skill_node_id = Column(Integer, ForeignKey("skill_nodes.id"), nullable=False, index=True)  # 技能节点ID
    level = Column(Integer, default=1, nullable=False)  # 技能等级
    experience = Column(Float, default=0.0, nullable=False)  # 技能经验值
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

