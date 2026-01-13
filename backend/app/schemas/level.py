from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class LevelBase(BaseModel):
    """关卡基础模型"""
    name: str = Field(..., min_length=1, max_length=255, description="关卡名称")
    description: Optional[str] = Field(None, description="关卡描述")
    order: int = Field(0, description="关卡顺序")
    allow_skip: bool = Field(False, description="是否允许跳过关卡")


class LevelCreate(LevelBase):
    """创建关卡模型"""
    chapter_id: int = Field(..., description="所属篇章ID")


class LevelUpdate(BaseModel):
    """更新关卡模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="关卡名称")
    description: Optional[str] = Field(None, description="关卡描述")
    order: Optional[int] = Field(None, description="关卡顺序")
    is_visible: Optional[bool] = Field(None, description="是否可见")
    teaching_guide_md: Optional[str] = Field(None, description="教案/实验指导书（Markdown格式）")
    allow_skip: Optional[bool] = Field(None, description="是否允许跳过关卡")


class LevelRead(LevelBase):
    """关卡读取模型"""
    id: int
    chapter_id: int
    is_visible: bool
    is_published: bool
    published_at: Optional[datetime]
    teaching_guide_md: Optional[str] = Field(None, description="教案/实验指导书（Markdown格式）")
    course_data_json: Optional[str] = Field(None, description="课程数据JSON（可编辑）")
    last_md_sync: Optional[datetime] = Field(None, description="最后一次从MD同步的时间")
    last_json_edit: Optional[datetime] = Field(None, description="最后一次JSON编辑的时间")
    edit_mode: Optional[str] = Field(None, description="当前编辑模式：'md' 或 'json'")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CourseDataUpdate(BaseModel):
    """课程数据更新模型"""
    course_data: dict = Field(..., description="课程数据JSON对象")


class CourseDataResponse(BaseModel):
    """课程数据响应模型"""
    course_data: dict = Field(..., description="课程数据JSON对象")

