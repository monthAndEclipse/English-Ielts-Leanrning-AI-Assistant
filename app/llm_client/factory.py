from app.llm_client.openai_client import OpenAIClient
from app.llm_client.deepseek_client import DeepSeekClient
import logging
# 未来可以引入 ClaudeClient, DeepseekClient 等

logger = logging.getLogger(__name__)
from app.core.user_config import (
    UserConfig,
    load_user_config,
    save_user_config,
)

def get_llm_client(provider: str, model_name:str):
    if not provider or not provider.strip():
        raise ValueError(f"Unsupported LLM provider: {provider}")
    if not model_name or not model_name.strip():
        raise ValueError(f"Unsupported LLM model_name: {model_name}")
    cfg = load_user_config()
    if not cfg:
        raise ValueError(f"API秘钥未配置")

    provider = provider.lower()
    logger.info(f"{provider} provider is used,model_name:{model_name}")
    if provider == "openai":
        return OpenAIClient(model_name,cfg.openai_api_key)
    if provider == "deepseek":
        return DeepSeekClient(model_name,cfg.openai_api_key)
    else:
        raise ValueError(f"Unsupported LLM provider and model: {provider}_{model_name}")
