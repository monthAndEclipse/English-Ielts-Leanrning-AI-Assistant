from pydantic import BaseModel, HttpUrl, Field, validator
from typing import Optional, List, Union,Dict
from datetime import datetime
from enum import Enum


class UploadType(str, Enum):
    FILE = "file"
    URL = "url"
    STREAM = "stream"


class FileUploadRequest(BaseModel):
    """文件上传请求"""
    filename: str = Field(..., description="文件名")
    content_type: Optional[str] = Field(None, description="文件类型")
    upload_type: UploadType = Field(UploadType.FILE, description="上传类型")
    url: Optional[HttpUrl] = Field(None, description="URL上传时的源地址")
    folder: Optional[str] = Field(None, description="子文件夹路径")
    tags: Optional[dict] = Field(None, description="文件标签")

    @validator('url')
    def validate_url(cls, v, values):
        if values.get('upload_type') == UploadType.URL and not v:
            raise ValueError('URL upload requires a valid URL')
        return v


class FileInfo(BaseModel):
    """文件信息"""
    filename: str = Field(..., description="原始文件名")
    file_path: str = Field(..., description="存储路径")
    content_type: str = Field(..., description="文件类型")
    file_size: int = Field(..., description="文件大小(字节)")
    upload_time: Optional[datetime] = Field(..., description="上传时间")
    user_id: str = Field(..., description="上传用户ID")
    etag: Optional[str] = Field(None, description="文件ETag")
    last_modified: Optional[datetime] = Field(None, description="最后修改时间")
    file_id: Optional[str] = Field(None, description="文件ID")
    tags: Optional[dict] = Field(None, description="文件标签")

    class Config:
        from_attributes = True


class FileListRequest(BaseModel):
    """文件列表查询请求"""
    folder: Optional[str] = Field(None, description="文件夹路径")
    prefix: Optional[str] = Field(None, description="文件名前缀")
    limit: int = Field(20, ge=1, le=100, description="返回数量限制")
    offset: int = Field(0, ge=0, description="偏移量")
    content_type: Optional[str] = Field(None, description="文件类型过滤")


class FileListResponse(BaseModel):
    """文件列表响应"""
    files: List[FileInfo] = Field(..., description="文件列表")
    total: int = Field(..., description="总数量")
    has_more: bool = Field(..., description="是否还有更多")


class PresignedUrlRequest(BaseModel):
    """预签名URL请求"""
    filename: str = Field(..., description="文件名")
    content_type: Optional[str] = Field(None, description="文件类型")
    folder: Optional[str] = Field(None, description="子文件夹路径")
    expire_seconds: Optional[int] = Field(3600, ge=60, le=86400, description="过期时间(秒)")


class PresignedUrlResponse(BaseModel):
    """预签名URL响应"""
    upload_url: str = Field(..., description="上传URL")
    file_path: str = Field(..., description="文件路径")
    expire_time: datetime = Field(..., description="过期时间")
    fields: Optional[dict] = Field(None, description="额外的表单字段")


class FileDownloadRequest(BaseModel):
    """文件下载请求"""
    file_path: str = Field(..., description="文件路径")
    expire_seconds: Optional[int] = Field(3600, ge=60, le=86400, description="URL过期时间(秒)")


class FileDownloadResponse(BaseModel):
    """文件下载响应"""
    download_url: str = Field(..., description="下载URL")
    filename: str = Field(..., description="文件名")
    content_type: str = Field(..., description="文件类型")
    file_size: int = Field(..., description="文件大小")
    expire_time: datetime = Field(..., description="URL过期时间")


class FileCopyRequest(BaseModel):
    """文件复制请求"""
    source_path: str = Field(..., description="源文件路径")
    target_path: str = Field(..., description="目标文件路径")
    overwrite: bool = Field(False, description="是否覆盖已存在的文件")


class FileDeleteRequest(BaseModel):
    """文件删除请求"""
    file_paths: List[str] = Field(..., min_items=1, description="要删除的文件路径列表")


class FileDeleteResponse(BaseModel):
    """文件删除响应"""
    deleted_files: List[str] = Field(..., description="成功删除的文件路径")
    failed_files: List[dict] = Field(..., description="删除失败的文件信息")


class StorageStatsResponse(BaseModel):
    """存储统计响应"""
    total_files: int = Field(..., description="文件总数")
    total_size: int = Field(..., description="总大小(字节)")
    used_quota: float = Field(..., description="已使用配额百分比")


class ApiResponse(BaseModel):
    """通用API响应"""
    success: bool = Field(..., description="操作是否成功")
    message: str = Field(..., description="响应消息")
    data: Optional[Union[dict, list]] = Field(None, description="响应数据")


class FileUploadFromUrlRequest(BaseModel):
    """从URL上传文件请求模型"""
    url: str = Field(..., description="源文件URL")
    filename: Optional[str] = Field(None, description="文件名（可选）")
    content_type: Optional[str] = Field(None, description="文件MIME类型")
    file_type: str = Field(default="files", description="文件分类")
    metadata: Optional[Dict[str, str]] = Field(default_factory=dict, description="文件元数据")

    @validator('url')
    def validate_url(cls, v):
        if not v or not v.strip():
            raise ValueError('URL cannot be empty')
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return v.strip()

    @validator('filename')
    def validate_filename(cls, v):
        if v is None:
            return v
        if not v.strip():
            raise ValueError('Filename cannot be empty if provided')
        # 移除危险字符
        dangerous_chars = ['/', '\\', '..', '<', '>', ':', '"', '|', '?', '*']
        for char in dangerous_chars:
            if char in v:
                raise ValueError(f'Filename contains dangerous character: {char}')
        return v.strip()


class FileUploadResponse(BaseModel):
    """文件上传响应模型"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    file_info: Optional[FileInfo] = Field(None, description="上传的文件信息")
    error_code: Optional[str] = Field(None, description="错误代码")



class PresignedUploadUrlRequest(BaseModel):
    """预签名上传URL请求模型"""
    filename: str = Field(..., description="文件名")
    content_type: Optional[str] = Field(None, description="文件MIME类型")
    file_type: str = Field(default="files", description="文件分类")
    expire_seconds: int = Field(default=3600, ge=60, le=86400, description="过期时间（秒）")

    @validator('filename')
    def validate_filename(cls, v):
        if not v or not v.strip():
            raise ValueError('Filename cannot be empty')
        # 移除危险字符
        dangerous_chars = ['/', '\\', '..', '<', '>', ':', '"', '|', '?', '*']
        for char in dangerous_chars:
            if char in v:
                raise ValueError(f'Filename contains dangerous character: {char}')
        return v.strip()


class PresignedDownloadUrlRequest(BaseModel):
    """预签名下载URL请求模型"""
    file_path: str = Field(..., description="文件路径")
    expire_seconds: int = Field(default=3600, ge=60, le=86400, description="过期时间（秒）")

    @validator('file_path')
    def validate_file_path(cls, v):
        if not v or not v.strip():
            raise ValueError('File path cannot be empty')
        return v.strip()

