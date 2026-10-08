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
        raise EnvironmentError("OPENAI_API_KEY is required for caption generation.")
    return OpenAI(api_key=OPENAI_API_KEY)


def _normalize_hashtags(raw_hashtags):
    normalized = []
    for tag in raw_hashtags:
        if not tag:
            continue

        text = tag.strip().lstrip("#").replace(" ", "")
        if text:
            normalized.append(f"#{text}")

    return normalized


def generate_caption_data(
    topic: str,
    script: str,
    language: str = "English",
    openai_client: Optional[OpenAI] = None
) -> dict:
    """Generate a viral caption, hashtags, and platform-ready caption formatting."""
    client = _get_client(openai_client)
    prompt = f"""
You are a YouTube caption expert.
Based on the topic "{topic}" and the following video script, create:
1) A viral caption that hooks viewers
2) A formatted caption ready for YouTube description text
3) A list of 10 high-impact hashtags
4) A short call-to-action line for viewers
Language: {language}

Script:
{script}

Return a JSON object with keys: caption, formatted_caption, hashtags, cta
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    raw_text = response.choices[0].message.content.strip()
    payload = {
        "raw": raw_text,
        "caption": raw_text,
        "formatted_caption": raw_text,
        "hashtags": [],
        "cta": ""
    }

    try:
        parsed = json.loads(raw_text)
        payload["caption"] = parsed.get("caption", payload["caption"])
        payload["formatted_caption"] = parsed.get("formatted_caption", payload["formatted_caption"])
        payload["cta"] = parsed.get("cta", payload["cta"])
        payload["hashtags"] = _normalize_hashtags(parsed.get("hashtags", []))
    except Exception:
        if "#" in raw_text:
            payload["hashtags"] = [tag.strip() for tag in raw_text.split() if tag.startswith("#")]
        payload["formatted_caption"] = raw_text

    return payload
