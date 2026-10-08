import json
from typing import Dict, List, Optional
from config.settings import OPENAI_API_KEY, FAST_LLM_MODEL
from openai import OpenAI
from utils.logger import logger


def _parse_json_response(raw_text: str, fallback: Dict = None) -> Dict:
    fallback = fallback or {}
    try:
        return json.loads(raw_text)
    except Exception:
        logger.warning("TopicService could not parse JSON response, returning fallback.")
        return fallback


class TopicService:
    """Topic intelligence and research for autonomous generation."""

    def __init__(self, client: Optional[OpenAI] = None):
        self.client = client or OpenAI(api_key=OPENAI_API_KEY)

    async def suggest_topics(self, seed_topic: str, language: str = "English") -> Dict[str, any]:
        prompt = f"""
You are a professional content strategist for YouTube.
Given the seed idea: '{seed_topic}', generate 3 high-potential niche topics, a 2-sentence trend insight for each, and an estimated audience interest score between 0.0 and 1.0.
Language: {language}
Return valid JSON with keys: topics, insights, scores
"""
        response = self.client.chat.completions.create(
            model=FAST_LLM_MODEL,
            messages=[
                {"role": "system", "content": "You are a trend prediction and topic research assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=500
        )
        raw_text = response.choices[0].message.content.strip()
        parsed = _parse_json_response(raw_text, fallback={
            "topics": [seed_topic],
            "insights": ["Use existing channel strengths."],
            "scores": [0.5]
        })
        return {
            "seed_topic": seed_topic,
            "suggested_topics": parsed.get("topics", [seed_topic]),
            "insights": parsed.get("insights", []),
            "scores": parsed.get("scores", [])
        }

    async def research_topic(self, topic: str, language: str = "English") -> Dict[str, any]:
        prompt = f"""
You are a YouTube research analyst.
Analyze the topic '{topic}' and return:
1. Why it is trending.
2. The top 3 competitor strengths.
3. Best publishing window.
4. Audience intent profile.
Language: {language}
Return valid JSON with keys: trend_summary, opportunity, competitor_signals, best_publish_window, audience_intent
"""
        response = self.client.chat.completions.create(
            model=FAST_LLM_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert in YouTube trend analytics."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=600
        )
        raw_text = response.choices[0].message.content.strip()
        parsed = _parse_json_response(raw_text, fallback={
            "trend_summary": "The topic is experiencing strong interest.",
            "opportunity": "Create a gripping cinematic overview.",
            "competitor_signals": [],
            "best_publish_window": "weekday evenings",
            "audience_intent": "educational and inspirational"
        })
        return parsed
