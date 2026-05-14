from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from .base_model import BaseModel

class SystemLog(BaseModel):
    __tablename__ = "system_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    trace_id = Column(String(36), nullable=True, index=True)
    level = Column(String(20), nullable=False)
    message = Column(Text, nullable=False)
    route = Column(String(255), nullable=True)
    method = Column(String(10), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)