import os
import uuid
from typing import Dict, List, Optional
from openai import OpenAI
from gtts import gTTS
from moviepy.editor import AudioFileClip, VideoFileClip
from config.settings import OPENAI_API_KEY, FAST_LLM_MODEL
from utils.logger import logger

LANGUAGE_MAP = {
    "english": "en",
    "urdu": "ur",
    "hindi": "hi",
    "arabic": "ar",
    "spanish": "es",
    "french": "fr"
}


def _language_code(language: str) -> str:
    return LANGUAGE_MAP.get(language.lower(), "en")


class DubbingService:
    """Multilingual dubbing and localized video version generation."""

    def __init__(self, output_dir: str = "renders"):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        logger.info("Dubbing Service initialized")

    def translate_script(self, script: str, source_language: str, target_language: str) -> str:
        prompt = f"""
You are a translation specialist.
Translate the following YouTube script from {source_language} to {target_language}.
Preserve tone, timing, and audience intent.
Return only the translated text.

SCRIPT:
{script}
"""
        response = self.client.chat.completions.create(
            model=FAST_LLM_MODEL,
            messages=[
                {"role": "system", "content": "You are a professional translator."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
            max_tokens=1200
        )
        return response.choices[0].message.content.strip()

    def generate_dubbed_audio(
        self,
        script: str,
        language: str = "english",
        output_dir: Optional[str] = None
    ) -> str:
        output_dir = output_dir or self.output_dir
        os.makedirs(output_dir, exist_ok=True)
        locale = _language_code(language)
        safe_text = script.strip()[:4000]
        tts = gTTS(text=safe_text, lang=locale)
        output_path = os.path.join(output_dir, f"dubbed_{language}_{uuid.uuid4().hex}.mp3")
        tts.save(output_path)
        return output_path

    def create_dubbed_video(
        self,
        video_path: str,
        dubbed_audio_path: str,
        target_language: str,
        output_dir: Optional[str] = None
    ) -> str:
        output_dir = output_dir or self.output_dir
        os.makedirs(output_dir, exist_ok=True)
        if not os.path.exists(video_path):
            raise FileNotFoundError("Input video path not found.")
        if not os.path.exists(dubbed_audio_path):
            raise FileNotFoundError("Dubbed audio path not found.")

        video_clip = VideoFileClip(video_path)
        audio_clip = AudioFileClip(dubbed_audio_path)
        combined = video_clip.set_audio(audio_clip.set_duration(video_clip.duration))
        output_path = os.path.join(output_dir, f"dubbed_video_{target_language}_{uuid.uuid4().hex}.mp4")
        combined.write_videofile(output_path, fps=video_clip.fps, audio_codec="aac", preset="medium")
        video_clip.close()
        audio_clip.close()
        return output_path

    def create_multilingual_versions(
        self,
        video_path: str,
        original_script: str,
        languages: List[str]
    ) -> Dict[str, str]:
        output = {}

        for language in languages:
            translated_script = self.translate_script(original_script, "English", language)
            dubbed_audio = self.generate_dubbed_audio(translated_script, language)
            dubbed_video = self.create_dubbed_video(video_path, dubbed_audio, language)
            output[language] = dubbed_video

        return output
