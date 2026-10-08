from gtts import gTTS
import os

LANGUAGE_MAP = {
    "English": "en",
    "Urdu": "ur",
    "Roman Urdu": "ur",
    "Hindi": "hi",
    "Arabic": "ar",
    "Spanish": "es"
}


def generate_voice(script: str, language: str = "English", output_dir: str = "outputs") -> str:
    os.makedirs(output_dir, exist_ok=True)
    locale = LANGUAGE_MAP.get(language, "en")
    safe_text = script.strip()[:4000]

    tts = gTTS(text=safe_text, lang=locale)
    output_path = os.path.join(output_dir, "voice_{}.mp3".format(os.urandom(8).hex()))
    tts.save(output_path)
    return output_path
