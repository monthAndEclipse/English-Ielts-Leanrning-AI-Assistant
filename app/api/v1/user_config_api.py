from fastapi import APIRouter
from app.core.user_config import (
    UserConfig,
    load_user_config,
    save_user_config,
)
from app.schemas.api_response import APIResponse

router = APIRouter(prefix="/settings",tags=["config"])

@router.get("/status")
def app_status():
    cfg = load_user_config()
    return APIResponse.success({
        "ready": cfg is not None,
    })


@router.get("/get")
def get_settings():
    """
    前端获取当前设置，用于回显
    """
    cfg = load_user_config()
    if not cfg:
        return APIResponse.success({
            "configured": False,
            "openai_api_key": "",
            "base_url": "",
        })

    return APIResponse.success({
        "configured": True,
        "openai_api_key": cfg.openai_api_key,
        "base_url": cfg.base_url or "",
    })

@router.post("/save")
def save_settings(cfg: UserConfig):
    save_user_config(cfg)
    return APIResponse.success({"ok": True})
