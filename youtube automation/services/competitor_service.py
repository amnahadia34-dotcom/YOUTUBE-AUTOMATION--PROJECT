import json
from typing import Dict, List, Optional
from config.settings import OPENAI_API_KEY, FAST_LLM_MODEL
from openai import OpenAI
from utils.logger import logger


def _safe_json_load(text: str, fallback: Dict) -> Dict:
    try:
        return json.loads(text)
    except Exception:
        logger.warning("CompetitorService returned unexpected text, using fallback.")
        return fallback


class CompetitorService:
    """Competitor analysis for channel-level benchmarking."""

    def __init__(self, client: Optional[OpenAI] = None):
        self.client = client or OpenAI(api_key=OPENAI_API_KEY)

    async def analyze_competitors(
        self,
        topic: str,
        competitor_channels: Optional[List[str]] = None,
        language: str = "English"
    ) -> Dict[str, any]:
        channels = competitor_channels or []
        channel_list = ", ".join(channels) if channels else "top creators in the niche"
        prompt = f"""
You are a competitive intelligence analyst for YouTube.
Analyze the niche for topic '{topic}' and compare the strengths, weaknesses, and content gaps of the following channels: {channel_list}.
Return valid JSON with keys: competitors, opportunity_gaps, theme_strengths, recommended_improvements.
Language: {language}
"""
        response = self.client.chat.completions.create(
            model=FAST_LLM_MODEL,
            messages=[
                {"role": "system", "content": "You are a market research analyst."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=650
        )
        raw_text = response.choices[0].message.content.strip()
        parsed = _safe_json_load(raw_text, {
            "competitors": [],
            "opportunity_gaps": [],
            "theme_strengths": [],
            "recommended_improvements": []
        })
        return parsed
