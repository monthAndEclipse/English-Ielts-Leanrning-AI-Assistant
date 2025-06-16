from fastapi import HTTPException, status


class StorageServiceException(Exception):
    """存储服务基础异常"""
    def __init__(self, message: str, details: str = None):
        self.message = message
        self.details = details
        super().__init__(self.message)


class AuthenticationException(HTTPException):
    """认证异常"""
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )


class AuthorizationException(HTTPException):
    """授权异常"""
    def __init__(self, detail: str = "Access denied"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )


class FileNotFoundException(HTTPException):
    """文件未找到异常"""
    def __init__(self, file_path: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File not found: {file_path}"
        )


class FileTooLargeException(HTTPException):
    """文件过大异常"""
    def __init__(self, max_size: int):
        super().__init__(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed size of {max_size} bytes"
        )


class InvalidFileTypeException(HTTPException):
    """无效文件类型异常"""
    def __init__(self, file_type: str, allowed_types: list[str]):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type '{file_type}' not allowed. Allowed types: {', '.join(allowed_types)}"
        )


class StorageOperationException(HTTPException):
    """存储操作异常"""
    def __init__(self, operation: str, detail: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Storage operation '{operation}' failed: {detail}"
        )


class BucketNotFoundException(HTTPException):
    """存储桶未找到异常"""
    def __init__(self, bucket_name: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bucket '{bucket_name}' not found"
        )


class InvalidPathException(HTTPException):
    """无效路径异常"""
    def __init__(self, path: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file path: {path}"
        )