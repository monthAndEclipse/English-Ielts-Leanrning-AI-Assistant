from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import Optional

class TranslationTask(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=lambda:  datetime.now(timezone.utc), nullable=False)
    updated_at: datetime = Field(default_factory=lambda:  datetime.now(timezone.utc), nullable=False)
    id: int
    task_id: UUID
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