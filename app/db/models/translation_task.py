from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import Optional

class TranslationTask(SQLModel, table=True):
    __tablename__ = "translation_task"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    task_id: str = Field(index=True, unique=True)
    event_type: str
    jwt_token: str
    file_path: str
    prompt_template: str
    target_language: str
    instruction: Optional[str]
    start_time: datetime
    translate_start_time: Optional[datetime]
    translation_end_time: Optional[datetime]
    status: str
    error_message: Optional[str]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)