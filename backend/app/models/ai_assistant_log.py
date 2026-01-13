from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text, JSON

from ..db.base import Base


class AIAssistantLog(Base):
    """AI交互日志模型"""
    __tablename__ = "ai_assistant_logs"

    id = Column(Integer, primary_key=True, index=True)
    action = Column(String(64), nullable=False, index=True)  # 操作类型：generate_mindmap, generate_task等
    input_data = Column(JSON, nullable=True)  # 输入数据（JSON格式）
    output_data = Column(JSON, nullable=True)  # 输出数据（JSON格式）
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

