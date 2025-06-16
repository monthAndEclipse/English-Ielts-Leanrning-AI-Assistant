from sqlmodel import Session, select
from app.db.models.log import Log
from app.schemas.log import LogCreate

def create_log(session: Session, data: LogCreate) -> Log:
    obj = Log.model_validate(data)
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return obj

def get_log(session: Session, obj_id):
    return session.get(Log, obj_id)

def list_logs(session: Session):
    return session.exec(select(Log)).all()

def delete_log(session: Session, obj_id):
    obj = session.get(Log, obj_id)
    if obj:
        session.delete(obj)
        session.commit()
        return True
    return False

def update_log(session: Session, obj_id, data: LogCreate):
    obj = session.get(Log, obj_id)
    if not obj:
        return None
    for key, value in data.dict().items():
        setattr(obj, key, value)
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return obj