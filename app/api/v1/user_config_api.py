from fastapi import APIRouter
from app.core.user_config import (
    UserConfig,
    load_user_config,
    save_user_config,
)

router = APIRouter(tags=["settings"])


def mask_key(key: str) -> str:
    if len(key) < 8:
        return "****"
    return key[:4] + "****" + key[-4:]


@router.get("/api/status")
def app_status():
    cfg = load_user_config()
    return {
        "ready": cfg is not None,
    }


@router.get("/api/settings")
def get_settings():
    """
    前端获取当前设置，用于回显
    """
    cfg = load_user_config()
    if not cfg:
        return {
            "configured": False,
            "openai_api_key": "",
            "base_url": "",
        }

    return {
        "configured": True,
        # ⚠️ 可以选择是否脱敏
        "openai_api_key":  mask_key(cfg.openai_api_key),
        "base_url": cfg.base_url or "",
    }

@router.post("/api/settings")
def save_settings(cfg: UserConfig):
    save_user_config(cfg)
    return {"ok": True}
