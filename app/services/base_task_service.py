import logging
import asyncio
from abc import ABC, abstractmethod
from typing import Optional
from app.llm_client.factory import get_llm_client
from app.config import settings
from app.schemas.task_req import TaskReq
from app.services.random_dimensions import RandomizerEngine

logger = logging.getLogger(__name__)


class BasePromptService(ABC):
    """
    抽象类，所有任务类型的 Service 都从这里继承
    子类只需要实现：start_post_process_by_type / correct_post_process_by_type / hint_post_process_by_type
    """

    def __init__(self):
        self.settings = settings
        self.client = get_llm_client(
            self.settings.llm.provider,
            self.settings.llm.model
        )

    def random_dimensions(self, dim_list=None, k=None):
        """
        dim_list: 想使用的维度（None=全体）
        k: 随机挑选多少个维度
        """
        from app.services.random_dimensions import READING_DIMENSIONS

        # 默认使用全部维度
        dim_list = dim_list or list(READING_DIMENSIONS.keys())
        return RandomizerEngine.pick_reading(dim_list, k=k)

    # ======================================================
    #                    ⭐ public API ⭐
    # ======================================================
    def start(self, data: TaskReq):
        prompt = self.choose_prompt(data)
        prompt = self.start_pre_process(data, prompt)
        llm_result = self.retry_prompt(prompt)
        return self.start_post_process(data, llm_result)

    def correct(self, data: TaskReq):
        prompt = self.choose_prompt(data)
        prompt = self.correct_pre_process(data, prompt)
        llm_result = self.retry_prompt(prompt)
        return self.correct_post_process(data, llm_result)

    def hint(self, data: TaskReq):
        prompt = self.choose_prompt(data)
        llm_result = self.retry_prompt(prompt)
        return self.hint_post_process(data, llm_result)

    # ======================================================
    #                     ⭐ 抽象方法 ⭐
    # ======================================================
    @abstractmethod
    def start_post_process(self, data: TaskReq, result: str) -> str:
        pass

    @abstractmethod
    def correct_post_process(self, data: TaskReq, result: str) -> str:
        pass

    @abstractmethod
    def hint_post_process(self, data: TaskReq, result: str) -> str:
        pass

    @abstractmethod
    def start_pre_process(self, data: TaskReq, prompt: str) -> str:
        pass

    @abstractmethod
    def correct_pre_process(self, data: TaskReq, prompt: str) -> str:
        pass

    @abstractmethod
    def hint_pre_process(self, data: TaskReq, prompt: str) -> str:
        pass

    # ======================================================
    #                  ⭐ Prompt 选择逻辑 ⭐
    # ======================================================
    def choose_prompt(self, data: TaskReq)->str:
        lang = getattr(data, "language", "zh")
        task_type = getattr(data, "type", None)
        subtype = getattr(data, "subtype", "start")

        lang_prompt = getattr(self.settings.prompt, lang, None)
        if lang_prompt is None:
            lang_prompt = self.settings.prompt.zh

        combined_key = f"{task_type}_{subtype}" if task_type else None

        prompt = getattr(lang_prompt, combined_key, None) if combined_key else None

        if prompt is None and task_type:
            default_key = f"{task_type}_start"
            prompt = getattr(lang_prompt, default_key, None)

        if prompt is None:
            prompt = getattr(lang_prompt, "default")

        return prompt

    # ======================================================
    #                  ⭐ 重试逻辑 ⭐
    # ======================================================
    def retry_prompt(self, prompt):
        retries = int(self.settings.llm.retries)
        retry_delay = int(self.settings.llm.retry_delay)

        for attempt in range(1, retries + 1):
            try:
                return self.client.prompt(prompt)
            except Exception as e:
                logger.error(f"【LLM 调用失败 第 {attempt}/{retries} 次】 {e}")
                logger.exception("任务失败详情：")

                if attempt < retries:
                    asyncio.sleep(retry_delay)
                    continue
                else:
                    raise e

        return None

    def __del__(self):
        pass
