"""
Advanced Voice Director Service
AI-powered narration with emotional control, pacing, and multilingual support
"""

from typing import Optional, Dict, List
from dataclasses import dataclass
from enum import Enum
import json
import asyncio
import openai
from config.settings import OPENAI_API_KEY, ELEVENLABS_API_KEY, AUDIO_SAMPLE_RATE
from utils.logger import logger


class VoiceProvider(str, Enum):
    ELEVENLABS = "elevenlabs"
    OPENAI = "openai"
    EDGE = "edge_tts"


class VoiceGender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    NEUTRAL = "neutral"


class EmotionTone(str, Enum):
    HAPPY = "happy"
    SERIOUS = "serious"
    ENERGETIC = "energetic"
    CALM = "calm"
    DRAMATIC = "dramatic"
    MYSTERIOUS = "mysterious"
    URGENT = "urgent"
    PERSUASIVE = "persuasive"


@dataclass
class VoiceSettings:
    """Voice generation settings"""
    provider: VoiceProvider
    gender: VoiceGender
    emotion: EmotionTone
    speed: float  # 0.5-2.0
    pitch: float  # 0.5-2.0
    volume: float  # 0.0-1.0
    language: str


@dataclass
class NarrationSegment:
    """Individual narration segment with timing"""
    text: str
    start_time: float
    duration: float
    emotion: EmotionTone
    speed_multiplier: float = 1.0


class VoiceDirector:
    """
    Production-grade voice narration system
    
    Features:
    - Multiple voice providers (ElevenLabs, OpenAI TTS, Edge TTS)
    - Emotional voice control
    - Pacing and speed adjustment
    - Multilingual narration
    - Voice variety and personality
    - Pause injection for pacing
    - Prosody control
    - Auto voice selection
    """
    
    def __init__(self):
        self.openai_client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)
        self.elevenlabs_api_key = ELEVENLABS_API_KEY
    
    async def generate_narration(
        self,
        script: str,
        voice_settings: VoiceSettings,
        output_path: str
    ) -> str:
        """
        Generate high-quality narration from script
        """
        
        try:
            logger.info(f"Generating narration using {voice_settings.provider.value}")
            
            if voice_settings.provider == VoiceProvider.OPENAI:
                audio_path = await self._generate_openai_tts(
                    script, voice_settings, output_path
                )
            elif voice_settings.provider == VoiceProvider.ELEVENLABS:
                audio_path = await self._generate_elevenlabs_tts(
                    script, voice_settings, output_path
                )
            elif voice_settings.provider == VoiceProvider.EDGE:
                audio_path = await self._generate_edge_tts(
                    script, voice_settings, output_path
                )
            else:
                raise ValueError(f"Unknown voice provider: {voice_settings.provider}")
            
            logger.info(f"Narration generated: {audio_path}")
            return audio_path
            
        except Exception as e:
            logger.error(f"Error generating narration: {str(e)}")
            raise
    
    async def _generate_openai_tts(
        self,
        script: str,
        voice_settings: VoiceSettings,
        output_path: str
    ) -> str:
        """Generate narration using OpenAI TTS"""
        
        # Map voice settings to OpenAI voices
        voice_map = {
            VoiceGender.MALE: "onyx",  # Deep male
            VoiceGender.FEMALE: "nova",  # Female
            VoiceGender.NEUTRAL: "echo"  # Neutral
        }
        
        voice = voice_map.get(voice_settings.gender, "nova")
        
        try:
            response = await self.openai_client.audio.speech.create(
                model="tts-1-hd",  # High quality
                voice=voice,
                input=script,
                speed=voice_settings.speed
            )
            
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            return output_path
            
        except Exception as e:
            logger.error(f"OpenAI TTS error: {str(e)}")
            raise
    
    async def _generate_elevenlabs_tts(
        self,
        script: str,
        voice_settings: VoiceSettings,
        output_path: str
    ) -> str:
        """Generate narration using ElevenLabs"""
        
        if not self.elevenlabs_api_key:
            raise ValueError("ElevenLabs API key not configured")
        
        try:
            import aiohttp
            
            # Map emotion to ElevenLabs voice settings
            stability = self._get_stability(voice_settings.emotion)
            similarity_boost = self._get_similarity_boost(voice_settings.emotion)
            
            # Select voice based on gender and emotion
            voice_id = await self._select_elevenlabs_voice(
                voice_settings.gender,
                voice_settings.emotion
            )
            
            headers = {
                "xi-api-key": self.elevenlabs_api_key,
                "Content-Type": "application/json"
            }
            
            data = {
                "text": script,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": stability,
                    "similarity_boost": similarity_boost,
                    "style": self._get_voice_style(voice_settings.emotion)
                }
            }
            
            async with aiohttp.ClientSession() as session:
                url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
                async with session.post(url, json=data, headers=headers) as response:
                    if response.status == 200:
                        with open(output_path, 'wb') as f:
                            f.write(await response.read())
                        return output_path
                    else:
                        raise Exception(f"ElevenLabs API error: {response.status}")
            
        except Exception as e:
            logger.error(f"ElevenLabs TTS error: {str(e)}")
            raise
    
    async def _generate_edge_tts(
        self,
        script: str,
        voice_settings: VoiceSettings,
        output_path: str
    ) -> str:
        """Generate narration using Microsoft Edge TTS"""
        
        try:
            import edge_tts
            
            # Map language to Edge TTS locale
            language_map = {
                "english": "en-US",
                "urdu": "ur-PK",
                "hindi": "hi-IN",
                "arabic": "ar-SA",
                "spanish": "es-ES",
                "french": "fr-FR"
            }
            
            locale = language_map.get(voice_settings.language, "en-US")
            
            # Select voice
            if voice_settings.gender == VoiceGender.FEMALE:
                voice = f"{locale}-Female"
            elif voice_settings.gender == VoiceGender.MALE:
                voice = f"{locale}-Male"
            else:
                voice = f"{locale}"
            
            # Adjust rate for emotion
            rate = self._get_edge_rate(voice_settings.emotion, voice_settings.speed)
            
            communicate = edge_tts.Communicate(
                text=script,
                voice=voice,
                rate=rate,
                volume=int(voice_settings.volume * 100)
            )
            
            await communicate.save(output_path)
            
            return output_path
            
        except Exception as e:
            logger.error(f"Edge TTS error: {str(e)}")
            raise
    
    def _get_stability(self, emotion: EmotionTone) -> float:
        """Map emotion to ElevenLabs stability setting"""
        
        stability_map = {
            EmotionTone.CALM: 0.8,
            EmotionTone.SERIOUS: 0.75,
            EmotionTone.HAPPY: 0.7,
            EmotionTone.ENERGETIC: 0.6,
            EmotionTone.DRAMATIC: 0.5,
            EmotionTone.URGENT: 0.4
        }
        
        return stability_map.get(emotion, 0.7)
    
    def _get_similarity_boost(self, emotion: EmotionTone) -> float:
        """Map emotion to similarity boost"""
        
        boost_map = {
            EmotionTone.CALM: 0.75,
            EmotionTone.SERIOUS: 0.8,
            EmotionTone.HAPPY: 0.85,
            EmotionTone.ENERGETIC: 0.9,
            EmotionTone.DRAMATIC: 0.8,
            EmotionTone.URGENT: 0.85
        }
        
        return boost_map.get(emotion, 0.75)
    
    async def _select_elevenlabs_voice(self, gender: VoiceGender,
                                       emotion: EmotionTone) -> str:
        """Select appropriate ElevenLabs voice ID"""
        
        # Placeholder voice IDs - would be configured in settings
        voice_map = {
            (VoiceGender.MALE, EmotionTone.SERIOUS): "pMsXgVNQu63GQdsXU/PH",
            (VoiceGender.MALE, EmotionTone.ENERGETIC): "EXAVITQu4rP4TqMsxvlz",
            (VoiceGender.FEMALE, EmotionTone.HAPPY): "piTKgcLEGmPLHRajZE9t",
            (VoiceGender.FEMALE, EmotionTone.CALM): "ThT5KcBeYPX3keUQqHPh",
        }
        
        # Get appropriate voice
        key = (gender, emotion)
        voice_id = voice_map.get(key, "pMsXgVNQu63GQdsXU/PH")  # Default male serious
        
        return voice_id
    
    def _get_voice_style(self, emotion: EmotionTone) -> float:
        """Get voice style intensity for emotion"""
        
        style_map = {
            EmotionTone.CALM: 0.3,
            EmotionTone.HAPPY: 0.6,
            EmotionTone.SERIOUS: 0.4,
            EmotionTone.ENERGETIC: 0.8,
            EmotionTone.DRAMATIC: 0.7,
            EmotionTone.MYSTERIOUS: 0.5
        }
        
        return style_map.get(emotion, 0.4)
    
    def _get_edge_rate(self, emotion: EmotionTone, speed: float) -> float:
        """Calculate Edge TTS rate"""
        
        # Base rate from emotion
        emotion_rate = {
            EmotionTone.CALM: 0.8,
            EmotionTone.HAPPY: 1.0,
            EmotionTone.SERIOUS: 0.9,
            EmotionTone.ENERGETIC: 1.2,
            EmotionTone.DRAMATIC: 0.85,
            EmotionTone.URGENT: 1.3
        }
        
        base_rate = emotion_rate.get(emotion, 1.0)
        
        # Apply speed multiplier
        final_rate = base_rate * speed
        
        # Clamp to valid range (-50 to 50)
        return max(-50, min(50, (final_rate - 1.0) * 100))
    
    async def generate_cinematic_narration(
        self,
        segments: List[NarrationSegment],
        voice_settings: VoiceSettings,
        output_path: str
    ) -> str:
        """
        Generate segmented narration with varying emotions and pacing
        """
        
        try:
            import pydub
            
            combined_audio = pydub.AudioSegment.empty()
            
            for i, segment in enumerate(segments):
                # Adjust settings for this segment
                segment_settings = VoiceSettings(
                    provider=voice_settings.provider,
                    gender=voice_settings.gender,
                    emotion=segment.emotion,
                    speed=voice_settings.speed * segment.speed_multiplier,
                    pitch=voice_settings.pitch,
                    volume=voice_settings.volume,
                    language=voice_settings.language
                )
                
                # Generate segment audio
                segment_path = f"/tmp/segment_{i}.mp3"
                await self.generate_narration(
                    segment.text,
                    segment_settings,
                    segment_path
                )
                
                # Load and add to combined
                segment_audio = pydub.AudioSegment.from_file(segment_path)
                combined_audio += segment_audio
            
            # Export final audio
            combined_audio.export(output_path, format="mp3")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating cinematic narration: {str(e)}")
            raise
    
    async def select_optimal_voice(
        self,
        script: str,
        video_type: str,
        audience: str
    ) -> VoiceSettings:
        """
        AI-powered voice selection based on content
        """
        
        prompt = f"""
        Select optimal voice settings for YouTube video.
        
        Video Type: {video_type}
        Target Audience: {audience}
        Script Length: {len(script)} characters
        
        Provide optimal:
        - Voice provider (elevenlabs, openai, edge)
        - Gender (male, female, neutral)
        - Emotion tone (energetic, serious, calm, etc)
        - Speed (0.8-1.2)
        - Why this combination works
        
        Return JSON:
        {{
            "provider": "elevenlabs",
            "gender": "male",
            "emotion": "energetic",
            "speed": 1.0,
            "reasoning": "..."
        }}
        """
        
        response = await self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        settings_data = json.loads(response.choices[0].message.content)
        
        return VoiceSettings(
            provider=VoiceProvider(settings_data.get("provider", "openai")),
            gender=VoiceGender(settings_data.get("gender", "male")),
            emotion=EmotionTone(settings_data.get("emotion", "energetic")),
            speed=float(settings_data.get("speed", 1.0)),
            pitch=1.0,
            volume=1.0,
            language="english"
        )


# Global instance
voice_director = VoiceDirector()
