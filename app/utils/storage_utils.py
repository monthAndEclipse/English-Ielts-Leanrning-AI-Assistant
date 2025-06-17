#根据file_path去存储服务获取文件流
import httpx
import json
from app.config import get_settings
from typing import Optional

async def download_file_text_from_storage(file_path: str, token: str):
    url = f"http://{get_settings().storage_service_container}/api/v1/storage/download/{file_path}"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code == 200:
            # 获取原始字节内容
            byte_data = response.content
            try:
                # 尝试解码为 json 对象
                json_obj = json.loads(byte_data.decode("utf-8"))
                return json_obj["texts"]
            except json.JSONDecodeError:
                raise ValueError("下载的内容不是合法的 JSON 数据")
        else:
            raise Exception(f"下载失败: {response.status_code} - {response.text}")


async def upload_file_to_storage(
        token: str,
        file_type: str = "files",
        file_bytes: Optional[bytes] = None,
        file_name: Optional[str] = None,
        local_file_path: Optional[str] = None,
        content_type: str = "application/octet-stream"
):
    """
    上传文件到远程存储服务。

    支持本地路径或内存字节数组方式上传。
    参数说明：
    - token: JWT 授权 Token
    - file_type: 文件分类（如 "files", "avatar", "docs"）
    - file_bytes: 文件内容（bytes）
    - file_name: 文件名（和 file_bytes 配合使用）
    - local_file_path: 本地文件路径（若使用此方式，file_bytes 可不传）
    - content_type: MIME 类型（默认 application/octet-stream）
    """
    url = f"http://{get_settings().storage_service_container}/api/v1/storage/upload"
    headers = {
        "Authorization": f"Bearer {token}"
    }

    if file_bytes and file_name:
        # 上传字节数组
        files = {
            "file": (file_name, file_bytes, content_type)
        }
    elif local_file_path:
        # 上传本地文件
        with open(local_file_path, "rb") as f:
            file_name = file_name or local_file_path.split("/")[-1]
            files = {
                "file": (file_name, f, content_type)
            }
    else:
        raise ValueError("请提供 file_bytes+file_name 或 local_file_path 中的一个")

    data = {
        "file_type": file_type
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, files=files, data=data)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"上传失败: {response.status_code} - {response.text}")

