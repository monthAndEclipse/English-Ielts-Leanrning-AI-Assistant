import json
from pathlib import Path
from pydantic import BaseModel
from app.core.paths import runtime_dir


class UserConfig(BaseModel):
    openai_api_key: str
    base_url: str | None = None


CONFIG_PATH: Path = runtime_dir() / "user_config.json"


def load_user_config() -> UserConfig | None:
    if not CONFIG_PATH.exists():
        return None
    return UserConfig.model_validate_json(
        CONFIG_PATH.read_text(encoding="utf-8")
    )


def save_user_config(cfg: UserConfig) -> None:
    CONFIG_PATH.write_text(
        cfg.model_dump_json(indent=2),
        encoding="utf-8"
    )
