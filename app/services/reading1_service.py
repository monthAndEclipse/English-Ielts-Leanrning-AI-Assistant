from abc import ABC

from app.services.base_task_service import BasePromptService
from app.schemas.task_req import TaskReq
import json
import random

class Reading1PromptService(BasePromptService, ABC):

    def start_pre_process(self, data: TaskReq, prompt: str) -> str:
        # 👉 这里写你“synonym start”的前置增强逻辑
        processed = self.randomize(data,prompt)
        return processed

    def randomize(self, data, prompt):
        original_type = data.type
        data.type = "subtopics"

        # 生成 subtopics
        subtopic_prompt = self.choose_prompt(data).replace("[1]", data.domain)
        subtopics_json = json.loads(self.retry_prompt(subtopic_prompt))

        # 🎯 随机 topic + 随机 dimension（统一机制）
        random_dims = self.random_dimensions()
        # 例如返回：
        # {"text_styles": "historical", "tones": "critical", ...}
        task_config = {
            "topic": data.domain,
            "subtopics": random.choice(subtopics_json["subtopics"]),
            **random_dims
        }

        # 替换
        result = prompt
        result = result.replace("[1]", task_config["topic"])
        result = result.replace("[2]", task_config["subtopics"])

        # 把所有随机维度按名称自动注入 prompt
        for key, value in random_dims.items():
            result = result.replace(f"[{key}]", value)

        data.type = original_type
        return result

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
        processed = prompt.replace("[1]", original).replace("[2]", answers_json)

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
