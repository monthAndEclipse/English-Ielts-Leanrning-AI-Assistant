from pydantic_settings import BaseSettings
from pydantic import field_validator, model_validator, Field
from typing import Optional
from enum import Enum
from app.utils.consul_utils import get_config
import os

class StorageProvider(str, Enum):
    MINIO = "minio"
    # 未来可扩展：AWS_S3 = "aws_s3", GOOGLE_CLOUD = "google_cloud"
    @classmethod
    def from_str(cls, name: str) -> "StorageProvider":
        try:
            return cls(name.lower())
        except ValueError:
            raise ValueError(f"Invalid storage provider: {name}")

"""
统一配置，有些是os.getenv 有些是从consul获取的，统一在这里调整吧
不是和启动强关联的配置项，有些不敏感的可以存consul,有些敏感的直接os.getenv()
"""
class Settings(BaseSettings):
    # 应用配置
    app_name: str = "Cloud Storage Service"
    app_version: str = "1.0.0"
    debug: bool = False

    # 存储配置
    storage_provider: StorageProvider = StorageProvider.from_str(get_config("/default_storage_provider","minio"))


    # MinIO 配置
    minio_access_key: str = os.getenv("MINIO_ACCESS_KEY")
    minio_secret_key: str =  os.getenv("MINIO_SECRET_KEY")
    minio_endpoint: str = Field(default="placeholder")
    minio_secure: bool = Field(default=False)
    minio_bucket_name: str = Field(default="placeholder")

    # 文件配置
    max_file_size: int = Field(default=10485760)  # default 10MB
    # 预签名 URL 配置
    presigned_url_expire_seconds: int = Field(default=3600)  # 1小时
    allowed_file_types: list[str] = [
        "image/jpeg", "image/png", "image/gif", "image/webp",
        "application/pdf", "text/plain", "application/json",
        "video/mp4", "video/avi", "audio/mpeg", "audio/wav"
    ]


    def load_from_consul(self):
        """手动从 Consul 加载配置，延迟加载实现"""
        self.storage_provider = StorageProvider.from_str(get_config("/default_storage_provider", self.storage_provider))
        self.minio_endpoint = get_config("/minio_endpoint", self.minio_endpoint)
        self.minio_bucket_name = get_config("/minio_bucket_name", self.minio_bucket_name)

        raw_secure = get_config("/minio_secure", self.minio_secure)
        self.minio_secure = raw_secure.lower() in ("true", "1", "yes") if isinstance(raw_secure, str) else bool(raw_secure)

        self.max_file_size = int(get_config("/max_file_size", str(self.max_file_size)))
        self.presigned_url_expire_seconds = int(get_config("/presigned_url_expire_seconds", str(self.presigned_url_expire_seconds)))


    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


from functools import lru_cache
@lru_cache()
# 全局配置实例,延迟加载
def get_settings():
    settings = Settings()
    settings.load_from_consul()
    return settings