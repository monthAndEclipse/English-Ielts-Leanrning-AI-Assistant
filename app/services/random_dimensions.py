# app/services/random_dimensions.py

import random

READING_DIMENSIONS = {
    "text_styles": [
        "informative", "historical", "expository", "research_summary",
        "biographical", "news_feature", "descriptive", "social_commentary"
    ],
    "tones": ["neutral", "positive", "critical", "mysterious", "awe", "contrast"],
    "time_frames": [
        "ancient", "middle_age", "19th_century", "modern", "future", "cross_era"
    ],
    "geographies": [
        "Asia", "Europe", "North America", "Africa", "South America",
        "Oceania", "multi_region", "fictional_country"
    ],
    "structures": [
        "problem_cause_solution", "chronological", "comparison",
        "topic_sentence_first", "progressive", "nested_explanation"
    ],
    "narrators": [
        "scientists", "locals", "students", "company", "researcher_story",
        "animals", "plants", "historical_figure"
    ],
    "example_types": [
        "real_case", "fictional_case", "historical_case",
        "modern_research", "nature_example", "engineering_example"
    ],
}

class RandomizerEngine:

    @staticmethod
    def pick_reading(dimensions: list[str], k: int = None) -> dict:
        """
        dimensions: ["text_styles", "tones", ...]
        k: 随机选几个，不传就全部
        return: {dim_name: random_value}
        """
        pool = dimensions.copy()

        if k:
            pool = random.sample(pool, min(k, len(pool)))

        return {dim: random.choice(READING_DIMENSIONS[dim]) for dim in pool}
