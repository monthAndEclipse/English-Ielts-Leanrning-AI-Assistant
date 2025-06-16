import asyncio
import uuid
from typing import Optional, List, Dict, Union, BinaryIO
from datetime import datetime, timedelta
from io import BytesIO
import httpx
from minio import Minio
from minio.error import S3Error
from app.core.cloud_storage_base  import BaseStorageProvider
from app.schemas.storage import FileInfo, PresignedUrlResponse, FileDownloadResponse
from app.exceptions import (
    StorageOperationException,
    FileNotFoundException,
    BucketNotFoundException
)
from app.utils.logger import get_logger

logger = get_logger(__name__)


class MinIOStorageProvider(BaseStorageProvider):
    """MinIO 存储提供商实现"""

    def __init__(self, config: dict):
        super().__init__(config)
        self.bucket_name = config.get("bucket_name", "cloud-storage")

    async def initialize(self) -> None:
        """初始化 MinIO 客户端"""
        try:
            logger.info(f"self.config:{self.config}")
            self.client = Minio(
                endpoint=self.config["endpoint"],
                access_key=self.config["access_key"],
                secret_key=self.config["secret_key"],
                secure=self.config.get("secure", False)
            )
            # 检查并创建存储桶
            if not await self.bucket_exists(self.bucket_name):
                await self.create_bucket(self.bucket_name)

            logger.info(f"MinIO client initialized successfully. Bucket: {self.bucket_name}")

        except Exception as e:
            logger.error(f"Failed to initialize MinIO client: {str(e)}")
            raise StorageOperationException("initialize", str(e))

    async def upload_file(
            self,
            file_path: str,
            file_data: Union[bytes, BinaryIO, BytesIO],
            content_type: Optional[str] = None,
            metadata: Optional[Dict[str, str]] = None
    ) -> FileInfo:
        """上传文件到 MinIO"""
        try:
            # 处理文件数据
            if isinstance(file_data, bytes):
                file_stream = BytesIO(file_data)
                file_size = len(file_data)
            else:
                file_stream = file_data
                file_stream.seek(0, 2)  # 移动到文件末尾
                file_size = file_stream.tell()
                file_stream.seek(0)  # 重置到开头

            # 执行上传
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.put_object(
                    bucket_name=self.bucket_name,
                    object_name=file_path,
                    data=file_stream,
                    length=file_size,
                    content_type=content_type,
                    metadata=metadata or {}
                )
            )

            # 构造文件信息
            file_info = FileInfo(
                file_id=str(uuid.uuid4()),
                filename=file_path.split("/")[-1],
                file_path=file_path,
                content_type=content_type or "application/octet-stream",
                file_size=file_size,
                etag=result.etag,
                upload_time=datetime.utcnow(),
                last_modified=datetime.utcnow(),
                user_id=metadata.get("user_id", "") if metadata else "",
                tags=metadata or {}
            )

            logger.info(f"File uploaded successfully: {file_path}")
            return file_info

        except S3Error as e:
            logger.error(f"MinIO S3 error during upload: {str(e)}")
            raise StorageOperationException("upload", str(e))
        except Exception as e:
            logger.error(f"Unexpected error during upload: {str(e)}")
            raise StorageOperationException("upload", str(e))

    async def upload_from_url(
            self,
            file_path: str,
            url: str,
            content_type: Optional[str] = None,
            metadata: Optional[Dict[str, str]] = None
    ) -> FileInfo:
        """从URL上传文件"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                response.raise_for_status()

                if not content_type:
                    content_type = response.headers.get("content-type", "application/octet-stream")

                return await self.upload_file(
                    file_path=file_path,
                    file_data=response.content,
                    content_type=content_type,
                    metadata=metadata
                )

        except httpx.RequestError as e:
            logger.error(f"Failed to fetch file from URL {url}: {str(e)}")
            raise StorageOperationException("upload_from_url", f"Failed to fetch from URL: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during URL upload: {str(e)}")
            raise StorageOperationException("upload_from_url", str(e))

    async def download_file(self, file_path: str) -> bytes:
        """下载文件数据"""
        try:
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.get_object(self.bucket_name, file_path)
            )

            data = response.read()
            response.close()
            response.release_conn()

            logger.info(f"File downloaded successfully: {file_path}")
            return data

        except S3Error as e:
            logger.error(f"MinIO S3 error during download: {str(e)}")
            raise StorageOperationException("download", str(e))
        except Exception as e:
            logger.error(f"Unexpected error during download: {str(e)}")
            raise StorageOperationException("download", str(e))

    async def get_file_info(self, file_path: str) -> FileInfo:
        """获取文件信息"""
        try:
            stat = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.stat_object(self.bucket_name, file_path)
            )

            return FileInfo(
                filename=file_path.split("/")[-1],
                file_path=file_path,
                content_type=stat.content_type or "application/octet-stream",
                file_size=stat.size,
                etag=stat.etag,
                upload_time=stat.last_modified,
                last_modified=stat.last_modified,
                user_id=stat.metadata.get("user_id", "") if stat.metadata else "",
                tags=stat.metadata or {}
            )

        except S3Error as e:
            logger.error(f"MinIO S3 error getting file info: {str(e)}")
            raise StorageOperationException("get_file_info", str(e))
        except Exception as e:
            logger.error(f"Unexpected error getting file info: {str(e)}")
            raise StorageOperationException("get_file_info", str(e))

    async def delete_file(self, file_path: str) -> bool:
        """删除单个文件"""
        try:
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.remove_object(self.bucket_name, file_path)
            )

            logger.info(f"File deleted successfully: {file_path}")
            return True

        except S3Error as e:
            logger.error(f"MinIO S3 error during deletion: {str(e)}")
            raise StorageOperationException("delete", str(e))
        except Exception as e:
            logger.error(f"Unexpected error during deletion: {str(e)}")
            raise StorageOperationException("delete", str(e))

    async def delete_files(self, file_paths: List[str]) -> Dict[str, bool]:
        """批量删除文件"""
        results = {}

        for file_path in file_paths:
            try:
                success = await self.delete_file(file_path)
                results[file_path] = success
            except Exception:
                results[file_path] = False

        return results

    async def list_files(
            self,
            prefix: Optional[str] = None,
            limit: int = 100,
            start_after: Optional[str] = None
    ) -> List[FileInfo]:
        """列出文件"""
        try:
            objects =  list(self.client.list_objects(
                    bucket_name=self.bucket_name,
                    prefix=prefix,
                    start_after=start_after))

            files = []
            for obj in objects[:limit]:
                logger.info(f"obj:{obj.last_modified}")
                file_info = FileInfo(
                    filename=obj.object_name.split("/")[-1],
                    file_path=obj.object_name,
                    content_type="application/octet-stream",  # MinIO list不返回content_type
                    file_size=int(obj.size) if obj.size is not None else 0,
                    etag=obj.etag,
                    upload_time=obj.last_modified,
                    last_modified=obj.last_modified,
                    user_id="",  # 需要从详细信息中获取
                    tags={}
                )
                files.append(file_info)

            logger.info(f"Listed {len(files)} files with prefix: {prefix}")
            return files

        except S3Error as e:
            logger.error(f"MinIO S3 error listing files: {str(e)}")
            raise StorageOperationException("list_files", str(e))
        except Exception as e:
            logger.error(f"Unexpected error listing files: {str(e)}")
            raise StorageOperationException("list_files", str(e))

    async def file_exists(self, file_path: str) -> bool:
        """检查文件是否存在"""
        try:
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.stat_object(self.bucket_name, file_path)
            )
            return True
        except Exception as e:
            logger.error(f"Error checking file existence: {str(e)}")
            return False

    async def copy_file(
            self,
            source_path: str,
            target_path: str,
            metadata: Optional[Dict[str, str]] = None
    ) -> FileInfo:
        """复制文件"""
        try:
            from minio.commonconfig import CopySource

            copy_source = CopySource(self.bucket_name, source_path)

            result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.copy_object(
                    bucket_name=self.bucket_name,
                    object_name=target_path,
                    source=copy_source,
                    metadata=metadata
                )
            )

            # 获取复制后的文件信息
            return await self.get_file_info(target_path)

        except S3Error as e:
            logger.error(f"MinIO S3 error during copy: {str(e)}")
            raise StorageOperationException("copy", str(e))
        except Exception as e:
            logger.error(f"Unexpected error during copy: {str(e)}")
            raise StorageOperationException("copy", str(e))


    async def generate_presigned_upload_url(
            self,
            file_path: str,
            content_type: Optional[str] = None,
            expire_seconds: int = 3600
    ) -> PresignedUrlResponse:
        """生成预签名上传URL"""
        try:
            expires = timedelta(seconds=expire_seconds)

            # 构建额外的条件
            conditions = {}
            if content_type:
                conditions["Content-Type"] = content_type

            upload_url = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.presigned_put_object(
                    bucket_name=self.bucket_name,
                    object_name=file_path,
                    expires=expires
                )
            )

            return PresignedUrlResponse(
                upload_url=upload_url,
                file_path=file_path,
                expire_time=datetime.utcnow() + expires,
                fields=conditions
            )

        except S3Error as e:
            logger.error(f"MinIO S3 error generating presigned upload URL: {str(e)}")
            raise StorageOperationException("generate_presigned_upload_url", str(e))
        except Exception as e:
            logger.error(f"Unexpected error generating presigned upload URL: {str(e)}")
            raise StorageOperationException("generate_presigned_upload_url", str(e))

    async def generate_presigned_download_url(
            self,
            file_path: str,
            expire_seconds: int = 3600
    ) -> FileDownloadResponse:
        """生成预签名下载URL"""
        try:
            # 先获取文件信息
            file_info = await self.get_file_info(file_path)

            expires = timedelta(seconds=expire_seconds)

            download_url = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.presigned_get_object(
                    bucket_name=self.bucket_name,
                    object_name=file_path,
                    expires=expires
                )
            )

            return FileDownloadResponse(
                download_url=download_url,
                filename=file_info.filename,
                content_type=file_info.content_type,
                file_size=file_info.file_size,
                expire_time=datetime.utcnow() + expires
            )

        except S3Error as e:
            logger.error(f"MinIO S3 error generating presigned download URL: {str(e)}")
            raise StorageOperationException("generate_presigned_download_url", str(e))
        except Exception as e:
            logger.error(f"Unexpected error generating presigned download URL: {str(e)}")
            raise StorageOperationException("generate_presigned_download_url", str(e))

    async def create_bucket(self, bucket_name: str) -> bool:
        """创建存储桶"""
        try:
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.make_bucket(bucket_name)
            )

            logger.info(f"Bucket created successfully: {bucket_name}")
            return True

        except S3Error as e:
            if "BucketAlreadyExists" in str(e):
                logger.info(f"Bucket already exists: {bucket_name}")
                return True
            logger.error(f"MinIO S3 error creating bucket: {str(e)}")
            raise StorageOperationException("create_bucket", str(e))
        except Exception as e:
            logger.error(f"Unexpected error creating bucket: {str(e)}")
            raise StorageOperationException("create_bucket", str(e))

    async def bucket_exists(self, bucket_name: str) -> bool:
        """检查存储桶是否存在"""
        try:
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.bucket_exists(bucket_name)
            )
            return result
        except Exception as e:
            logger.error(f"Error checking bucket existence: {str(e)}")
            return False

    async def get_storage_stats(self, prefix: Optional[str] = None) -> Dict[str, Union[int, float]]:
        """获取存储统计信息"""
        try:
            objects = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: list(self.client.list_objects(
                    bucket_name=self.bucket_name,
                    prefix=prefix,
                    recursive=True
                ))
            )

            total_files = len(objects)
            total_size = sum(obj.size for obj in objects)

            return {
                "total_files": total_files,
                "total_size": total_size,
                "used_quota": 0.0  # 需要配合配额系统计算
            }

        except S3Error as e:
            logger.error(f"MinIO S3 error getting storage stats: {str(e)}")
            raise StorageOperationException("get_storage_stats", str(e))
        except Exception as e:
            logger.error(f"Unexpected error getting storage stats: {str(e)}")
            raise StorageOperationException("get_storage_stats", str(e))