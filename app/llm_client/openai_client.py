from openai import OpenAI
from .base_client import BaseLLMClient
import logging

logger = logging.getLogger(__name__)
"""
openAI的价格太贵了，基本没有用武之地了，付不起，后期再说吧
"""
@DeprecationWarning
class OpenAIClient(BaseLLMClient):
    def __init__(self):
        self.client = OpenAI()

    async def prompt(self, prompt: str) -> str:
        pass

