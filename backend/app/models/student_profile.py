from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, ForeignKey, Float

from ..db.base import Base


class StudentProfile(Base):
    """学生档案模型（等级、经验值）"""
    __tablename__ = "student_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)  # 用户ID（一对一）
    level = Column(Integer, default=1, nullable=False)  # 等级
    experience = Column(Float, default=0.0, nullable=False)  # 经验值
    total_score = Column(Float, default=0.0, nullable=False)  # 总得分
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

