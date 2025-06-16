from sqlmodel import SQLModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class LogCreate(SQLModel):
    id: UUID
    user_id: UUID
    operation_type: str
    file_path: str
    file_size: Optional[int]
    status: str
    message: Optional[str]
    source_ip: Optional[str]
    user_agent: Optional[str]
    created_at: datetime

class LogRead(LogCreate):
    id: UUID
    created_at: datetime
    updated_at: datetime