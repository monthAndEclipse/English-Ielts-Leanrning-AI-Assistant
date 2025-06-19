from datetime import datetime
from typing import Optional,Dict,Any
from sqlalchemy import update
from app.db.models.translation_task import  TranslationTask
from app.schemas.mq_schema import TranslationRequest
from sqlmodel import Session
import logging
from app.db.database import get_session
from app.schemas.translation_task import TaskStatus

logger = logging.getLogger(__name__)


def create_translation_task(payload: TranslationRequest) -> TranslationTask:
    """创建翻译任务记录"""
    with get_session() as session :
        task = TranslationTask(
            task_id=payload.uuid,
            event_type=payload.event_type,
            jwt_token=payload.jwt,
            file_path=payload.file_path,
            prompt_template=payload.prompt_template,
            target_language=payload.target_language,
            instruction=payload.instruction,
            start_time=datetime.fromisoformat(payload.start_time),
            status=TaskStatus.PENDING
        )
        session.add(task)
        session.commit()
        session.refresh(task)
        logger.info(f"创建翻译任务记录: {task.task_id}")
        return task


def update_translation_task_fields(
    task_id: str,
    fields_to_update: Dict[str, Any]
) -> bool:
    """
    Args:
        task_id (str): 要更新的任务ID
        fields_to_update (Dict[str, Any]): 要更新的字段和值，如 {"status": "COMPLETE", "file_path": "/path/to/file"}
    Returns:
        bool: 是否成功更新
    """
    with get_session() as session:
        try:
            # 自动更新时间
            fields_to_update["updated_at"] = datetime.now()

            stmt = (
                update(TranslationTask)
                .where(TranslationTask.task_id == task_id)
                .values(**fields_to_update)
            )
            result = session.execute(stmt)
            session.commit()
            logger.info(f"[更新任务] 成功更新 task_id={task_id}, 更新字段={list(fields_to_update.keys())}")
            return result.rowcount > 0
        except Exception as e:
            session.rollback()
            logger.error(f"[更新任务] 更新失败 task_id={task_id}: {e}")
            return False