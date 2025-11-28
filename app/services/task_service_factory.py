from app.services.synonym_service import SynonymPromptService
from app.services.sentence_service import SentencePromptService
from app.services.paragraph_service import ParagraphPromptService
from app.services.summary_service import SummaryPromptService
from app.services.reading1_service import Reading1PromptService
from app.services.reading2_service import Reading2PromptService
from app.services.reading3_service import Reading3PromptService
from app.services.writing1_service import Writing1PromptService
from app.services.writing2_service import Writing2PromptService
from app.services.sentence_upgrade_service import SentenceUpgradePromptService
from app.services.sentence_translation_serivce import SentenceTranslationPromptService
from app.services.speaking_service import SpeakingPromptService

def get_prompt_service(task_type):
    if task_type == "synonym":
        return SynonymPromptService()
    if task_type == "sentence":
        return SentencePromptService()
    if task_type == "paragraph":
        return ParagraphPromptService()
    if task_type == "summary":
        return SummaryPromptService()
    if task_type == "reading1":
        return Reading1PromptService()
    if task_type == "reading2":
        return Reading2PromptService()
    if task_type == "reading3":
        return Reading3PromptService()
    if task_type == "writing1":
        return Writing1PromptService()
    if task_type == "writing2":
        return Writing2PromptService()
    if task_type == "sentence_upgrade":
        return SentenceUpgradePromptService()
    if task_type == "sentence_translation":
        return SentenceTranslationPromptService()
    if task_type == "speaking":
        return SpeakingPromptService()
    # ……按需继续扩展
    else:
        raise ValueError(f"未知任务类型: {task_type}")
