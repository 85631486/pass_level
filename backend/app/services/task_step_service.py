"""
任务步骤服务
"""
from typing import Optional, List

from sqlalchemy.orm import Session

from ..models.task_step import TaskStep
from ..core.exceptions import NotFoundError, ValidationError


class TaskStepService:
    """任务步骤服务类"""

    @staticmethod
    def get_step(db: Session, step_id: int) -> Optional[TaskStep]:
        return db.query(TaskStep).filter(TaskStep.id == step_id).first()

    @staticmethod
    def get_steps_by_phase(db: Session, phase_id: int) -> List[TaskStep]:
        return (
            db.query(TaskStep)
            .filter(TaskStep.phase_id == phase_id)
            .order_by(TaskStep.order.asc(), TaskStep.id.asc())
            .all()
        )

    @staticmethod
    def create_step(
        db: Session,
        phase_id: int,
        step_name: str,
        content: Optional[str] = None,
        requirements: Optional[str] = None,
        submission_type: str = "text",
        validation_rules: Optional[dict] = None,
        order: int = 0,
    ) -> TaskStep:
        if not step_name:
            raise ValidationError("步骤名称不能为空")

        step = TaskStep(
            phase_id=phase_id,
            step_name=step_name,
            content=content,
            requirements=requirements,
            submission_type=submission_type,
            validation_rules=validation_rules,
            order=order,
        )
        db.add(step)
        db.commit()
        db.refresh(step)
        return step

    @staticmethod
    def update_step(
        db: Session,
        step_id: int,
        step_name: Optional[str] = None,
        content: Optional[str] = None,
        requirements: Optional[str] = None,
        submission_type: Optional[str] = None,
        validation_rules: Optional[dict] = None,
        order: Optional[int] = None,
    ) -> TaskStep:
        step = TaskStepService.get_step(db, step_id)
        if not step:
            raise NotFoundError("任务步骤不存在")

        if step_name is not None:
            step.step_name = step_name
        if content is not None:
            step.content = content
        if requirements is not None:
            step.requirements = requirements
        if submission_type is not None:
            step.submission_type = submission_type
        if validation_rules is not None:
            step.validation_rules = validation_rules
        if order is not None:
            step.order = order

        db.commit()
        db.refresh(step)
        return step

    @staticmethod
    def delete_step(db: Session, step_id: int) -> bool:
        step = TaskStepService.get_step(db, step_id)
        if not step:
            raise NotFoundError("任务步骤不存在")

        db.delete(step)
        db.commit()
        return True

















