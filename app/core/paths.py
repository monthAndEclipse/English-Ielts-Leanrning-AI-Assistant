import sys
from pathlib import Path


def runtime_dir() -> Path:
    """
    用户可写运行目录：
    - EXE：ai_server.exe 所在目录
    - 源码：项目根目录
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parents[2]


def resource_dir() -> Path:
    """
    只读资源目录（打包资源）：
    - EXE：_MEIPASS
    - 源码：项目根目录
    """
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parents[2]
