from openai import OpenAI
from .base_client import BaseLLMClient
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class DeepSeekClient(BaseLLMClient):
    # singleton is fine
    _shared_client = None

    def __init__(self, model_name: str = None,api_key: str = None):
        if not DeepSeekClient._shared_client:
            DeepSeekClient._shared_client = OpenAI(api_key=api_key,base_url="https://api.deepseek.com")
        self.client = DeepSeekClient._shared_client
        self.model_name = model_name

    def prompt(self, prompt: str) -> str:
        try:
            logger.info(f"prompt: {prompt},using model: {self.model_name}")
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                stream=True,
                max_tokens=8000
            )
            full_content = []
            for chunk in response:
                delta = getattr(chunk.choices[0].delta, 'content', None)
                if delta:
                    full_content.append(delta)
            result = ''.join(full_content)
            logger.info(result)
            return result

        except Exception as e:
            logger.error(f"Translation failed: {e}")
            logger.exception("Translation failed details")
            raise e

