import os
import uuid
from typing import Optional
from openai import OpenAI

from services.ai_service import generate_script, optimize_text
from services.caption_service import generate_caption_data
from services.seo_service import generate_seo_metadata
from services.thumbnail_service import create_ai_thumbnail
from services.voice_service import generate_voice
from services.subtitle_service import build_subtitles, write_subtitles_srt
from services.video_service import generate_video
from services.youtube_service import upload_video_real
from services.scheduler_service import schedule_upload


def _build_openai_client(api_key: str) -> OpenAI:
    if not api_key:
        raise ValueError("OpenAI API key is required for generation.")
    return OpenAI(api_key=api_key)


def run_generation_pipeline(payload: dict, task_id: str) -> dict:
    openai_client = _build_openai_client(payload["openai_api_key"])
    language = payload.get("language", "English")
    mode = payload.get("mode", "Full AI Auto Mode")
    topic = payload.get("topic", "")
    auto_upload = payload.get("auto_upload", False)
    schedule_publish = payload.get("schedule_publish", False)
    publish_at = payload.get("publish_at")
    privacy_status = payload.get("privacy_status", "public")
    manual_title = payload.get("manual_title", "")
    manual_description = payload.get("manual_description", "")
    manual_tags = payload.get("manual_tags", [])
    uploaded_video_path = payload.get("uploaded_video_path")
    uploaded_thumbnail_path = payload.get("uploaded_thumbnail_path")

    result = {
        "task_id": task_id,
        "topic": topic,
        "mode": mode,
        "status": "PROCESSING",
        "progress": 0,
        "video_path": None,
        "thumbnail_path": None,
        "youtube_url": None,
        "seo": {},
        "caption": {},
        "error": None
    }

    title = manual_title.strip() if manual_title else topic
    description = manual_description.strip() if manual_description else ""
    tags = manual_tags if isinstance(manual_tags, list) else [t.strip() for t in manual_tags.split(",") if t.strip()]

    if mode == "Full AI Auto Mode":
        script = generate_script(topic, language, openai_client)
        result["progress"] = 15
        result["seo"] = generate_seo_metadata(topic, script, language, openai_client)
        result["caption"] = generate_caption_data(topic, script, language, openai_client)
        result["progress"] = 35

        thumbnail_path = create_ai_thumbnail(topic, language, openai_client)
        result["thumbnail_path"] = thumbnail_path
        result["progress"] = 50

        voice_path = generate_voice(script, language)
        result["progress"] = 60

        subtitles = build_subtitles(script, language)
        subtitle_path = write_subtitles_srt(subtitles, os.path.join("outputs", f"subs_{uuid.uuid4().hex}.srt"))
        result["progress"] = 70

        video_path = generate_video(
            script=script,
            audio_path=voice_path,
            scene_images=[thumbnail_path] if thumbnail_path else None,
            subtitles=subtitles,
            intro_text=payload.get("intro_text", ""),
            outro_text=payload.get("outro_text", ""),
            output_path=os.path.join("outputs", f"video_{uuid.uuid4().hex}.mp4")
        )
        result["video_path"] = video_path
        result["progress"] = 85

        title = result["seo"].get("title", title)
        description = result["seo"].get("description", script)
        tags = result["seo"].get("tags", [])

    else:
        if not uploaded_video_path:
            raise ValueError("Manual mode requires a video upload.")

        result["video_path"] = uploaded_video_path
        result["thumbnail_path"] = uploaded_thumbnail_path
        result["progress"] = 30

        if not description:
            description = "Manual creator video prepared for upload."

        if not tags:
            result["caption"] = generate_caption_data(title, description, language, openai_client)
            result["seo"] = generate_seo_metadata(title, description, language, openai_client)
            tags = result["seo"].get("tags", [])
        else:
            result["caption"] = generate_caption_data(title, description, language, openai_client)
            result["seo"] = generate_seo_metadata(title, description, language, openai_client)

        if not uploaded_thumbnail_path and payload.get("use_ai_thumbnail", False):
            thumbnail_path = create_ai_thumbnail(title, language, openai_client)
            result["thumbnail_path"] = thumbnail_path
            result["progress"] = 55

    if schedule_publish:
        schedule_upload(
            result["video_path"],
            title,
            description,
            publish_at,
            privacy_status
        )
        result["status"] = "SCHEDULED"
        result["progress"] = 100
    elif auto_upload:
        result["status"] = "UPLOADING"
        result["progress"] = 90
        result["youtube_url"] = upload_video_real(
            result["video_path"],
            title,
            description,
            tags=tags,
            privacy_status=privacy_status
        )
        result["progress"] = 100
    else:
        result["status"] = "COMPLETED"
        result["progress"] = 100

    return result
