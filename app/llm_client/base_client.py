from abc import ABC, abstractmethod

class BaseLLMClient(ABC):

    @abstractmethod
    def translate(self, prompt:str ) -> str:
        """翻译文本到目标语言"""
        pass

