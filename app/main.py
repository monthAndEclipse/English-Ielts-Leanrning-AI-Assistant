from fastapi import FastAPI
from app.api.v1.log_api import router as log_router
from app.api.v1.storage_router import router as store_router
from fastapi.middleware.cors import CORSMiddleware
from app.utils.consul_utils import ConsulServiceRegistrar, set_global_config
from sqlmodel import SQLModel
from contextlib import asynccontextmanager
from app.db.database import engine
from app.db.models import *
import os

#数据库初始化
@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield
    # cleanup code here if needed

app = FastAPI(lifespan=lifespan)

# 启动 Consul 注册 + 配置拉取
consul_client = ConsulServiceRegistrar(
    service_name=os.getenv("SERVICE_NAME"),
    service_port=int(os.getenv("SERVICE_PORT")),
    consul_host=os.getenv("CONSUL_HOST"),
    config_prefix=os.getenv("CONSUL_CONFIG_PREFIX"),
    update_interval=59,
    hostname=os.getenv("HOSTNAME"),
)
consul_client.register_service()
consul_client.start_config_updater()
set_global_config(consul_client)

#路由设置
app.include_router(log_router, prefix="/api/v1/log", tags=["Logs"])
app.include_router(store_router, prefix="/api/v1/storage", tags=["Storage"])

#跨域设置
#dev locally ,no need to push to remote branch
origins = [
    "http://localhost:4001",  # Local development
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]  # Expose all headers to frontend
)

# uvicorn app.main:app --reload
# pip freeze > requirements.txt

