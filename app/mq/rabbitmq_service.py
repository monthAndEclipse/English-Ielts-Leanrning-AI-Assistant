"""
RabbitMQ服务封装
整合连接管理、消息发布和消费功能的高级封装
"""
import logging
from typing import Callable, Optional,Dict,Any
from app.mq.connection_manager import RabbitMQConnectionManager
from app.mq.message_publisher import MessagePublisher
from app.mq.message_consumer import MessageConsumer
from typing import TypeVar,Type,Union,Awaitable

logger = logging.getLogger(__name__)
T = TypeVar("T")

class RabbitMQService:
    """RabbitMQ服务封装"""

    def __init__(
            self,
            host: str,
            port: int,
            username: str,
            password: str,
            virtual_host: str = "/"
    ):
        self.connection_manager = RabbitMQConnectionManager(
            host=host,
            port=port,
            username=username,
            password=password,
            virtual_host=virtual_host
        )
        self.publisher = MessagePublisher(self.connection_manager)
        self.consumer = MessageConsumer(self.connection_manager)
        self._initialized = False

    async def initialize(self) -> None:
        """初始化服务"""
        if not self._initialized:
            await self.connection_manager.connect()
            self._initialized = True
            logger.info("RabbitMQ服务初始化完成")

    async def consuming_msg(
            self,
            queue_name: str,
            handler: Callable[[T], Union[Awaitable[None], None]],
            message_cls: Type[T],
            max_concurrent_messages: int = 5
    ) -> None:
        """
        启动翻译服务
        Args:
            queue_name:队列名称
            handler: 翻译处理函数
            message_cls: 泛型
            max_concurrent_messages: 最大并发处理消息数
        """
        if not self._initialized:
            await self.initialize()

        await self.consumer.start_consuming(
            queue_name,
            handler,
            message_cls,
            max_concurrent_messages
        )

    async def publish_msg(
            self,
            queue: str,
            msg: str
    ) -> bool:
        if not self._initialized:
            await self.initialize()

        return await self.publisher.publish_message(queue, msg)


    async def health_check(self) -> bool:
        """
        健康检查

        Returns:
            bool: 服务健康返回True
        """
        try:
            if not self._initialized:
                return False

            return await self.connection_manager.is_connected()
        except Exception as e:
            logger.error(f"健康检查失败: {e}")
            return False

    async def stop(self) -> None:
        """停止服务"""
        logger.info("正在停止RabbitMQ服务...")

        # 停止消费
        await self.consumer.stop_consuming()

        # 关闭连接
        await self.connection_manager.close()

        self._initialized = False
        logger.info("RabbitMQ服务已停止")

    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.stop()