import json
import os
from typing import Optional
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(dotenv_path=".env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def _get_client(openai_client: Optional[OpenAI] = None) -> OpenAI:
    if openai_client is not None:
        return openai_client
    if not OPENAI_API_KEY:
        raise EnvironmentError("OPENAI_API_KEY is required for SEO generation.")
    return OpenAI(api_key=OPENAI_API_KEY)


def _normalize_list(values):
    return [value.strip() for value in values if isinstance(value, str) and value.strip()]


def generate_seo_metadata(
    topic: str,
    script: str,
    language: str = "English",
    openai_client: Optional[OpenAI] = None
) -> dict:
    """Generate SEO title, description, hashtags, and tags for YouTube."""
    client = _get_client(openai_client)
    prompt = f"""
You are a YouTube SEO specialist.
Based on the topic "{topic}" and the script below, create:
- One strong SEO title under 70 characters
- A keyword-rich YouTube description with 2-3 paragraphs
- A list of 6 hashtags
- A list of 12 searchable tags
Language: {language}

Return valid JSON with keys: title, description, hashtags, tags

Script:
{script}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    raw_text = response.choices[0].message.content.strip()
    payload = {
        "raw": raw_text,
        "title": topic,
        "description": script[:500],
        "hashtags": [],
        "tags": []
    }

    try:
        parsed = json.loads(raw_text)
        payload["title"] = parsed.get("title", payload["title"]).strip()
        payload["description"] = parsed.get("description", payload["description"]).strip()
        payload["hashtags"] = _normalize_list(parsed.get("hashtags", []))
        payload["tags"] = _normalize_list(parsed.get("tags", []))
    except Exception:
        payload["description"] = raw_text
        if "#" in raw_text:
            payload["hashtags"] = [tag.strip() for tag in raw_text.split() if tag.startswith("#")]

    return payload
