"""
AI Shorts Auto-Generation Engine
Automatically detects viral moments, extracts clips, and creates TikTok/YouTube Shorts
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import asyncio
import openai
import cv2
import numpy as np
from moviepy.editor import VideoFileClip, concatenate_videoclips, speedx
from config.settings import (
    OPENAI_API_KEY, SHORTS_RESOLUTION, SHORTS_MAX_DURATION,
    SHORTS_DIR, MAIN_LLM_MODEL, VISION_MODEL
)
from utils.logger import logger


class ViralMomentType(str, Enum):
    PEAK_ENERGY = "peak_energy"
    PUNCHLINE = "punchline"
    REVELATION = "revelation"
    VISUAL_PEAK = "visual_peak"
    EMOTIONAL_CLIMAX = "emotional_climax"
    TRANSFORMATION = "transformation"


@dataclass
class ViralMoment:
    """Detected viral moment in video"""
    start_time: float
    end_time: float
    duration: float
    moment_type: ViralMomentType
    confidence_score: float  # 0-100
    description: str
    text_overlay: Optional[str]
    hooks_needed: List[str]


class ShortsEngine:
    """
    AI-powered shorts generation
    
    Features:
    - Automatic viral moment detection
    - Fast-paced clip generation
    - Vertical formatting (9:16)
    - Subtitle generation
    - Hook injection
    - Caption overlays with emojis
    - Speed ramping for emphasis
    - Auto-vertical transitions
    - Ending hooks for engagement
    """
    
    def __init__(self):
        self.openai_client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)
        self.shorts_dir = SHORTS_DIR
    
    async def extract_shorts_from_video(
        self,
        video_path: str,
        num_shorts: int = 3,
        output_dir: Optional[str] = None
    ) -> List[str]:
        """
        Automatically extract shorts from long-form video
        """
        
        try:
            logger.info(f"Extracting {num_shorts} shorts from: {video_path}")
            
            if not output_dir:
                output_dir = self.shorts_dir
            
            # Step 1: Analyze video for viral moments
            viral_moments = await self._detect_viral_moments(video_path, num_shorts)
            
            logger.info(f"Detected {len(viral_moments)} viral moments")
            
            # Step 2: Extract and process each moment
            shorts_paths = []
            for i, moment in enumerate(viral_moments):
                try:
                    short_path = await self._create_short_from_moment(
                        video_path=video_path,
                        moment=moment,
                        short_number=i + 1,
                        output_dir=output_dir
                    )
                    shorts_paths.append(short_path)
                except Exception as e:
                    logger.error(f"Error creating short {i+1}: {str(e)}")
                    continue
            
            logger.info(f"Successfully created {len(shorts_paths)} shorts")
            return shorts_paths
            
        except Exception as e:
            logger.error(f"Error extracting shorts: {str(e)}")
            raise
    
    async def _detect_viral_moments(self, video_path: str,
                                    num_moments: int = 3) -> List[ViralMoment]:
        """
        Use AI to detect viral moments in video
        """
        
        try:
            video = VideoFileClip(video_path)
            duration = video.duration
            
            prompt = f"""
            Analyze this YouTube video for viral shorts moments.
            
            Video Duration: {duration:.0f} seconds
            Target: Find {num_moments} best moments for TikTok/YouTube Shorts
            
            Identify moments that are:
            - Attention-grabbing (first 3 seconds crucial)
            - Self-contained narratively
            - Fast-paced and energetic
            - Emotionally impactful
            - Quotable or share-worthy
            
            For each moment provide:
            - Start time (seconds)
            - End time (seconds)
            - Moment type (peak_energy, punchline, revelation, etc)
            - Why it's viral
            - Suggested text overlay/caption
            - Suggested ending hook/CTA
            
            Return JSON:
            {{
                "moments": [
                    {{
                        "start_time": 10.5,
                        "end_time": 20.0,
                        "moment_type": "peak_energy",
                        "description": "...",
                        "text_overlay": "...",
                        "hooks_needed": ["..."]
                    }}
                ]
            }}
            """
            
            response = await self.openai_client.chat.completions.create(
                model=MAIN_LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                response_format={"type": "json_object"}
            )
            
            moments_data = json.loads(response.choices[0].message.content)
            
            viral_moments = []
            for moment_data in moments_data.get("moments", []):
                start = moment_data["start_time"]
                end = moment_data["end_time"]
                
                moment = ViralMoment(
                    start_time=start,
                    end_time=end,
                    duration=end - start,
                    moment_type=ViralMomentType(moment_data.get("moment_type", "peak_energy")),
                    confidence_score=85.0,
                    description=moment_data.get("description", ""),
                    text_overlay=moment_data.get("text_overlay"),
                    hooks_needed=moment_data.get("hooks_needed", [])
                )
                
                viral_moments.append(moment)
            
            video.close()
            
            return viral_moments[:num_moments]
            
        except Exception as e:
            logger.error(f"Error detecting viral moments: {str(e)}")
            return []
    
    async def _create_short_from_moment(
        self,
        video_path: str,
        moment: ViralMoment,
        short_number: int,
        output_dir: str
    ) -> str:
        """
        Create a polished short from viral moment
        """
        
        try:
            video = VideoFileClip(video_path)
            
            # Extract clip
            clip = video.subclip(moment.start_time, moment.end_time)
            
            # Speed up slightly for more impact (but not too much)
            if moment.moment_type == ViralMomentType.PEAK_ENERGY:
                clip = speedx(clip, 1.1)
            elif moment.moment_type == ViralMomentType.PUNCHLINE:
                clip = speedx(clip, 1.05)
            
            # Resize to vertical (9:16)
            clip = self._resize_to_vertical(clip)
            
            # Add captions
            clip = await self._add_shorts_captions(clip, moment)
            
            # Add hook at end
            if moment.hooks_needed:
                clip = self._add_ending_hook(clip, moment.hooks_needed)
            
            # Export
            output_path = f"{output_dir}/short_{short_number:02d}.mp4"
            clip.write_videofile(
                output_path,
                fps=30,
                codec='libx264',
                audio_codec='aac',
                verbose=False,
                logger=None
            )
            
            clip.close()
            video.close()
            
            logger.info(f"Short created: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error creating short: {str(e)}")
            raise
    
    def _resize_to_vertical(self, clip: VideoFileClip) -> VideoFileClip:
        """Resize clip to vertical format (1080x1920)"""
        
        # Get original dimensions
        w, h = clip.size
        aspect_ratio = w / h
        target_aspect = 9 / 16  # vertical
        
        if aspect_ratio > target_aspect:
            # Crop width
            new_w = int(h * target_aspect)
            left = (w - new_w) // 2
            clip = clip.crop(x1=left, x2=left + new_w)
        else:
            # Crop height
            new_h = int(w / target_aspect)
            top = (h - new_h) // 2
            clip = clip.crop(y1=top, y2=top + new_h)
        
        # Resize to final dimensions
        clip = clip.resize(newsize=(SHORTS_RESOLUTION[0], SHORTS_RESOLUTION[1]))
        
        return clip
    
    async def _add_shorts_captions(self, clip: VideoFileClip,
                                  moment: ViralMoment) -> VideoFileClip:
        """
        Add engaging captions with emojis for shorts
        """
        
        try:
            from moviepy.editor import TextClip, CompositeVideoClip
            
            if not moment.text_overlay:
                return clip
            
            # Create caption with emoji potential
            caption_text = moment.text_overlay
            
            # Add emoji suggestion based on moment type
            emoji_map = {
                ViralMomentType.PEAK_ENERGY: "🔥",
                ViralMomentType.PUNCHLINE: "😂",
                ViralMomentType.REVELATION: "😲",
                ViralMomentType.EMOTIONAL_CLIMAX: "😭",
                ViralMomentType.TRANSFORMATION: "✨"
            }
            
            emoji = emoji_map.get(moment.moment_type, "👀")
            
            # Create text
            txt_clip = TextClip(
                f"{emoji} {caption_text}",
                fontsize=60,
                color='white',
                font='Arial-Bold',
                method='caption',
                size=(SHORTS_RESOLUTION[0] - 40, None)
            ).set_duration(clip.duration)
            
            # Center position
            txt_clip = txt_clip.set_position(('center', 'center'))
            
            # Fade in/out
            txt_clip = txt_clip.crossfadein(0.2).crossfadeout(0.2)
            
            return CompositeVideoClip([clip, txt_clip])
            
        except Exception as e:
            logger.error(f"Error adding captions: {str(e)}")
            return clip
    
    def _add_ending_hook(self, clip: VideoFileClip, hooks: List[str]) -> VideoFileClip:
        """
        Add ending hook to encourage engagement
        """
        
        try:
            from moviepy.editor import TextClip, CompositeVideoClip, ColorClip
            
            if not hooks:
                return clip
            
            hook_text = hooks[0]
            hook_duration = 2.0
            
            # Create hook title card
            bg = ColorClip(
                size=SHORTS_RESOLUTION,
                color=(0, 0, 0)
            ).set_duration(hook_duration)
            
            txt = TextClip(
                hook_text,
                fontsize=70,
                color='white',
                font='Arial-Bold',
                method='caption',
                size=(SHORTS_RESOLUTION[0] - 40, None)
            ).set_duration(hook_duration)
            
            txt = txt.set_position(('center', 'center'))
            
            hook_clip = CompositeVideoClip([bg, txt])
            
            # Combine
            final_clip = concatenate_videoclips([clip, hook_clip])
            
            return final_clip
            
        except Exception as e:
            logger.error(f"Error adding ending hook: {str(e)}")
            return clip


# Global instance
shorts_engine = ShortsEngine()
