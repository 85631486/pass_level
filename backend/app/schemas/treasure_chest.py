from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel, Field


class TreasureChestBase(BaseModel):
    """宝箱基础模型"""
    name: str = Field(..., min_length=1, max_length=255, description="宝箱名称")
    position_x: Optional[float] = Field(None, description="X坐标")
    position_y: Optional[float] = Field(None, description="Y坐标")
    reward_config: Optional[dict] = Field(None, description="奖励配置（JSON格式）")


class TreasureChestCreate(TreasureChestBase):
    """创建宝箱模型"""
    level_id: int = Field(..., description="所属关卡ID")


class TreasureChestUpdate(BaseModel):
    """更新宝箱模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="宝箱名称")
    position_x: Optional[float] = Field(None, description="X坐标")
    position_y: Optional[float] = Field(None, description="Y坐标")
    reward_config: Optional[dict] = Field(None, description="奖励配置（JSON格式）")


class TreasureChestRead(TreasureChestBase):
    """宝箱读取模型"""
    id: int
    level_id: int
    is_opened: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

