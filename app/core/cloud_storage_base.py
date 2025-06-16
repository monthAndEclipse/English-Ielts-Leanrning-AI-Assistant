from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Union, BinaryIO
from datetime import datetime, timedelta
from io import BytesIO
from ..schemas.storage import FileInfo, PresignedUrlResponse, FileDownloadResponse

class BaseStorageProvider(ABC):
    """存储提供商基础接口"""

    def __init__(self, config: dict):
        self.config = config
        self.client = None

    @abstractmethod
    async def initialize(self) -> None:
        """初始化存储客户端"""
        pass

    @abstractmethod
    async def upload_file(
            self,
            file_path: str,
            file_data: Union[bytes, BinaryIO, BytesIO],
            content_type: Optional[str] = None,
            metadata: Optional[Dict[str, str]] = None
    ) -> FileInfo:
        """
        上传文件
        Args:
            file_path: 存储路径
            file_data: 文件数据
            content_type: 文件类型
            metadata: 文件元数据
        Returns:
            FileInfo: 文件信息
        """
        pass

    @abstractmethod
    async def upload_from_url(
            self,
            file_path: str,
            url: str,
            content_type: Optional[str] = None,
            metadata: Optional[Dict[str, str]] = None
    ) -> FileInfo:
        """
        从URL上传文件
        Args:
            file_path: 存储路径
            url: 源文件URL
            content_type: 文件类型
            metadata: 文件元数据
        Returns:
            FileInfo: 文件信息
        """
        pass

    @abstractmethod
    async def download_file(self, file_path: str) -> bytes:
        """
        下载文件数据
        Args:
            file_path: 文件路径
        Returns:
            bytes: 文件数据
        """
        pass

    @abstractmethod
    async def get_file_info(self, file_path: str) -> FileInfo:
        """
        获取文件信息
        Args:
            file_path: 文件路径
        Returns:
            FileInfo: 文件信息
        """
        pass

    @abstractmethod
    async def delete_file(self, file_path: str) -> bool:
        """
        删除单个文件
        Args:
            file_path: 文件路径
        Returns:
            bool: 是否删除成功
        """
        pass

    @abstractmethod
    async def delete_files(self, file_paths: List[str]) -> Dict[str, bool]:
        """
        批量删除文件
        Args:
            file_paths: 文件路径列表
        Returns:
            Dict[str, bool]: 文件路径 -> 是否删除成功的映射
        """
        pass

    @abstractmethod
    async def list_files(
            self,
            prefix: Optional[str] = None,
            limit: int = 100,
            start_after: Optional[str] = None
    ) -> List[FileInfo]:
        """
        列出文件
        Args:
            prefix: 路径前缀
            limit: 返回数量限制
            start_after: 起始位置

        Returns:
            List[FileInfo]: 文件信息列表
        """
        pass

    @abstractmethod
    async def file_exists(self, file_path: str) -> bool:
        """
        检查文件是否存在
        Args:
            file_path: 文件路径
        Returns:
            bool: 文件是否存在
        """
        pass

    @abstractmethod
    async def copy_file(
            self,
            source_path: str,
            target_path: str,
            metadata: Optional[Dict[str, str]] = None
    ) -> FileInfo:
        """
        复制文件
        Args:
            source_path: 源文件路径
            target_path: 目标文件路径
            metadata: 新文件元数据
        Returns:
            FileInfo: 新文件信息
        """
        pass

    @abstractmethod
    async def generate_presigned_upload_url(
            self,
            file_path: str,
            content_type: Optional[str] = None,
            expire_seconds: int = 3600
    ) -> PresignedUrlResponse:
        """
        生成预签名上传URL
        Args:
            file_path: 文件路径
            content_type: 文件类型
            expire_seconds: 过期时间(秒)
        Returns:
            PresignedUrlResponse: 预签名URL信息
        """
        pass

    @abstractmethod
    async def generate_presigned_download_url(
            self,
            file_path: str,
            expire_seconds: int = 3600
    ) -> FileDownloadResponse:
        """
        生成预签名下载URL
        Args:
            file_path: 文件路径
            expire_seconds: 过期时间(秒)
        Returns:
            FileDownloadResponse: 下载URL信息
        """
        pass

    @abstractmethod
    async def create_bucket(self, bucket_name: str) -> bool:
        """
        创建存储桶
        Args:
            bucket_name: 存储桶名称
        Returns:
            bool: 是否创建成功
        """
        pass

    @abstractmethod
    async def bucket_exists(self, bucket_name: str) -> bool:
        """
        检查存储桶是否存在
        Args:
            bucket_name: 存储桶名称
        Returns:
            bool: 存储桶是否存在
        """
        pass

    @abstractmethod
    async def get_storage_stats(self, prefix: Optional[str] = None) -> Dict[str, Union[int, float]]:
        """
        获取存储统计信息
        Args:
            prefix: 路径前缀
        Returns:
            Dict: 统计信息 (total_files, total_size, etc.)
        """
        pass