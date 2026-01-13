from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text, ForeignKey, Float, Boolean

from ..db.base import Base


class PointMall(Base):
    """积分商城模型"""
    __tablename__ = "point_malls"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)  # 商城名称
    description = Column(Text, nullable=True)  # 商城描述
    is_active = Column(Boolean, default=True, nullable=False)  # 是否启用
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class PointMallItem(Base):
    """积分商城商品模型"""
    __tablename__ = "point_mall_items"

    id = Column(Integer, primary_key=True, index=True)
    mall_id = Column(Integer, ForeignKey("point_malls.id"), nullable=False, index=True)  # 所属商城ID
    name = Column(String(255), nullable=False)  # 商品名称
    description = Column(Text, nullable=True)  # 商品描述
    item_type = Column(String(64), nullable=False)  # 商品类型：item（道具）, gift（礼品）
    point_cost = Column(Integer, nullable=False)  # 所需积分
    stock = Column(Integer, default=0, nullable=False)  # 库存（-1表示无限）
    image_url = Column(String(512), nullable=True)  # 商品图片
    is_active = Column(Boolean, default=True, nullable=False)  # 是否上架
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

