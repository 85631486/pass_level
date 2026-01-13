from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text, ForeignKey, JSON, Float, Boolean

from ..db.base import Base


class TreasureChest(Base):
    """宝箱模型"""
    __tablename__ = "treasure_chests"

    id = Column(Integer, primary_key=True, index=True)
    level_id = Column(Integer, ForeignKey("levels.id"), nullable=False, index=True)  # 所属关卡ID
    name = Column(String(255), nullable=False)  # 宝箱名称
    position_x = Column(Float, nullable=True)  # 宝箱在地图上的X坐标
    position_y = Column(Float, nullable=True)  # 宝箱在地图上的Y坐标
    reward_config = Column(JSON, nullable=True)  # 奖励配置（JSON格式）
    # 例如：{"type": "item", "item_id": 1, "quantity": 1} 或 {"type": "point", "amount": 100} 或 {"type": "gift", "gift_id": 1}
    is_opened = Column(Boolean, default=False, nullable=False)  # 是否已开启（学生端使用）
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

