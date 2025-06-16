from typing import Optional, List, Dict, Union, BinaryIO
from datetime import datetime
from io import BytesIO
import os
import uuid
import mimetypes
import httpx
from urllib.parse import urlparse

from app.factory.storage_factory import get_default_storage
from app.schemas.storage import (
    FileInfo,
    PresignedUrlResponse,
    FileDownloadResponse,
    FileUploadRequest,
    FileUploadResponse,
    FileListResponse,
    StorageStatsResponse
)
from app.exceptions import StorageOperationException
from app.utils.logger import get_logger

logger = get_logger(__name__)


class StorageService:
    """存储服务层，封装存储操作的业务逻辑"""

    def __init__(self):
        self.storage_provider = None

    async def _get_storage_provider(self):
        """获取存储提供商实例"""
        if self.storage_provider is None:
            self.storage_provider = await get_default_storage()
        return self.storage_provider

    def _generate_file_path(self, user_id: str, filename: str, file_type: str = "files") -> str:
        """
        生成文件存储路径
        格式: {user_id}/{file_type}/{date}/{uuid}_{filename}

        Args:
            user_id: 用户ID
            filename: 原始文件名
            file_type: 文件类型分类 (files, avatar, docs等)

        Returns:
            str: 生成的文件路径
        """
        # 获取当前日期
        date_str = datetime.now().strftime("%Y%m%d")

        # 生成UUID前缀避免文件名冲突
        file_uuid = str(uuid.uuid4())[:8]

        # 构建文件路径
        file_path = f"{user_id}/{file_type}/{date_str}/{file_uuid}_{filename}"

        return file_path

    def _get_content_type(self, filename: str, content_type: Optional[str] = None) -> str:
        """
        获取文件的MIME类型

        Args:
            filename: 文件名
            content_type: 指定的内容类型

        Returns:
            str: MIME类型
        """
        if content_type:
            return content_type

        # 根据文件扩展名推断MIME类型
        mime_type, _ = mimetypes.guess_type(filename)
        return mime_type or "application/octet-stream"

    async def upload_file(
            self,
            user_id: str,
            filename: str,
            file_data: Union[bytes, BinaryIO, BytesIO],
            content_type: Optional[str] = None,
            file_type: str = "files",
            metadata: Optional[Dict[str, str]] = None
    ) -> FileUploadResponse:
        """
        上传文件

        Args:
            user_id: 用户ID
            filename: 文件名
            file_data: 文件数据
            content_type: 文件类型
            file_type: 文件分类
            metadata: 文件元数据

        Returns:
            FileUploadResponse: 上传结果
        """
        try:
            storage = await self._get_storage_provider()

            # 生成文件路径
            file_path = self._generate_file_path(user_id, filename, file_type)

            # 获取内容类型
            content_type = self._get_content_type(filename, content_type)

            # 添加用户信息到元数据
            if metadata is None:
                metadata = {}
            metadata.update({
                "user_id": user_id,
                "original_filename": filename,
                "file_type": file_type,
                "upload_time": datetime.now().isoformat()
            })

            # 执行上传
            file_info = await storage.upload_file(
                file_path=file_path,
                file_data=file_data,
                content_type=content_type,
                metadata=metadata
            )

            logger.info(f"File uploaded successfully: {file_path} for user {user_id}")

            return FileUploadResponse(
                success=True,
                message="File uploaded successfully",
                file_info=file_info
            )

        except Exception as e:
            logger.error(f"Failed to upload file for user {user_id}: {str(e)}")
            raise StorageOperationException("upload", f"Failed to upload file: {str(e)}")

    async def upload_from_url(
            self,
            user_id: str,
            url: str,
            filename: Optional[str] = None,
            content_type: Optional[str] = None,
            file_type: str = "files",
            metadata: Optional[Dict[str, str]] = None
    ) -> FileUploadResponse:
        """
        从URL上传文件

        Args:
            user_id: 用户ID
            url: 源文件URL
            filename: 文件名，如果不提供则从URL推断
            content_type: 文件类型
            file_type: 文件分类
            metadata: 文件元数据

        Returns:
            FileUploadResponse: 上传结果
        """
        try:
            storage = await self._get_storage_provider()

            # 如果没有提供文件名，从URL推断
            if not filename:
                parsed_url = urlparse(url)
                filename = os.path.basename(parsed_url.path) or f"file_{uuid.uuid4().hex[:8]}"

            # 生成文件路径
            file_path = self._generate_file_path(user_id, filename, file_type)

            # 获取内容类型
            content_type = self._get_content_type(filename, content_type)

            # 添加用户信息到元数据
            if metadata is None:
                metadata = {}
            metadata.update({
                "user_id": user_id,
                "source_url": url,
                "original_filename": filename,
                "file_type": file_type,
                "upload_time": datetime.now().isoformat()
            })

            # 执行上传
            file_info = await storage.upload_from_url(
                file_path=file_path,
                url=url,
                content_type=content_type,
                metadata=metadata
            )

            logger.info(f"File uploaded from URL successfully: {file_path} for user {user_id}")

            return FileUploadResponse(
                success=True,
                message="File uploaded from URL successfully",
                file_info=file_info
            )

        except Exception as e:
            logger.error(f"Failed to upload file from URL for user {user_id}: {str(e)}")
            raise StorageOperationException("upload_from_url", f"Failed to upload file from URL: {str(e)}")

    async def download_file(self, user_id: str, file_path: str) -> bytes:
        """
        下载文件数据

        Args:
            user_id: 用户ID
            file_path: 文件路径

        Returns:
            bytes: 文件数据
        """
        try:
            # 验证用户权限（文件路径必须以用户ID开头）
            if not file_path.startswith(f"{user_id}/"):
                raise StorageOperationException(
                    "download",
                    "Access denied: You can only access your own files"
                )

            storage = await self._get_storage_provider()
            file_data = await storage.download_file(file_path)

            logger.info(f"File downloaded successfully: {file_path} for user {user_id}")
            return file_data

        except Exception as e:
            logger.error(f"Failed to download file for user {user_id}: {str(e)}")
            raise StorageOperationException("download", f"Failed to download file: {str(e)}")

    async def get_file_info(self, user_id: str, file_path: str) -> FileInfo:
        """
        获取文件信息
        Args:
            user_id: 用户ID
            file_path: 文件路径
        Returns:
            FileInfo: 文件信息
        """
        try:
            # 验证用户权限
            if not file_path.startswith(f"{user_id}/"):
                raise StorageOperationException(
                    "get_file_info",
                    "Access denied: You can only access your own files"
                )
            storage = await self._get_storage_provider()
            file_info = await storage.get_file_info(file_path)
            return file_info

        except Exception as e:
            logger.error(f"Failed to get file info for user {user_id}: {str(e)}")
            raise StorageOperationException("get_file_info", f"Failed to get file info: {str(e)}")

    async def delete_file(self, user_id: str, file_path: str) -> bool:
        """
        删除文件

        Args:
            user_id: 用户ID
            file_path: 文件路径

        Returns:
            bool: 是否删除成功
        """
        try:
            # 验证用户权限
            if not file_path.startswith(f"{user_id}/"):
                raise StorageOperationException(
                    "delete_file",
                    "Access denied: You can only delete your own files"
                )

            storage = await self._get_storage_provider()
            success = await storage.delete_file(file_path)

            if success:
                logger.info(f"File deleted successfully: {file_path} for user {user_id}")
            else:
                logger.warning(f"File deletion failed: {file_path} for user {user_id}")

            return success

        except Exception as e:
            logger.error(f"Failed to delete file for user {user_id}: {str(e)}")
            raise StorageOperationException("delete_file", f"Failed to delete file: {str(e)}")

    async def delete_files(self, user_id: str, file_paths: List[str]) -> Dict[str, bool]:
        """
        批量删除文件

        Args:
            user_id: 用户ID
            file_paths: 文件路径列表

        Returns:
            Dict[str, bool]: 删除结果
        """
        try:
            # 验证用户权限
            for file_path in file_paths:
                if not file_path.startswith(f"{user_id}/"):
                    raise StorageOperationException(
                        "delete_files",
                        f"Access denied: You can only delete your own files. Invalid path: {file_path}"
                    )

            storage = await self._get_storage_provider()
            results = await storage.delete_files(file_paths)

            success_count = sum(1 for success in results.values() if success)
            logger.info(f"Batch delete completed: {success_count}/{len(file_paths)} files deleted for user {user_id}")

            return results

        except Exception as e:
            logger.error(f"Failed to delete files for user {user_id}: {str(e)}")
            raise StorageOperationException("delete_files", f"Failed to delete files: {str(e)}")

    async def list_files(
            self,
            user_id: str,
            file_type: Optional[str] = None,
            limit: int = 100,
            start_after: Optional[str] = None
    ) -> FileListResponse:
        """
        列出用户文件

        Args:
            user_id: 用户ID
            file_type: 文件类型过滤
            limit: 返回数量限制
            start_after: 起始位置

        Returns:
            FileListResponse: 文件列表
        """
        try:
            storage = await self._get_storage_provider()

            # 构建前缀
            prefix = f"{user_id}/"
            if file_type:
                prefix = f"{user_id}/{file_type}/"

            files = await storage.list_files(
                prefix=prefix,
                limit=limit,
                start_after=start_after
            )

            logger.info(f"Listed {len(files)} files for user {user_id}")

            return FileListResponse(
                files=files,
                total=len(files),
                has_more=len(files) == limit
            )

        except Exception as e:
            logger.error(f"Failed to list files for user {user_id}: {str(e)}")
            raise StorageOperationException("list_files", f"Failed to list files: {str(e)}")

    async def copy_file(
            self,
            user_id: str,
            source_path: str,
            target_filename: str,
            file_type: str = "files",
            metadata: Optional[Dict[str, str]] = None
    ) -> FileInfo:
        """
        复制文件

        Args:
            user_id: 用户ID
            source_path: 源文件路径
            target_filename: 目标文件名
            file_type: 文件类型
            metadata: 元数据

        Returns:
            FileInfo: 新文件信息
        """
        try:
            # 验证用户权限
            if not source_path.startswith(f"{user_id}/"):
                raise StorageOperationException(
                    "copy_file",
                    "Access denied: You can only copy your own files"
                )

            storage = await self._get_storage_provider()

            # 生成目标路径
            target_path = self._generate_file_path(user_id, target_filename, file_type)

            # 添加元数据
            if metadata is None:
                metadata = {}
            metadata.update({
                "user_id": user_id,
                "source_path": source_path,
                "copy_time": datetime.now().isoformat()
            })

            file_info = await storage.copy_file(
                source_path=source_path,
                target_path=target_path,
                metadata=metadata
            )

            logger.info(f"File copied successfully: {source_path} -> {target_path} for user {user_id}")
            return file_info

        except Exception as e:
            logger.error(f"Failed to copy file for user {user_id}: {str(e)}")
            raise StorageOperationException("copy_file", f"Failed to copy file: {str(e)}")

    """
    注意：这个url并不能实现大小和类型控制，只能通过nginx做一层限制
    """
    async def generate_presigned_upload_url(
            self,
            user_id: str,
            filename: str,
            content_type: Optional[str] = None,
            file_type: str = "files",
            expire_seconds: int = 3600
    ) -> PresignedUrlResponse:
        """
        生成预签名上传URL

        Args:
            user_id: 用户ID
            filename: 文件名
            content_type: 文件类型
            file_type: 文件分类
            expire_seconds: 过期时间
        Returns:
            PresignedUrlResponse: 预签名URL信息
        """
        try:
            storage = await self._get_storage_provider()
            # 生成文件路径
            file_path = self._generate_file_path(user_id, filename, file_type)
            # 获取内容类型
            content_type = self._get_content_type(filename, content_type)
            presigned_url = await storage.generate_presigned_upload_url(
                file_path=file_path,
                content_type=content_type,
                expire_seconds=expire_seconds
            )

            logger.info(f"Generated presigned upload URL for user {user_id}: {file_path}")
            return presigned_url

        except Exception as e:
            logger.error(f"Failed to generate presigned upload URL for user {user_id}: {str(e)}")
            raise StorageOperationException("generate_presigned_upload_url",
                                            f"Failed to generate presigned upload URL: {str(e)}")

    async def generate_presigned_download_url(
            self,
            user_id: str,
            file_path: str,
            expire_seconds: int = 3600
    ) -> FileDownloadResponse:
        """
        生成预签名下载URL

        Args:
            user_id: 用户ID
            file_path: 文件路径
            expire_seconds: 过期时间

        Returns:
            FileDownloadResponse: 下载URL信息
        """
        try:
            # 验证用户权限
            if not file_path.startswith(f"{user_id}/"):
                raise StorageOperationException(
                    "generate_presigned_download_url",
                    "Access denied: You can only access your own files"
                )

            storage = await self._get_storage_provider()

            download_url = await storage.generate_presigned_download_url(
                file_path=file_path,
                expire_seconds=expire_seconds
            )

            logger.info(f"Generated presigned download URL for user {user_id}: {file_path}")
            return download_url

        except Exception as e:
            logger.error(f"Failed to generate presigned download URL for user {user_id}: {str(e)}")
            raise StorageOperationException("generate_presigned_download_url",
                                            f"Failed to generate presigned download URL: {str(e)}")

    async def get_user_storage_stats(self, user_id: str) -> StorageStatsResponse:
        """
        获取用户存储统计信息

        Args:
            user_id: 用户ID

        Returns:
            StorageStatsResponse: 存储统计信息
        """
        try:
            storage = await self._get_storage_provider()

            # 获取用户前缀的统计信息
            stats = await storage.get_storage_stats(prefix=f"{user_id}/")

            return StorageStatsResponse(
                total_files=stats.get("total_files", 0),
                total_size=stats.get("total_size", 0),
            )

        except Exception as e:
            logger.error(f"Failed to get storage stats for user {user_id}: {str(e)}")
            raise StorageOperationException("get_storage_stats", f"Failed to get storage stats: {str(e)}")


# 创建服务实例
storage_service = StorageService()