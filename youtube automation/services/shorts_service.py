"""
SHORTS REPURPOSING ENGINE - AI Shorts Generation

Responsibilities:
- Convert long videos into vertical shorts
- Generate captions for shorts
- Generate hooks for maximum engagement
- Create TikTok/Instagram Reels format
- Auto vertical formatting
"""

import json
import os
from typing import Dict, List, Any, Optional
from config.settings import SHORTS_DIR, SHORTS_RESOLUTION, SHORTS_MAX_DURATION, OPENAI_API_KEY
from utils.logger import logger
from openai import OpenAI


class ShortsService:
    """
    Converts horizontal videos into vertical shorts for maximum reach
    """

    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.shorts_dir = SHORTS_DIR
        os.makedirs(self.shorts_dir, exist_ok=True)
        logger.info("Shorts Service initialized")

    async def generate_shorts_from_video(
        self,
        video_path: str,
        num_shorts: int = 3,
        max_duration: float = SHORTS_MAX_DURATION
    ) -> Dict[str, Any]:
        try:
            from moviepy.editor import VideoFileClip

            logger.info(f"Generating {num_shorts} shorts from video")
            video = VideoFileClip(video_path)
            video_duration = video.duration
            segment_duration = min(max_duration, video_duration / num_shorts)

            shorts_list = []
            for index in range(num_shorts):
                start = min(video_duration, (video_duration / num_shorts) * index)
                end = min(video_duration, start + segment_duration)
                short = await self._extract_and_process_short(video_path, start, end, index + 1)
                shorts_list.append(short)

            video.close()
            return {"status": "success", "total_shorts": len(shorts_list), "shorts": shorts_list}

        except Exception as e:
            logger.error(f"Shorts generation failed: {e}")
            return {"status": "failed", "error": str(e)}

    async def _extract_and_process_short(
        self,
        video_path: str,
        start_time: float,
        end_time: float,
        short_number: int
    ) -> Dict[str, Any]:
        try:
            from moviepy.editor import VideoFileClip

            logger.info(f"Processing short {short_number}: {start_time}-{end_time}")
            clip = VideoFileClip(video_path).subclip(start_time, end_time)
            height = clip.h
            width = int(height * SHORTS_RESOLUTION[0] / SHORTS_RESOLUTION[1])
            cropped = clip.crop(
                width=width,
                height=height,
                x_center=clip.w // 2,
                y_center=clip.h // 2
            )

            output_path = os.path.join(self.shorts_dir, f"short_{short_number}_{int(start_time)}_{int(end_time)}.mp4")
            cropped.write_videofile(output_path, fps=30, audio_codec="aac", preset="medium")
            clip.close()
            cropped.close()

            return {
                "short_number": short_number,
                "path": output_path,
                "duration": end_time - start_time,
                "resolution": SHORTS_RESOLUTION
            }

        except Exception as e:
            logger.error(f"Short process failed: {e}")
            return {"short_number": short_number, "error": str(e)}

    async def generate_shorts_captions(self, script: Dict[str, Any], shorts_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        captions = []
        for idx, short in enumerate(shorts_data, 1):
            captions.append(await self._generate_short_caption(script, idx, short))
        return {"status": "success", "captions": captions}

    async def _generate_short_caption(self, script: Dict[str, Any], short_number: int, short_data: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""
Generate a viral caption for a short clip.
Topic: {script.get('topic', 'Unknown')}
Scene duration: {short_data.get('duration', 10)} seconds
Return JSON with keys: tiktok, instagram, youtube, hashtags, call_to_action
"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert social media copywriter."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=250
            )
            payload = json.loads(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"Short caption generation failed: {e}")
            payload = {
                "tiktok": f"Watch this clip about {script.get('topic')}",
                "instagram": f"Short clip about {script.get('topic')}.",
                "youtube": f"A quick highlight from {script.get('topic')}.",
                "hashtags": ["#shorts", "#viral"],
                "call_to_action": "Like and subscribe for more."
            }

        return {"short_number": short_number, "captions": payload}

    async def generate_shorts_hooks(self, shorts_data: List[Dict[str, Any]]) -> List[str]:
        prompt = f"""
Generate {len(shorts_data)} attention-grabbing hooks for shorts.
Return only a JSON array of hooks.
"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a short-form hook strategist."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.85,
                max_tokens=200
            )
            hooks = json.loads(response.choices[0].message.content)
            return hooks if isinstance(hooks, list) else []
        except Exception as e:
            logger.error(f"Shorts hooks generation failed: {e}")
            return ["Watch this!", "Must-see moment.", "You won't believe this."]

    async def add_text_overlays(self, short_path: str, text_elements: List[Dict[str, Any]]) -> str:
        try:
            from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip

            clip = VideoFileClip(short_path)
            overlays = []
            for element in text_elements:
                overlay = TextClip(
                    element.get("text", ""),
                    fontsize=40,
                    color="white",
                    size=(clip.w - 80, None),
                    method="caption"
                ).set_position((40, 40)).set_duration(clip.duration)
                overlays.append(overlay)

            final = CompositeVideoClip([clip, *overlays])
            output_path = short_path.replace(".mp4", "_text.mp4")
            final.write_videofile(output_path, fps=clip.fps, audio_codec="aac", preset="medium")
            clip.close()
            return output_path

        except Exception as e:
            logger.error(f"Text overlay failed: {e}")
            return short_path

    async def optimize_for_platform(self, short_path: str, platform: str) -> str:
        try:
            from moviepy.editor import VideoFileClip

            clip = VideoFileClip(short_path)
            if platform.lower() in ["tiktok", "instagram", "youtube"]:
                aspect = SHORTS_RESOLUTION
                output_path = short_path.replace(".mp4", f"_{platform.lower()}.mp4")
                clip_resized = clip.resize(height=aspect[1]).crop(width=aspect[0], height=aspect[1], x_center=clip.w // 2, y_center=clip.h // 2)
                clip_resized.write_videofile(output_path, fps=clip.fps, audio_codec="aac", preset="medium")
                clip.close()
                clip_resized.close()
                return output_path

            clip.close()
            return short_path

        except Exception as e:
            logger.error(f"Platform optimization failed: {e}")
            return short_path


_shorts_service = None



def get_shorts_service() -> ShortsService:
    """Get or create shorts service"""
    global _shorts_service
    if _shorts_service is None:
        _shorts_service = ShortsService()
    return _shorts_service
