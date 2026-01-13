from typing import Optional, Any

from pydantic import BaseModel, Field


class LevelMapBase(BaseModel):
    """地图基础模型"""
    map_config_json: Optional[str] = Field(None, description="思维导图配置JSON（关卡树结构）")


class LevelMapCreate(LevelMapBase):
    """创建地图模型"""
    chapter_id: int = Field(..., description="所属篇章ID")


class LevelMapUpdate(LevelMapBase):
    """更新地图模型"""
    pass


class LevelMapRead(LevelMapBase):
    """地图读取模型"""
    id: int
    chapter_id: int

    class Config:
        from_attributes = True

