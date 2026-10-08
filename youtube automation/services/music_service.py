import os
import uuid
from typing import Dict, Any
import numpy as np
import soundfile as sf
from moviepy.editor import AudioFileClip, CompositeAudioClip
from config.settings import AUDIO_SAMPLE_RATE, AUDIO_CHANNELS
from utils.logger import logger


class MusicService:
    """AI-backed music composition and background audio generation."""

    def __init__(self, output_dir: str = "renders"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        logger.info("Music Service initialized")

    def _wave(self, frequency: float, duration: float, amplitude: float = 0.35):
        sample_count = int(AUDIO_SAMPLE_RATE * duration)
        t = np.linspace(0, duration, sample_count, False)
        return amplitude * np.sin(2 * np.pi * frequency * t)

    def generate_background_music(
        self,
        duration: float = 120,
        mood: str = "motivational",
        genre: str = "corporate",
        tempo_bpm: int = 100,
        intensity: float = 0.6
    ) -> str:
        mood_map = {
            "epic": 110,
            "calm": 440,
            "energetic": 660,
            "dramatic": 220,
            "motivational": 330,
            "cinematic": 260
        }
        base_freq = mood_map.get(mood.lower(), 330)
        melody = self._wave(base_freq, duration, amplitude=0.32 * intensity)
        harmony = self._wave(base_freq * 1.5, duration, amplitude=0.18 * intensity)
        bass = self._wave(base_freq * 0.5, duration, amplitude=0.12 * intensity)
        combined = melody + harmony + bass
        combined = combined / np.max(np.abs(combined)) * 0.9

        stereo = np.column_stack([combined, combined])
        output_path = os.path.join(self.output_dir, f"music_{uuid.uuid4().hex}.wav")
        sf.write(output_path, stereo, AUDIO_SAMPLE_RATE)
        return output_path

    def generate_emotion_matched_music(self, script_emotions: Any, video_duration: float) -> str:
        intensity = 0.7
        mood = "motivational"
        return self.generate_background_music(duration=video_duration, mood=mood, intensity=intensity)

    def generate_scene_music(self, scene: Dict[str, Any]) -> str:
        duration = float(scene.get("duration", 10))
        mood = scene.get("music","cinematic")
        return self.generate_background_music(duration=duration, mood=mood)

    def composite_music_with_video(self, video_path: str, music_path: str, output_path: str) -> str:
        if not os.path.exists(video_path) or not os.path.exists(music_path):
            raise FileNotFoundError("Video or music file missing for composition.")

        from moviepy.editor import VideoFileClip

        clip = VideoFileClip(video_path)
        music_clip = AudioFileClip(music_path).volumex(0.35)
        final = clip.set_audio(music_clip.set_duration(clip.duration))
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        final.write_videofile(output_path, fps=clip.fps, audio_codec="aac", preset="medium")
        clip.close()
        music_clip.close()
        return output_path
