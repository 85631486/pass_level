"""
任务环节服务
"""
from typing import Optional, List

from sqlalchemy.orm import Session

from ..models.task_phase import TaskPhase
from ..core.exceptions import NotFoundError, ValidationError


class TaskPhaseService:
    """任务环节服务类"""

    @staticmethod
    def get_phase(db: Session, phase_id: int) -> Optional[TaskPhase]:
        return db.query(TaskPhase).filter(TaskPhase.id == phase_id).first()

    @staticmethod
    def get_phases_by_task(db: Session, task_id: int) -> List[TaskPhase]:
        return (
            db.query(TaskPhase)
            .filter(TaskPhase.task_id == task_id)
            .order_by(TaskPhase.order.asc(), TaskPhase.id.asc())
            .all()
        )

    @staticmethod
    def create_phase(
        db: Session,
        task_id: int,
        phase_name: str,
        order: int = 0,
        is_required: bool = True,
    ) -> TaskPhase:
        if not phase_name:
            raise ValidationError("环节名称不能为空")

        phase = TaskPhase(
            task_id=task_id,
            phase_name=phase_name,
            order=order,
            is_required=is_required,
        )
        db.add(phase)
        db.commit()
        db.refresh(phase)
        return phase

    @staticmethod
    def update_phase(
        db: Session,
        phase_id: int,
        phase_name: Optional[str] = None,
        order: Optional[int] = None,
        is_required: Optional[bool] = None,
    ) -> TaskPhase:
        phase = TaskPhaseService.get_phase(db, phase_id)
        if not phase:
            raise NotFoundError("任务环节不存在")

        if phase_name is not None:
            phase.phase_name = phase_name
        if order is not None:
            phase.order = order
        if is_required is not None:
            phase.is_required = is_required

        db.commit()
        db.refresh(phase)
        return phase

    @staticmethod
    def delete_phase(db: Session, phase_id: int) -> bool:
        phase = TaskPhaseService.get_phase(db, phase_id)
        if not phase:
            raise NotFoundError("任务环节不存在")

        db.delete(phase)
        db.commit()
        return True

















