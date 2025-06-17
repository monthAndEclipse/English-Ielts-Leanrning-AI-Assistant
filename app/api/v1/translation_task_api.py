from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from uuid import UUID

from app.db.database import get_session
from app.schemas.translation_task import TranslationTaskCreate, TranslationTaskRead
from app.services.db.translation_task_service import (
    create_translation_task,
    get_translation_task,
    list_translation_tasks,
    delete_translation_task,
    update_translation_task,
)

router = APIRouter(prefix="/translation_tasks", tags=["TranslationTasks"])

@router.post("/", response_model=TranslationTaskRead)
def create(data: TranslationTaskCreate, session: Session = Depends(get_session)):
    return create_translation_task(session, data)

@router.get("/", response_model=list[TranslationTaskRead])
def list_all(session: Session = Depends(get_session)):
    return list_translation_tasks(session)

@router.get("/{obj_id}", response_model=TranslationTaskRead)
def get_one(obj_id: UUID, session: Session = Depends(get_session)):
    obj = get_translation_task(session, obj_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    return obj

@router.put("/{obj_id}", response_model=TranslationTaskRead)
def update_one(obj_id: UUID, data: TranslationTaskCreate, session: Session = Depends(get_session)):
    updated = update_translation_task(session, obj_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Not found")
    return updated

@router.delete("/{obj_id}")
def delete_one(obj_id: UUID, session: Session = Depends(get_session)):
    if not delete_translation_task(session, obj_id):
        raise HTTPException(status_code=404, detail="Not found")
    return {"ok": True}