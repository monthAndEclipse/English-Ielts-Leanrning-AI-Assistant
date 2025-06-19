"""
消息发布器
负责向RabbitMQ发送消息
"""
import logging
from aio_pika import Message, DeliveryMode
from .connection_manager import RabbitMQConnectionManager

logger = logging.getLogger(__name__)


class MessagePublisher:
    """消息发布器"""

    def __init__(self, connection_manager: RabbitMQConnectionManager):
        self.connection_manager = connection_manager

    async def publish_message(
            self,
            queue_name: str,
            message_body: str,
            routing_key: str = None,
            exchange_name: str = ""
    ) -> bool:
        """
        发布消息到指定队列
        Args:
            queue_name: 队列名称
            message_body: 消息体
            routing_key: 路由键，默认使用队列名
            exchange_name: 交换器名称，默认为空

        Returns:
            bool: 发送成功返回True
        """
        try:
            channel = await self.connection_manager.get_channel()

            # 声明队列（确保队列存在）
            await channel.declare_queue(
                queue_name,
                durable=True,  # 队列持久化
                auto_delete=False
            )

            # 构建消息
            message = Message(
               message_body.encode('utf-8'),
                delivery_mode=DeliveryMode.PERSISTENT,  # 消息持久化
                content_type='application/json',
                content_encoding='utf-8'
            )

            # 发送消息
            await channel.default_exchange.publish(
                message,
                routing_key=routing_key or queue_name
            )

            logger.info(f"消息已发送到队列 {queue_name}: {message_body}")
            return True

        except Exception as e:
            logger.error(f"发送消息到队列 {queue_name} 失败: {e}")
            return False

