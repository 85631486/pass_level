from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, ForeignKey

from ..db.base import Base


class TaskQuestionRel(Base):
    """任务-题目关联模型

    用于表示某道题目属于哪个任务/关卡中的哪一部分，
    支持题目在题库中复用，但在具体任务下有独立的排序等属性。
    """

    __tablename__ = "task_question_rels"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False, index=True)  # 所属任务ID
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False, index=True)  # 题目ID
    order = Column(Integer, default=0, nullable=False)  # 在任务中的顺序
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

















