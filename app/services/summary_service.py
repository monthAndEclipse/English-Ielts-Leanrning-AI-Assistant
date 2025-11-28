from abc import ABC

from app.services.base_task_service import BasePromptService
from app.schemas.task_req import TaskReq
import json
import random
class SummaryPromptService(BasePromptService, ABC):

    def start_pre_process(self, data: TaskReq, prompt: str) -> str:
        # 👉 这里写你“synonym start”的前置增强逻辑
        processed = prompt.replace("[1]", data.domain)
        return processed

    def correct_pre_process(self, data: TaskReq, prompt: str) -> str:
        """
        在 prompt 中替换占位符：
        [1] -> 原始文章 original_article
        [2] -> 用户答案 answers（通常是 dict，需要转成 json 字符串）
        """
        # --- 1. 取数据 ---
        original = data.original_article or ""
        answers = data.answers or {}

        # 将 answers 转为漂亮的 JSON，防止 dict 无法直接放进 prompt
        import json
        answers_json = json.dumps(answers, ensure_ascii=False, indent=2)

        # --- 2. 替换占位符 ---
        # 使用简单 replace 即可，因为格式固定
        processed = prompt.replace("[1]", original)
        processed = processed.replace("[2]", answers_json)
        return processed

    def hint_pre_process(self, data: TaskReq, prompt: str) -> str:
        # 👉 这里写“synonym hint”的前置增强逻辑
        return prompt


    def start_post_process(self, data: TaskReq, result: str) -> str:
        # 👉 这里写你“synonym start”的后处理逻辑
        return result

    def correct_post_process(self, data: TaskReq, result: str) -> str:
        # 👉 这里写“synonym correct”的后处理
        return result

    def hint_post_process(self, data: TaskReq, result: str) -> str:
        # 👉 这里写“synonym hint”的后处理
        return result
