from pydantic import BaseModel, Field
from typing import Any, Optional, Generic, TypeVar

# 定义泛型类型变量
T = TypeVar('T')

class APIResponse(BaseModel, Generic[T]):
    """通用API响应模型"""
    code: str = Field(..., description="响应状态码，'0'表示成功")
    msg: str = Field(..., description="响应消息")
    data: Optional[T] = Field(None, description="响应数据")

    class Config:
        # 允许任意类型的数据
        arbitrary_types_allowed = True
        # JSON编码配置
        json_encoders = {
            # 可以在这里添加自定义类型的编码器
        }

    @classmethod
    def success(cls, data: Optional[T] = None, msg: str = "success") -> 'APIResponse[T]':
        """成功响应"""
        return cls(code="0", msg=msg, data=data)

    @classmethod
    def error(cls, code: str, msg: str, data: Optional[T] = None) -> 'APIResponse[T]':
        """错误响应"""
        return cls(code=code, msg=msg, data=data)

    # 常用错误响应
    @classmethod
    def unauthorized(cls, msg: str = "Authentication required") -> 'APIResponse[None]':
        """401 未授权"""
        return cls.error("401", msg)

    @classmethod
    def forbidden(cls, msg: str = "Forbidden") -> 'APIResponse[None]':
        """403 禁止访问"""
        return cls.error("403", msg)

    @classmethod
    def not_found(cls, msg: str = "Resource not found") -> 'APIResponse[None]':
        """404 资源未找到"""
        return cls.error("404", msg)

    @classmethod
    def server_error(cls, msg: str = "Internal server error") -> 'APIResponse[None]':
        """500 服务器内部错误"""
        return cls.error("500", msg)

    @classmethod
    def invalid_params(cls, msg: str = "Invalid params") -> 'APIResponse[None]':
        """参数无效"""
        return cls.error("-1", msg)

    @classmethod
    def validation_error(cls, msg: str = "Validation failed") -> 'APIResponse[None]':
        """数据验证失败"""
        return cls.error("422", msg)

    @classmethod
    def bad_request(cls, msg: str = "Bad request") -> 'APIResponse[None]':
        """400 请求错误"""
        return cls.error("400", msg)

    def is_success(self) -> bool:
        """判断是否为成功响应"""
        return self.code == "0"

    def is_error(self) -> bool:
        """判断是否为错误响应"""
        return self.code != "0"
