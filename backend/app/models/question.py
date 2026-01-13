from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text, ForeignKey, JSON, Float, Boolean

from ..db.base import Base


class Question(Base):
    """题目模型（从关卡中自动提取到题库）"""
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    level_id = Column(Integer, ForeignKey("levels.id"), nullable=False, index=True)  # 所属关卡ID（自动关联）
    question_type = Column(String(64), nullable=False)  # 题型：single_choice, multiple_choice, true_false, fill_blank, short_answer, programming
    title = Column(Text, nullable=False)  # 题目标题
    content = Column(Text, nullable=True)  # 题目内容（支持图文、数学公式、代码高亮）
    options = Column(JSON, nullable=True)  # 选项（JSON格式，用于选择题）
    correct_answer = Column(Text, nullable=True)  # 正确答案
    answer_analysis = Column(Text, nullable=True)  # 答案解析
    difficulty = Column(String(32), default="medium", nullable=False)  # 难度：easy, medium, hard
    score = Column(Float, default=10.0, nullable=False)  # 分值
    knowledge_point = Column(String(255), nullable=True)  # 知识点
    tags = Column(JSON, nullable=True)  # 标签（JSON数组）
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

