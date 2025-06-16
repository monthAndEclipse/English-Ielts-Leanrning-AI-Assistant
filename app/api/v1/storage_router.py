# app/routers/storage.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.responses import StreamingResponse, Response
from typing import Optional, List
import io
from datetime import datetime

from app.services.storage_service import storage_service
from app.schemas.storage import (
    FileUploadRequest,
    FileUploadResponse,
    FileInfo,
    FileListResponse,
    FileDeleteRequest,
    FileDeleteResponse,
    PresignedUrlResponse,
    FileDownloadResponse,
    StorageStatsResponse,
    ApiResponse,
    FileUploadFromUrlRequest,
    PresignedUploadUrlRequest,
    PresignedDownloadUrlRequest,
    FileCopyRequest
)
from app.services.supabase.auth.supabase_auth import get_mock_user as get_current_user
from app.exceptions import StorageOperationException
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="/storage",
    tags=["Storage"],
    responses={404: {"description": "Not found"}},
)


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
        file: UploadFile = File(...),
        file_type: str = "files",
        user_id: str = Depends(get_current_user)
):
    """
    上传文件

    - **file**: 要上传的文件
    - **file_type**: 文件分类 (files, avatar, docs等)
    """
    try:
        # 读取文件数据
        file_data = await file.read()

        # 调用服务层上传文件
        result = await storage_service.upload_file(
            user_id=user_id,
            filename=file.filename,
            file_data=file_data,
            content_type=file.content_type,
            file_type=file_type
        )

        return result

    except StorageOperationException as e:
        logger.error(f"Storage operation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during file upload: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/upload-from-url", response_model=FileUploadResponse)
async def upload_file_from_url(
        request: FileUploadFromUrlRequest,
        user_id: str = Depends(get_current_user)
):
    """
    从URL上传文件

    - **url**: 源文件URL
    - **filename**: 文件名（可选，不提供则从URL推断）
    - **content_type**: 文件MIME类型（可选）
    - **file_type**: 文件分类
    - **metadata**: 文件元数据
    """
    try:
        result = await storage_service.upload_from_url(
            user_id=user_id,
            url=request.url,
            filename=request.filename,
            content_type=request.content_type,
            file_type=request.file_type,
            metadata=request.metadata
        )

        return result

    except StorageOperationException as e:
        logger.error(f"Storage operation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during URL upload: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/download/{file_path:path}")
async def download_file(
        file_path: str,
        user_id: str = Depends(get_current_user)
):
    """
    下载文件

    - **file_path**: 文件路径
    """
    try:
        # 获取文件数据
        file_data = await storage_service.download_file(user_id, file_path)

        # 获取文件信息
        file_info = await storage_service.get_file_info(user_id, file_path)

        # 创建流式响应
        def generate():
            yield file_data

        return StreamingResponse(
            io.BytesIO(file_data),
            media_type=file_info.content_type,
            headers={
                "Content-Disposition": f"attachment; filename={file_info.filename}",
                "Content-Length": str(len(file_data))
            }
        )

    except StorageOperationException as e:
        logger.error(f"Storage operation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during file download: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/info/{file_path:path}", response_model=FileInfo)
async def get_file_info(
        file_path: str,
        user_id: str = Depends(get_current_user)
):
    """
    获取文件信息

    - **file_path**: 文件路径
    """
    try:
        file_info = await storage_service.get_file_info(user_id, file_path)
        return file_info

    except StorageOperationException as e:
        logger.error(f"Storage operation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error getting file info: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/delete/{file_path:path}", response_model=ApiResponse)
async def delete_file(
        file_path: str,
        user_id: str = Depends(get_current_user)
):
    """
    删除单个文件

    - **file_path**: 文件路径
    """
    try:
        success = await storage_service.delete_file(user_id, file_path)

        if success:
            return ApiResponse(
                success=True,
                message="File deleted successfully",
                data={"file_path": file_path}
            )
        else:
            return ApiResponse(
                success=False,
                message="File deletion failed",
                data={"file_path": file_path}
            )

    except StorageOperationException as e:
        logger.error(f"Storage operation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during file deletion: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/delete-batch", response_model=FileDeleteResponse)
async def delete_files_batch(
        request: FileDeleteRequest,
        user_id: str = Depends(get_current_user)
):
    """
    批量删除文件

    - **file_paths**: 要删除的文件路径列表
    """
    try:
        results = await storage_service.delete_files(user_id, request.file_paths)

        deleted_files = [path for path, success in results.items() if success]
        failed_files = [
            {"file_path": path, "reason": "Deletion failed"}
            for path, success in results.items() if not success
        ]

        return FileDeleteResponse(
            deleted_files=deleted_files,
            failed_files=failed_files
        )

    except StorageOperationException as e:
        logger.error(f"Storage operation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during batch deletion: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# @router.get("/list", response_model=FileListResponse)
async def list_files(
        file_type: Optional[str] = None,
        limit: int = 100,
        start_after: Optional[str] = None,
        user_id: str = Depends(get_current_user)
):
    """
    列出用户文件

    - **file_type**: 文件类型过滤（可选）
    - **limit**: 返回数量限制
    - **start_after**: 起始位置（用于分页）
    """
    try:
        # 参数验证
        if limit > 100:
            limit = 100
        if limit < 1:
            limit = 1

        result = await storage_service.list_files(
            user_id=user_id,
            file_type=file_type,
            limit=limit,
            start_after=start_after
        )

        return result

    except StorageOperationException as e:
        logger.error(f"Storage operation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error listing files: {e}")
        logger.exception("Unexpected error")
        raise HTTPException(status_code=500, detail="Internal server error")


# @router.post("/copy", response_model=FileInfo)
async def copy_file(
        request: FileCopyRequest,
        user_id: str = Depends(get_current_user)
):
    """
    复制文件

    - **source_path**: 源文件路径
    - **target_path**: 目标文件路径
    - **overwrite**: 是否覆盖已存在的文件
    """
    try:
        # 从目标路径提取文件名
        target_filename = request.target_path.split('/')[-1]

        file_info = await storage_service.copy_file(
            user_id=user_id,
            source_path=request.source_path,
            target_filename=target_filename,
            file_type="files"
        )

        return file_info

    except StorageOperationException as e:
        logger.error(f"Storage operation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error copying file: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/presigned-upload-url", response_model=PresignedUrlResponse)
async def generate_presigned_upload_url(
        request: PresignedUploadUrlRequest,
        user_id: str = Depends(get_current_user)
):
    """
    生成预签名上传URL
    - **filename**: 文件名
    - **content_type**: 文件MIME类型（可选）
    - **file_type**: 文件分类
    - **expire_seconds**: 过期时间（秒）
    """
    try:
        result = await storage_service.generate_presigned_upload_url(
            user_id=user_id,
            filename=request.filename,
            content_type=request.content_type,
            file_type=request.file_type,
            expire_seconds=request.expire_seconds
        )

        return result

    except StorageOperationException as e:
        logger.error(f"Storage operation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error generating presigned upload URL: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/presigned-download-url", response_model=FileDownloadResponse)
async def generate_presigned_download_url(
        request: PresignedDownloadUrlRequest,
        user_id: str = Depends(get_current_user)
):
    """
    生成预签名下载URL

    - **file_path**: 文件路径
    - **expire_seconds**: 过期时间（秒）
    """
    try:
        result = await storage_service.generate_presigned_download_url(
            user_id=user_id,
            file_path=request.file_path,
            expire_seconds=request.expire_seconds
        )

        return result

    except StorageOperationException as e:
        logger.error(f"Storage operation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error generating presigned download URL: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/stats", response_model=StorageStatsResponse)
async def get_storage_stats(
        user_id: str = Depends(get_current_user)
):
    """
    获取用户存储统计信息
    """
    try:
        stats = await storage_service.get_user_storage_stats(user_id)
        return stats

    except StorageOperationException as e:
        logger.error(f"Storage operation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error getting storage stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/health")
async def health_check():
    """
    健康检查端点
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "service": "storage-service"
    }