from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String

from ..db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=True, index=True)
    phone = Column(String(32), unique=True, nullable=True, index=True)
    student_id = Column(String(64), unique=True, nullable=True, index=True)  # 学号
    nickname = Column(String(64), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(32), default="student", nullable=False, index=True)  # student, teacher, admin
    is_active = Column(Boolean, default=True, nullable=False)
    class_name = Column(String(128), nullable=True)  # 班级
    notes = Column(String(512), nullable=True)  # 备注
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

