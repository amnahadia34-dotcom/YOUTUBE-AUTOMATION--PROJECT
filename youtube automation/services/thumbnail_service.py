import base64
import os
import uuid
from typing import Optional
from PIL import Image, ImageDraw, ImageFont
from openai import OpenAI
from config.settings import OPENAI_API_KEY
from utils.logger import logger


def _build_thumbnail_prompt(topic: str, language: str):
    return (
        f"Create a cinematic YouTube thumbnail for the topic '{topic}'. "
        f"Use high contrast, bold headline copy, and a strong emotional hook in {language}. "
        "Return design guidance rather than file data."
    )


def _create_local_thumbnail(topic: str, language: str, output_dir: str) -> str:
    os.makedirs(output_dir, exist_ok=True)
    image_path = os.path.join(output_dir, f"thumbnail_local_{uuid.uuid4().hex}.png")
    width, height = 1280, 720
    background = Image.new("RGB", (width, height), (18, 24, 55))
    draw = ImageDraw.Draw(background)

    title = topic[:40].upper()
    subtitle = f"{language.title()} · AI Media" if language else "AI Media"
    draw.rectangle([0, 0, width, height], fill=(18, 24, 55))
    draw.rectangle([40, 40, width - 40, height - 40], outline=(255, 255, 255), width=4)
    draw.text((60, 80), title, fill="white")
    draw.text((60, 160), subtitle, fill=(220, 220, 220))

    background.save(image_path, quality=90)
    return image_path


def create_ai_thumbnail(topic: str, language: str = "English", openai_client: Optional[OpenAI] = None, output_dir: str = "outputs") -> str:
    client = openai_client or OpenAI(api_key=OPENAI_API_KEY)
    os.makedirs(output_dir, exist_ok=True)

    try:
        prompt = _build_thumbnail_prompt(topic, language)
        response = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="1024x1024"
        )
        image_base64 = response.data[0].b64_json
        image_bytes = base64.b64decode(image_base64)
        image_path = os.path.join(output_dir, f"thumbnail_{uuid.uuid4().hex}.png")
        with open(image_path, "wb") as image_file:
            image_file.write(image_bytes)
        return image_path
    except Exception as exc:
        logger.warning(f"OpenAI thumbnail generation failed, using local fallback: {exc}")
        return _create_local_thumbnail(topic, language, output_dir)
