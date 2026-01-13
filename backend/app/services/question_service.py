"""
题目服务
"""
from typing import Optional, List

from sqlalchemy.orm import Session

from ..models.question import Question
from ..models.task_question_rel import TaskQuestionRel
from ..core.exceptions import NotFoundError, ValidationError


class QuestionService:
    """题目服务类（负责题库与关卡关联）"""

    @staticmethod
    def get_question(db: Session, question_id: int) -> Optional[Question]:
        return db.query(Question).filter(Question.id == question_id).first()

    @staticmethod
    def get_questions_by_level(db: Session, level_id: int) -> List[Question]:
        return (
            db.query(Question)
            .filter(Question.level_id == level_id)
            .order_by(Question.id.asc())
            .all()
        )

    @staticmethod
    def create_question(
        db: Session,
        level_id: int,
        question_type: str,
        title: str,
        content: Optional[str] = None,
        options: Optional[list] = None,
        correct_answer: Optional[str] = None,
        answer_analysis: Optional[str] = None,
        difficulty: str = "medium",
        score: float = 10.0,
        knowledge_point: Optional[str] = None,
        tags: Optional[list] = None,
        task_id: Optional[int] = None,
        order: int = 0,
    ) -> Question:
        """创建题目，并可选地关联到指定任务（自动提取到题库）"""
        if not title:
            raise ValidationError("题目标题不能为空")
        if not question_type:
            raise ValidationError("题目类型不能为空")

        question = Question(
            level_id=level_id,
            question_type=question_type,
            title=title,
            content=content,
            options=options,
            correct_answer=correct_answer,
            answer_analysis=answer_analysis,
            difficulty=difficulty,
            score=score,
            knowledge_point=knowledge_point,
            tags=tags,
        )
        db.add(question)
        db.flush()  # 先拿到 question.id

        if task_id is not None:
            rel = TaskQuestionRel(task_id=task_id, question_id=question.id, order=order)
            db.add(rel)

        db.commit()
        db.refresh(question)
        return question

    @staticmethod
    def update_question(
        db: Session,
        question_id: int,
        **kwargs,
    ) -> Question:
        """更新题目信息（仅题库字段）"""
        question = QuestionService.get_question(db, question_id)
        if not question:
            raise NotFoundError("题目不存在")

        updatable_fields = {
            "question_type",
            "title",
            "content",
            "options",
            "correct_answer",
            "answer_analysis",
            "difficulty",
            "score",
            "knowledge_point",
            "tags",
        }
        for field, value in kwargs.items():
            if field in updatable_fields and value is not None:
                setattr(question, field, value)

        db.commit()
        db.refresh(question)
        return question

    @staticmethod
    def delete_question(db: Session, question_id: int) -> bool:
        """删除题目，同时删除与任务的关联关系"""
        question = QuestionService.get_question(db, question_id)
        if not question:
            raise NotFoundError("题目不存在")

        db.query(TaskQuestionRel).filter(TaskQuestionRel.question_id == question_id).delete()
        db.delete(question)
        db.commit()
        return True

















