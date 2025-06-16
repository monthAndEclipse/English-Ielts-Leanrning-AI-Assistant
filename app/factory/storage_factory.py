from typing import Dict, Type

from app.core.cloud_storage_base import BaseStorageProvider
from app.core.impl.minio_storage import MinIOStorageProvider
from app.config import StorageProvider
from app.exceptions import StorageOperationException
from app.utils.logger import get_logger
from app.config import get_settings
logger = get_logger(__name__)


class StorageFactory:
    """存储提供商工厂类"""

    # 注册所有可用的存储提供商
    _providers: Dict[StorageProvider, Type[BaseStorageProvider]] = {
        StorageProvider.MINIO: MinIOStorageProvider,
        # 未来可以添加更多提供商:
        # StorageProvider.AWS_S3: S3StorageProvider,
        # StorageProvider.GOOGLE_CLOUD: GCSStorageProvider,
    }
    # 存储提供商实例缓存
    _instances: Dict[StorageProvider, BaseStorageProvider] = {}

    @classmethod
    async def get_storage_provider(cls, provider_type: StorageProvider = None) -> BaseStorageProvider:
        """
        获取存储提供商实例

        Args:
            provider_type: 存储提供商类型，如果为None则使用配置中的默认类型

        Returns:
            BaseStorageProvider: 存储提供商实例
        """
        settings = get_settings()
        logger.info(f"settings:{settings}")
        if provider_type is None:
            provider_type = settings.storage_provider

        # 检查是否已经创建了实例
        if provider_type in cls._instances:
            return cls._instances[provider_type]

        # 检查提供商是否已注册
        if provider_type not in cls._providers:
            available_providers = ", ".join([p.value for p in cls._providers.keys()])
            raise StorageOperationException(
                "factory",
                f"Unsupported storage provider: {provider_type}. "
                f"Available providers: {available_providers}"
            )

        # 创建配置
        config = cls._get_provider_config(provider_type)

        # 创建实例
        provider_class = cls._providers[provider_type]
        provider_instance = provider_class(config)

        # 初始化
        await provider_instance.initialize()

        # 缓存实例
        cls._instances[provider_type] = provider_instance

        logger.info(f"Storage provider '{provider_type}' initialized successfully")

        return provider_instance

    @classmethod
    def _get_provider_config(cls, provider_type: StorageProvider) -> dict:
        """
        根据提供商类型获取配置

        Args:
            provider_type: 存储提供商类型

        Returns:
            dict: 提供商配置
        """
        settings = get_settings()
        if provider_type == StorageProvider.MINIO:
            return {
                "endpoint": settings.minio_endpoint,
                "access_key": settings.minio_access_key,
                "secret_key": settings.minio_secret_key,
                "secure": settings.minio_secure,
                "bucket_name": settings.minio_bucket_name,
            }

        # 未来可以添加其他提供商的配置
        # elif provider_type == StorageProvider.AWS_S3:
        #     return {
        #         "region": settings.aws_region,
        #         "access_key_id": settings.aws_access_key_id,
        #         "secret_access_key": settings.aws_secret_access_key,
        #         "bucket_name": settings.aws_bucket_name,
        #     }

        raise StorageOperationException(
            "factory",
            f"No configuration found for storage provider: {provider_type}"
        )

    @classmethod
    def register_provider(
            cls,
            provider_type: StorageProvider,
            provider_class: Type[BaseStorageProvider]
    ) -> None:
        """
        注册新的存储提供商

        Args:
            provider_type: 存储提供商类型
            provider_class: 存储提供商类
        """
        cls._providers[provider_type] = provider_class
        logger.info(f"Storage provider '{provider_type}' registered successfully")

    @classmethod
    def get_available_providers(cls) -> list[str]:
        """
        获取所有可用的存储提供商

        Returns:
            list[str]: 可用提供商列表
        """
        return [provider.value for provider in cls._providers.keys()]

    @classmethod
    async def close_all_connections(cls) -> None:
        """关闭所有存储提供商连接"""
        for provider_type, instance in cls._instances.items():
            try:
                if hasattr(instance, 'close'):
                    await instance.close()
                logger.info(f"Closed connection for storage provider: {provider_type}")
            except Exception as e:
                logger.error(f"Error closing storage provider {provider_type}: {str(e)}")

        cls._instances.clear()


# 便捷函数
async def get_default_storage() -> BaseStorageProvider:
    """获取默认存储提供商实例"""
    return await StorageFactory.get_storage_provider()