from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from uuid import UUID

from app.db.database import get_session
from app.schemas.log import LogCreate, LogRead
from app.services.db.log_service import (
    create_log,
    get_log,
    list_logs,
    delete_log,
    update_log,
)

router = APIRouter(prefix="/logs", tags=["Logs"])

@router.post("/", response_model=LogRead)
def create(data: LogCreate, session: Session = Depends(get_session)):
    return create_log(session, data)

@router.get("/", response_model=list[LogRead])
def list_all(session: Session = Depends(get_session)):
    return list_logs(session)

@router.get("/{obj_id}", response_model=LogRead)
def get_one(obj_id: UUID, session: Session = Depends(get_session)):
    obj = get_log(session, obj_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    return obj

@router.put("/{obj_id}", response_model=LogRead)
def update_one(obj_id: UUID, data: LogCreate, session: Session = Depends(get_session)):
    updated = update_log(session, obj_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Not found")
    return updated

@router.delete("/{obj_id}")
def delete_one(obj_id: UUID, session: Session = Depends(get_session)):
    if not delete_log(session, obj_id):
        raise HTTPException(status_code=404, detail="Not found")
    return {"ok": True}