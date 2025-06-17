from openai_client import OpenAIClient
from deepseek_client import DeepSeekClient
import logging
# 未来可以引入 ClaudeClient, DeepseekClient 等

logger = logging.getLogger(__name__)

def get_llm_client(provider: str, model_name:str):
    if not provider or not provider.strip():
        raise ValueError(f"Unsupported LLM provider: {provider}")
    if not model_name or not model_name.strip():
        raise ValueError(f"Unsupported LLM model_name: {model_name}")

    provider = provider.lower()
    logger.info(f"{provider} provider is used,model_name:{model_name}")
    if provider == "openai":
        return OpenAIClient(model_name)
    if provider == "deepseek":
        return DeepSeekClient(model_name)
    else:
        raise ValueError(f"Unsupported LLM provider and model: {provider}_{model_name}")
