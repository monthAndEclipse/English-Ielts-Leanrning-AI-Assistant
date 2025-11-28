import yaml
from pydantic import BaseModel
import sys
from pathlib import Path

class AppConfig(BaseModel):
    name: str
    debug: bool
    version: str

class LLMConfig(BaseModel):
    provider:str
    model:str
    retries:int
    retry_delay:int


class Prompts(BaseModel):
    subtopics_start:str
    synonym_start:str
    synonym_correct:str
    sentence_start:str
    sentence_correct:str
    paragraph_start:str
    paragraph_correct:str
    summary_start:str
    summary_correct:str
    reading1_start:str
    reading1_correct:str
    reading2_start:str
    reading2_correct:str
    reading3_start:str
    reading3_correct:str
    writing1_start:str
    writing1_correct:str
    writing2_start: str
    writing2_correct: str
    sentence_upgrade_correct: str
    sentence_translation_start: str
    speaking_start: str

class PromptConfig(BaseModel):
    en:Prompts
    zh:Prompts


class Settings(BaseModel):
    app: AppConfig
    llm: LLMConfig
    prompt: PromptConfig


def resource_path(relative_path: str) -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / relative_path
    return Path(__file__).resolve().parents[0] / relative_path
    #              ↑ 回到 app/

def load_settings(path: str = "config/settings.yml") -> Settings:
    config_path = resource_path(path)
    with open(config_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return Settings(**data)

# 单例配置对象（全局可用）
settings = load_settings()
