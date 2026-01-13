from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, Text, ForeignKey

from ..db.base import Base


class LevelMap(Base):
    """过关地图模型"""
    __tablename__ = "level_maps"

    id = Column(Integer, primary_key=True, index=True)
    chapter_id = Column(Integer, ForeignKey("chapters.id"), unique=True, nullable=False, index=True)  # 所属篇章ID（一对一）
    map_config_json = Column(Text, nullable=True)  # 思维导图配置JSON（关卡树结构）
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

