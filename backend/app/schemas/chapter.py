from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ChapterBase(BaseModel):
    """篇章基础模型"""
    name: str = Field(..., min_length=1, max_length=255, description="篇章名称")
    description: Optional[str] = Field(None, description="篇章描述")


class ChapterCreate(ChapterBase):
    """创建篇章模型"""
    pass


class ChapterUpdate(BaseModel):
    """更新篇章模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="篇章名称")
    description: Optional[str] = Field(None, description="篇章描述")


class ChapterRead(ChapterBase):
    """篇章读取模型"""
    id: int
    teacher_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

