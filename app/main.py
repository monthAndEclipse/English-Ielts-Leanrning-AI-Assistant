from fastapi import FastAPI
from app.api.v1.task_api import router as task_router
import logging
import os
import sys
import socket
import uvicorn
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from starlette.responses import FileResponse
from app.api.v1.user_config_api import router as config_router

logger = logging.getLogger(__name__)
def base_path() -> Path:
    """
    项目根路径：
    - 普通 python 运行：项目目录
    - PyInstaller --onefile：_MEIPASS
    """
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parents[1]  # ← 回到项目根

BASE_DIR = base_path()
FRONTEND_DIR = BASE_DIR / "frontend" / "out"
STATIC_DIR = BASE_DIR / "app" / "static"


app = FastAPI(docs_url=None,redoc_url=None)

# 1. 挂载静态资源
app.mount(
    "/_next",
    StaticFiles(directory=FRONTEND_DIR / "_next"),
    name="nextjs-static"
)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

#路由设置
app.include_router(task_router, prefix="/api/v1", tags=["task"])
app.include_router(config_router, prefix="/api/v1",tags=["config"])

# 2. 处理前端路由（非常重要）
@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    """
    所有非 API 路由交给 Next.js 的 index.html
    """
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"error": "frontend not found"}


# -------------------------
# 端口检测（防止重复启动）
# -------------------------
def port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0


# -------------------------
# 程序入口
# -------------------------
if __name__ == "__main__":
    PORT = 8080

    if port_in_use(PORT):
        print(f"[INFO] Port {PORT} already in use, exit")
        sys.exit(0)

    print(f"started....")
    uvicorn.run(
        app,
        host="127.0.0.1",      # ✅ 非常重要
        port=PORT,
        log_level="error",    # ✅ 避免命令行刷屏
        access_log=False,
        reload=False
    )

# uvicorn app.main:app --reload
# pip freeze > requirements.txt
#pyinstaller --onefile --add-data "app/static;app/static" --add-data "frontend/out;frontend/out" --add-data "app/config/settings.yml;config" --name ai_server --hidden-import=uvicorn.protocols.http --hidden-import=uvicorn.protocols.websockets --hidden-import=uvicorn.lifespan.on app/main.py
