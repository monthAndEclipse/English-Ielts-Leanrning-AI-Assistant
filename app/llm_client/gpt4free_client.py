from openai import OpenAI
from .base_client import BaseLLMClient
import logging
from g4f.client import Client

logger = logging.getLogger(__name__)
"""
github开源的免费api工具, 好像只是开页面去抓取的，不是纯后端调用
"""
@DeprecationWarning
class GPT4FreeClient(BaseLLMClient):
    # singleton is fine
    _shared_client = None

    def __init__(self, model_name: str = None):
        if not GPT4FreeClient._shared_client:
            GPT4FreeClient._shared_client = Client()
        self.client = GPT4FreeClient._shared_client
        self.model_name = model_name

    def prompt(self, prompt: str) -> str:
        try:
            logger.info(f"prompt: {prompt},using model: {self.model_name}")
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": prompt},
                ],
                web_search=False
            )
            print("RAW RESPONSE:", response)
            print(response.choices[0].message.content)
            return ""

        except Exception as e:
            logger.error(f"Translation failed: {e}")
            logger.exception("Translation failed details")
            raise e


