from app.llm_client.openai_client import OpenAIClient
from app.llm_client.deepseek_client import DeepSeekClient
from app.llm_client.gpt4free_client import GPT4FreeClient
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
    if provider == "gpt4free":
        return GPT4FreeClient(model_name)
    else:
        raise ValueError(f"Unsupported LLM provider and model: {provider}_{model_name}")
