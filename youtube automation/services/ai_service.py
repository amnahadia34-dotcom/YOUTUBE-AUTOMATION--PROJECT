from openai import OpenAI
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def _get_client(openai_client: Optional[OpenAI] = None) -> OpenAI:
    if openai_client is not None:
        return openai_client
    if not OPENAI_API_KEY:
        raise EnvironmentError("OPENAI_API_KEY is required for AI services.")
    return OpenAI(api_key=OPENAI_API_KEY)


def generate_script(topic: str, language: str = "English", openai_client: Optional[OpenAI] = None) -> str:
    client = _get_client(openai_client)
    prompt = f"""
You are a premium YouTube automation assistant.
Write a viral YouTube video script for the topic: {topic}
Language: {language}
Include:
- Hook
- Introduction
- 3 core scenes
- CTA
- Short subtitle-compatible lines
- Suggested SEO title, description, and tags section
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a professional YouTube script writer."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content


def optimize_text(
    text: str,
    task: str,
    topic: str = "",
    language: str = "English",
    openai_client: Optional[OpenAI] = None
) -> str:
    client = _get_client(openai_client)
    prompt = f"""
You are an AI YouTube optimization assistant.
Improve the following {task} for a YouTube creator in {language}.
Topic: {topic}

Text:
{text}

Return the improved {task} only.
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()
