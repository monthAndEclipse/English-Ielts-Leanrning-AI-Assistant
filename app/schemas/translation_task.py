from sqlmodel import SQLModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class TranslationTaskCreate(SQLModel):
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

class TranslationTaskRead(TranslationTaskCreate):
    id: UUID
    created_at: datetime
    updated_at: datetime