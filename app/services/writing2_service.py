from abc import ABC

from app.services.base_task_service import BasePromptService
from app.schemas.task_req import TaskReq
import json
import random

class Writing2PromptService(BasePromptService, ABC):
    difficulty = ["easy", "medium", "hard"]
    # -------------------------------
    # 角度维度（Perspective / Focus）
    # -------------------------------
    perspective = [
        # 影响对象
        "Individual impact",
        "Societal impact",
        "Economic impact",
        "Environmental impact",
        "Cultural impact",
        "Technological impact",
        "Educational impact",
        "Health impact",
        "Political impact",
        # 时间维度
        "Short-term effect",
        "Long-term effect",
        # 结果分析
        "Cause analysis",
        "Consequence analysis",
        # 比较/对比
        "Advantages vs Disadvantages",
        "Pros and Cons",
        "Comparison between options",
        # 立场/态度
        "Personal opinion",
        "Collective opinion",
        "Neutral stance",
        # 解决方案/建议
        "Problem-solving approach",
        "Recommendation focus"
    ]

    # -------------------------------
    # 地域维度（Region / Geography）
    # -------------------------------
    region = [
        "Global",
        "National",
        "Local / Community",
        "Urban areas",
        "Rural areas",
        "Developed countries",
        "Developing countries",
        "Asia",
        "Europe",
        "North America",
        "South America",
        "Africa",
        "Australia / Oceania",
        "Middle East"
    ]

    # -------------------------------
    # 群体维度（Population / Group）
    # -------------------------------
    population = [
        "Children / Students",
        "Teenagers",
        "Young adults",
        "Adults",
        "Elderly / Senior citizens",
        "Workers / Employees",
        "Unemployed people",
        "Women",
        "Men",
        "Families / Households",
        "Society at large",
        "Professionals / Experts",
        "Urban residents",
        "Rural residents",
        "Government / Policy makers"
    ]

    def start_pre_process(self, data: TaskReq, prompt: str) -> str:
        # 👉 这里写你“synonym start”的前置增强逻辑
        processed = self.randomize(data,prompt)
        return processed

    def randomize(self,data: TaskReq,prompt: str)-> str:
        original_type = data.type
        data.type = "subtopics"
        subtopics_start_prompt = self.choose_prompt(data)
        subtopics_start_prompt = subtopics_start_prompt.replace("[1]",data.domain)
        random_subtopics = self.retry_prompt(subtopics_start_prompt)
        random_subtopics_json = json.loads(random_subtopics)

        task_config = {
            "question_type": data.question_type,
            "topic": data.domain,
            "subtopics": random.choice(random_subtopics_json["subtopics"]),
            "difficulty": random.choice(self.difficulty),
            "perspective": random.choice(self.perspective),
            "region": random.choice(self.region),
            "population": random.choice(self.population),
        }
        processed = prompt.replace("[1]",task_config["question_type"])
        processed = processed.replace("[2]",task_config["topic"])
        processed = processed.replace("[3]",task_config["subtopics"])
        processed = processed.replace("[4]",task_config["difficulty"])
        processed = processed.replace("[5]",task_config["perspective"])
        processed = processed.replace("[6]",task_config["region"])
        processed = processed.replace("[7]",task_config["population"])

        #还原
        data.type = original_type
        return processed

    def correct_pre_process(self, data: TaskReq, prompt: str) -> str:
        """
        在 prompt 中替换占位符：
        [1] -> 原始题目 original_article
        [2] -> 用户答案 answers（通常是 dict，需要转成 json 字符串）
        """
        # --- 1. 取数据 ---
        original = data.original_article or ""
        answers = data.answers or {}
        question_type = data.question_type or ""

        # 将 answers 转为漂亮的 JSON，防止 dict 无法直接放进 prompt
        import json
        answers_json = json.dumps(answers, ensure_ascii=False, indent=2)

        # --- 2. 替换占位符 ---
        # 使用简单 replace 即可，因为格式固定
        processed = prompt.replace("[1]", question_type).replace("[2]", original).replace("[3]", answers_json)

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
