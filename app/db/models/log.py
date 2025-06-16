from typing import Optional
from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from datetime import datetime, timezone

class Log(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=lambda:  datetime.now(timezone.utc), nullable=False)
    updated_at: datetime = Field(default_factory=lambda:  datetime.now(timezone.utc), nullable=False)
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