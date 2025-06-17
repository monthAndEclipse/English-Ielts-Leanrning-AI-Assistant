#根据file_path去存储服务获取文件流
import httpx
import json
from app.config import get_settings
from typing import Optional
import logging

logger = logging.getLogger(__name__)

async def download_file_text_from_storage(file_path: str, token: str):
    url = f"http://{get_settings().storage_service_container}/api/v1/storage/download/{file_path}"
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers)
            if response.status_code == 200:
                # 获取原始字节内容
                byte_data = response.content
                # 尝试解码为 json 对象
                json_obj = json.loads(byte_data.decode("utf-8"))
                return json_obj
        except Exception as e:
            logger.exception("下载失败")
            return None
    return None


async def upload_file_to_storage(
        token: str,
        file_bytes: bytes,
        filename: str ,
        content_type: str = "application/octet-stream"
):
    url = f"http://{get_settings().storage_service_container}/api/v1/storage/upload"
    headers = {"Authorization": f"Bearer {token}"}
    if not file_bytes or not filename:
        raise ValueError("file_bytes or filename is empty")
    # 上传字节数组
    files = {
        "file": (filename, file_bytes, content_type)
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, files=files)
        if response.status_code == 200:
            return response.json()
        else:
            logger.exception("上传失败详情")
            raise Exception(f"上传失败: {response.status_code} - {response.text}")

