import os
import uuid
from typing import Dict, Any, Optional
from agents.base_agent import BaseAgent, AgentRole
from services.video_service import generate_video, add_background_music_to_video
from services.voice_service import generate_voice
from services.avatar_service import AvatarService
from services.dubbing_service import DubbingService
from services.music_service import MusicService
from services.shorts_service import ShortsService
from utils.logger import logger


class VideoAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_id="video_agent", role=AgentRole.VIDEO)
        self.avatar_service = AvatarService()
        self.dubbing_service = DubbingService()
        self.music_service = MusicService()
        self.shorts_service = ShortsService()

    async def _think(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "script": input_data.get("script", ""),
            "language": input_data.get("language", "English"),
            "video_style": input_data.get("video_style", "cinematic"),
            "duration": input_data.get("duration", 180),
            "enable_avatar": input_data.get("enable_avatar", False),
            "enable_shorts": input_data.get("enable_shorts", True),
            "shorts_count": input_data.get("shorts_count", 3),
            "music_mood": input_data.get("music_mood", "motivational"),
            "music_genre": input_data.get("music_genre", "cinematic")
        }

    async def _execute(self, analysis: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
        output_data: Dict[str, Any] = {}
        script = analysis["script"]
        language = analysis["language"]
        audio_path = generate_voice(script, language)
        output_data["voice_path"] = audio_path

        if analysis["enable_avatar"]:
            avatar_path = self.avatar_service.render_avatar_video(
                avatar_name=input_data.get("avatar_name", "AI Host"),
                script=script,
                audio_path=audio_path,
                duration=analysis["duration"]
            )
            output_data["avatar_video_path"] = avatar_path
        else:
            output_data["avatar_video_path"] = None

        video_path = generate_video(
            script=script,
            audio_path=audio_path,
            scene_images=input_data.get("scene_images", []),
            subtitles=input_data.get("subtitles", []),
            intro_text=input_data.get("intro_text"),
            outro_text=input_data.get("outro_text"),
            output_path=os.path.join("renders", f"video_{uuid.uuid4().hex}.mp4")
        )
        output_data["video_path"] = video_path

        music_path = self.music_service.generate_background_music(
            duration=analysis["duration"],
            mood=analysis["music_mood"],
            genre=analysis["music_genre"],
            intensity=input_data.get("music_intensity", 0.65)
        )
        output_data["music_path"] = music_path

        mixed_video_path = add_background_music_to_video(
            video_path=video_path,
            music_path=music_path,
            output_path=os.path.join("renders", f"video_music_{uuid.uuid4().hex}.mp4")
        )
        output_data["mixed_video_path"] = mixed_video_path

        if analysis["enable_shorts"]:
            shorts_result = await self.shorts_service.generate_shorts_from_video(
                video_path=mixed_video_path,
                num_shorts=analysis["shorts_count"]
            )
            output_data["shorts"] = shorts_result

        return output_data

    async def _learn(self, input_data: Dict[str, Any], result: Dict[str, Any]):
        logger.info("VideoAgent completed rendering and learned from the result")
