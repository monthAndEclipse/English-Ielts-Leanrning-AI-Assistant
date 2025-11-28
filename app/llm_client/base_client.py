from abc import ABC, abstractmethod

class BaseLLMClient(ABC):

    @abstractmethod
    def prompt(self, prompt:str ) -> str:
        """翻译文本到目标语言"""
        pass

