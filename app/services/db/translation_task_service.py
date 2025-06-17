import os
from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.future import select
from sqlalchemy import update
from app.db.models.translation_task import  TranslationTask
from app.schemas.mq_schema import TranslationRequest
from sqlmodel import Session
import logging

logger = logging.getLogger(__name__)


def create_translation_task(session:Session ,payload: TranslationRequest) -> TranslationTask:
    """创建翻译任务记录"""
    try:
        task = TranslationTask(
            task_id=payload.uuid,
            event_type=payload.event_type,
            jwt_token=payload.jwt,
            file_path=payload.file_path,
            prompt_template=payload.prompt_template,
            target_language=payload.target_language,
            instruction=payload.instruction,
            start_time=datetime.fromisoformat(payload.start_time),
            status="pending"
        )
        session.add(task)
        session.commit()
        session.refresh(task)
        logger.info(f"创建翻译任务记录: {task.task_id}")
        return task
    except Exception as e:
        session.rollback()
        logger.error(f"创建翻译任务失败: {e}")
        raise

def update_translation_start(session:Session , task_id: str) -> bool:
    """更新翻译开始时间"""
    try:
        stmt = (
            update(TranslationTask)
            .where(TranslationTask.task_id == task_id)
            .values(
                translate_start_time=datetime.now(),
                status="processing"
            )
        )
        result = session.execute(stmt)
        session.commit()
        logger.info(f"更新翻译开始时间: {task_id}")
        return result.rowcount > 0
    except Exception as e:
        session.rollback()
        logger.error(f"更新翻译开始时间失败: {e}")
        return False


def update_translation_complete(
        session:Session,
        task_id: str,
        file_path: Optional[str] = None,
        error_message: Optional[str] = None
) -> bool:
    try:
        update_values = {
            "translation_end_time": datetime.now(),
            "status": "completed" if not error_message else "failed"
        }
        if file_path:
            update_values["file_path"] = file_path
        if error_message:
            update_values["error_message"] = error_message
        stmt = (
            update(TranslationTask)
            .where(TranslationTask.task_id == task_id)
            .values(**update_values)
        )
        result = session.execute(stmt)
        session.commit()
        logger.info(f"更新翻译完成状态: {task_id}, 状态: {update_values['status']}")
        return result.rowcount > 0
    except Exception as e:
        session.rollback()
        logger.error(f"更新翻译完成状态失败: {e}")
        return False
