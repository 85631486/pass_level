from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text, ForeignKey

from ..db.base import Base


class TaskResource(Base):
    """任务资源模型

    用于描述任务执行过程中所需的教材、数据集、示例代码等资源。
    """

    __tablename__ = "task_resources"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False, index=True)  # 所属任务ID
    name = Column(String(255), nullable=False)  # 资源名称
    resource_type = Column(String(64), nullable=False, default="link")  # 资源类型：file, link, text, dataset 等
    url = Column(String(1024), nullable=True)  # 资源链接（文件存储路径或外部链接）
    description = Column(Text, nullable=True)  # 资源说明
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

















