"""
任务服务
"""
from typing import Optional, List
from sqlalchemy.orm import Session

from ..models.task import Task
from ..core.exceptions import NotFoundError, ValidationError


class TaskService:
    """任务服务类"""

    @staticmethod
    def get_task(db: Session, task_id: int) -> Optional[Task]:
        """获取任务"""
        return db.query(Task).filter(Task.id == task_id).first()

    @staticmethod
    def get_tasks_by_level(db: Session, level_id: int, skip: int = 0, limit: int = 100) -> List[Task]:
        """获取关卡下的任务列表"""
        return db.query(Task).filter(Task.level_id == level_id).offset(skip).limit(limit).all()

    @staticmethod
    def create_task(
        db: Session,
        level_id: int,
        name: str,
        description: Optional[str] = None,
        objective: Optional[str] = None
    ) -> Task:
        """创建任务"""
        if not name:
            raise ValidationError("任务名称不能为空")
        
        task = Task(
            level_id=level_id,
            name=name,
            description=description,
            objective=objective
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def update_task(
        db: Session,
        task_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        objective: Optional[str] = None
    ) -> Task:
        """更新任务"""
        task = TaskService.get_task(db, task_id)
        if not task:
            raise NotFoundError("任务不存在")
        
        if name is not None:
            task.name = name
        if description is not None:
            task.description = description
        if objective is not None:
            task.objective = objective
        
        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def delete_task(db: Session, task_id: int) -> bool:
        """删除任务"""
        task = TaskService.get_task(db, task_id)
        if not task:
            raise NotFoundError("任务不存在")
        
        db.delete(task)
        db.commit()
        return True

