import os
import time
import uuid
import logging
import requests
from typing import Optional
from config.settings import HF_TOKEN

logger = logging.getLogger(__name__)
HF_CACHE_DIR = "cache/hf_videos"
MODEL_CANDIDATES = ["Wan-2.1", "LTX Video", "CogVideoX"]

os.makedirs(HF_CACHE_DIR, exist_ok=True)
logger.info(f"huggingface_video_service initialized with HF_TOKEN: {bool(HF_TOKEN)}")


def _get_headers():
    headers = {"Accept": "application/octet-stream"}
    if HF_TOKEN:
        headers["Authorization"] = f"Bearer {HF_TOKEN}"
    return headers


def _model_status(model_id: str) -> bool:
    url = f"https://api-inference.huggingface.co/models/{model_id}"
    try:
        response = requests.get(url, headers=_get_headers(), timeout=10)
        return response.status_code == 200
    except Exception:
        return False


def _download_video_bytes(model_id: str, prompt: str, duration: int) -> Optional[bytes]:
    url = f"https://api-inference.huggingface.co/models/{model_id}"
    payload = {
        "inputs": prompt,
        "parameters": {
            "duration": duration,
            "video_length": duration,
            "num_inference_steps": 28,
            "guidance_scale": 7.5
        },
        "options": {"wait_for_model": True}
    }
    try:
        response = requests.post(url, headers=_get_headers(), json=payload, timeout=120)
        if response.status_code == 200 and response.content:
            content_type = response.headers.get("content-type", "")
            if "application/json" in content_type:
                data = response.json()
                if isinstance(data, dict) and data.get("error"):
                    raise RuntimeError(data.get("error"))
            return response.content
        raise RuntimeError(f"Hugging Face returned status {response.status_code}")
    except Exception as exc:
        raise RuntimeError(f"HF model {model_id} failed: {exc}") from exc


def _save_video_bytes(video_bytes: bytes, prompt: str) -> str:
    output_path = os.path.join(HF_CACHE_DIR, f"hf_{uuid.uuid4().hex[:8]}.mp4")
    with open(output_path, "wb") as out_file:
        out_file.write(video_bytes)
    logger.info(f"Saved HF video to {output_path}")
    return output_path


def _build_ai_prompt(scene_text: str) -> str:
    qualifier = (
        "cinematic documentary style, professional camera movement, ultra realistic, "
        "4k, high detail, Netflix style, dramatic lighting"
    )
    base = scene_text.strip()
    if not base.endswith("."):
        base = base + "."
    return f"{base} {qualifier}"


def generate_ai_video(prompt: str, duration: int = 3) -> Optional[str]:
    """Generate an AI video from Hugging Face with the first available model (3s max for memory safety)."""
    if not HF_TOKEN:
        raise RuntimeError("HF_TOKEN is not set")

    start_time = time.time()
    last_error = None

    for model_id in MODEL_CANDIDATES:
        try:
            if not _model_status(model_id):
                logger.warning(f"HF model unavailable: {model_id}")
                continue
            logger.info(f"Using HF model {model_id} for prompt")
            video_bytes = _download_video_bytes(model_id, prompt, duration)
            output_path = _save_video_bytes(video_bytes, prompt)
            elapsed = time.time() - start_time
            logger.info(f"Generated AI video with {model_id} in {elapsed:.1f}s")
            return output_path
        except Exception as exc:
            last_error = exc
            logger.warning(f"HF generation failed for {model_id}: {exc}")

    raise RuntimeError(f"All HF models failed: {last_error}")


def should_use_ai_video(scene_text: str) -> bool:
    """Decide whether a scene is better served by AI-generated video (disabled in memory-safe mode)."""
    # Disabled AI video generation for memory safety
    return False
    # text = (scene_text or "").lower()
    ai_triggers = [
        "future", "fantasy", "sci-fi", "science fiction", "ancient", "mythical",
        "dragon", "space", "alien", "dystopian", "utopian", "futuristic",
        "historical", "civilization", "epic", "mystical", "legendary",
        "magic", "myth", "mythology", "galaxy", "cosmic", "supernatural"
    ]
    real_triggers = [
        "business", "office", "car", "cars", "factory", "factories", "technology",
        "people", "work", "entrepreneur", "startup", "meeting", "finance",
        "building", "corporate", "team", "industry"
    ]
    if any(token in text for token in ai_triggers):
        return True
    if any(token in text for token in real_triggers):
        return False
    # default to Pexels when uncertain
    return False
