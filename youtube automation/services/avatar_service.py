import os
import uuid
from typing import Optional
from moviepy.editor import AudioFileClip, CompositeVideoClip, ColorClip, ImageClip, TextClip, concatenate_videoclips
from PIL import Image, ImageDraw
from utils.logger import logger


class AvatarService:
    """AI avatar generation and talking head video creation."""

    def __init__(self, output_dir: str = "renders"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        logger.info("Avatar Service initialized")

    def _create_avatar_card(self, subject: str, width: int = 1080, height: int = 1080) -> str:
        image_path = os.path.join(self.output_dir, f"avatar_card_{uuid.uuid4().hex}.png")
        background = Image.new("RGB", (width, height), (18, 24, 55))
        draw = ImageDraw.Draw(background)
        draw.ellipse((220, 180, 860, 820), fill=(255, 230, 120))
        draw.rectangle((420, 760, 660, 900), fill=(14, 19, 43))
        draw.text((260, 940), subject[:30], fill="white")
        background.save(image_path)
        return image_path

    def render_avatar_video(
        self,
        avatar_name: str,
        script: str,
        audio_path: str,
        duration: Optional[float] = None,
        output_path: Optional[str] = None
    ) -> str:
        if output_path is None:
            output_path = os.path.join(self.output_dir, f"avatar_{uuid.uuid4().hex}.mp4")

        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio path not found: {audio_path}")

        audio_clip = AudioFileClip(audio_path)
        duration = duration or audio_clip.duration
        text = script.strip().replace("\n", " ")[:220]
        scene_duration = duration
        avatar_image_path = self._create_avatar_card(avatar_name)

        background = ImageClip(avatar_image_path).set_duration(scene_duration).resize((1280, 720))
        caption = TextClip(text, fontsize=40, color="white", size=(1160, None), method="caption")
        caption = caption.set_position((60, 500)).set_duration(scene_duration)

        blink_clip = ColorClip((1280, 720), color=(18, 24, 55)).set_duration(0.25)
        avatar_clip = CompositeVideoClip([background, caption]).set_audio(audio_clip)
        avatar_clip.write_videofile(output_path, fps=24, audio_codec="aac", preset="medium")
        return output_path

    def create_custom_avatar(self, name: str, style: str, voice_id: str, output_dir: Optional[str] = None) -> dict:
        output_dir = output_dir or self.output_dir
        os.makedirs(output_dir, exist_ok=True)
        avatar_id = f"avatar_{uuid.uuid4().hex}"
        card_path = self._create_avatar_card(name)
        return {
            "avatar_id": avatar_id,
            "name": name,
            "style": style,
            "voice_id": voice_id,
            "card_path": card_path,
            "created_at": os.path.getctime(card_path)
        }
