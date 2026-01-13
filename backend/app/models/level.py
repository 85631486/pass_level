from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Boolean, Text, ForeignKey

from ..db.base import Base


class Level(Base):
    """关卡模型（简化版：基于MD教案）"""
    __tablename__ = "levels"

    id = Column(Integer, primary_key=True, index=True)
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=False, index=True)  # 所属篇章ID
    name = Column(String(255), nullable=False)  # 关卡名称
    description = Column(Text, nullable=True)  # 关卡描述（简短）
    order = Column(Integer, default=0, nullable=False)  # 关卡顺序
    allow_skip = Column(Boolean, default=False, nullable=False)  # 是否允许跳过
    # 教案内容（MD格式）：包含完整的实验指导书内容
    teaching_guide_md = Column(Text, nullable=True)  # 教案/实验指导书（Markdown格式）
    # 课程数据（JSON格式）：从MD生成的交互式课程数据，可编辑
    course_data_json = Column(Text, nullable=True)  # 课程数据JSON（可编辑）
    last_md_sync = Column(DateTime, nullable=True)  # 最后一次从MD同步的时间
    last_json_edit = Column(DateTime, nullable=True)  # 最后一次JSON编辑的时间
    edit_mode = Column(String(10), nullable=True)  # 当前编辑模式：'md' 或 'json'
    is_visible = Column(Boolean, default=False, nullable=False)  # 是否可见（发布状态）
    is_published = Column(Boolean, default=False, nullable=False, index=True)  # 是否已发布
    published_at = Column(DateTime, nullable=True)  # 发布时间
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

