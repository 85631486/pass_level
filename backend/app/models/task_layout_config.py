from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, ForeignKey, JSON

from ..db.base import Base


class TaskLayoutConfig(Base):
    """关卡/任务界面布局配置

    存储关卡编辑器中对任务界面布局的自定义设置（如面板位置、组件显示与否等）。
    """

    __tablename__ = "task_layout_configs"

    id = Column(Integer, primary_key=True, index=True)
    level_id = Column(Integer, ForeignKey("levels.id"), nullable=False, index=True)  # 所属关卡ID
    layout_json = Column(JSON, nullable=True)  # 布局配置 JSON
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

















