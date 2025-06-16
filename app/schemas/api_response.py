from typing import Any, Optional

class APIResponse:
    @staticmethod
    def success(data: Any = None, msg: str = "success") -> dict:
        return {
            "code": "0",
            "msg": msg,
            "data": data
        }

    @staticmethod
    def error(code: str, msg: str, data: Optional[Any] = None) -> dict:
        return {
            "code": code,
            "msg": msg,
            "data": data
        }

    # Common error responses
    @staticmethod
    def unauthorized(msg: str = "Authentication required") -> dict:
        return APIResponse.error("401", msg)

    @staticmethod
    def forbidden(msg: str = "Forbidden") -> dict:
        return APIResponse.error("403", msg)

    @staticmethod
    def not_found(msg: str = "Resource not found") -> dict:
        return APIResponse.error("404", msg)

    @staticmethod
    def server_error(msg: str = "Internal server error") -> dict:
        return APIResponse.error("500", msg)

    @staticmethod
    def invalid_params(msg: str = "invalid params") -> dict:
        return APIResponse.error("-1", msg)