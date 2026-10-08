"""
SCENE DIRECTOR SERVICE - AI Film Director

Responsibilities:
- Automatic storyboard generation
- Scene planning with visual descriptions
- Camera angle planning
- Cinematic pacing
- Lighting and mood suggestions
- Transition logic
"""

import json
from typing import Dict, Any, List, Optional
from config.settings import OPENAI_API_KEY, VIDEO_RESOLUTION
from openai import OpenAI
from utils.logger import logger
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class CameraAngle:
    """Represents a camera angle/shot"""
    name: str  # wide, medium, close-up, over-shoulder, tracking, drone, etc
    description: str
    duration_seconds: float
    position: Dict[str, float]  # x, y, z coordinates
    rotation: Dict[str, float]  # pitch, yaw, roll
    focal_length: float  # in mm
    motion: Optional[str]  # pan, tilt, zoom, track, static
    motion_speed: float  # 0-1 scale


@dataclass
class Transition:
    """Represents a transition between scenes"""
    type: str  # cut, fade, dissolve, wipe, slide, zoom
    duration_ms: int
    easing: str  # linear, ease-in, ease-out, ease-in-out
    direction: Optional[str]  # for directional transitions


@dataclass
class SceneDirection:
    """Represents a directed scene"""
    scene_number: int
    title: str
    duration_seconds: float
    script_excerpt: str
    visual_description: str
    camera_angle: CameraAngle
    lighting: Dict[str, Any]  # brightness, color temp, mood
    transition_in: Optional[Transition]
    transition_out: Optional[Transition]
    on_screen_elements: List[str]  # text overlays, graphics, etc
    music_cue: str  # music mood/intensity
    special_effects: List[str]  # effects to apply
    actors_needed: List[str]  # avatars, presenters, etc


class SceneDirectorService:
    """
    AI Scene Director - Plans cinematography and scenes like a professional director
    """
    
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.storyboards: Dict[str, List[SceneDirection]] = {}
        
        logger.info("Scene Director Service initialized")
    
    async def create_storyboard(self, script: Dict[str, Any], research_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate complete cinematic storyboard from script
        """
        try:
            topic = script.get("topic", "")
            scenes_data = script.get("scenes", [])
            
            logger.info(f"Creating storyboard for {topic}")
            
            # Build cinematic storyboard
            storyboard = []
            
            for idx, scene in enumerate(scenes_data, 1):
                directed_scene = await self._direct_scene(
                    scene_number=idx,
                    script_section=scene,
                    total_scenes=len(scenes_data),
                    topic=topic
                )
                storyboard.append(directed_scene)
            
            storyboard_id = f"storyboard_{hash(topic) % 1000000}"
            self.storyboards[storyboard_id] = storyboard
            
            return {
                "storyboard_id": storyboard_id,
                "topic": topic,
                "total_scenes": len(storyboard),
                "total_duration_seconds": sum(s.duration_seconds for s in storyboard),
                "scenes": [asdict(s) for s in storyboard],
                "cinematic_notes": self._generate_cinematic_notes(storyboard)
            }
            
        except Exception as e:
            logger.error(f"Storyboard creation failed: {str(e)}")
            return {
                "error": str(e),
                "status": "failed"
            }
    
    async def _direct_scene(
        self, 
        scene_number: int, 
        script_section: Dict[str, Any],
        total_scenes: int,
        topic: str
    ) -> SceneDirection:
        """
        Direct a single scene with cinematography details
        """
        script_text = script_section.get("script_text", "")
        visual_description = script_section.get("visual_description", "")
        duration = script_section.get("duration_seconds", 10)
        
        # Use AI to generate detailed cinematography
        prompt = f"""
You are a renowned film director. Direct this scene cinematically:

TOPIC: {topic}
SCENE NUMBER: {scene_number}/{total_scenes}
DURATION: {duration} seconds

SCRIPT:
{script_text}

VISUAL CONCEPT:
{visual_description}

Generate detailed cinematography as JSON:
{{
    "camera_angle": {{
        "name": "wide/medium/close-up/etc",
        "description": "What is framed",
        "position": {{"x": 0, "y": 0, "z": 0}},
        "focal_length_mm": 50,
        "motion": "pan/tilt/zoom/track/static",
        "motion_speed": 0.5
    }},
    "lighting": {{
        "brightness": 0.8,
        "color_temp_k": 5600,
        "mood": "dramatic/warm/cool/energetic",
        "key_light_angle": "45",
        "fill_light_ratio": 0.3
    }},
    "transition_in": {{
        "type": "cut/fade/dissolve",
        "duration_ms": 0,
        "easing": "linear"
    }},
    "transition_out": {{
        "type": "cut/fade/dissolve", 
        "duration_ms": 300,
        "easing": "ease-in-out"
    }},
    "on_screen_elements": ["text overlay 1", "graphic 1"],
    "music_cue": "intense/calm/motivational",
    "special_effects": ["effect1", "effect2"],
    "cinematography_notes": "Director's notes for the scene"
}}

Return ONLY valid JSON.
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a legendary film director. Return valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8
            )
            
            cinematography = json.loads(response.choices[0].message.content)
            
            # Build CameraAngle object
            camera_data = cinematography.get("camera_angle", {})
            camera_angle = CameraAngle(
                name=camera_data.get("name", "medium"),
                description=camera_data.get("description", ""),
                duration_seconds=duration,
                position=camera_data.get("position", {"x": 0, "y": 0, "z": 0}),
                rotation=camera_data.get("rotation", {"pitch": 0, "yaw": 0, "roll": 0}),
                focal_length=camera_data.get("focal_length_mm", 50),
                motion=camera_data.get("motion", "static"),
                motion_speed=camera_data.get("motion_speed", 0)
            )
            
            # Build Transition objects
            transition_in_data = cinematography.get("transition_in", {})
            transition_in = Transition(
                type=transition_in_data.get("type", "cut"),
                duration_ms=transition_in_data.get("duration_ms", 0),
                easing=transition_in_data.get("easing", "linear")
            ) if scene_number > 1 else None
            
            transition_out_data = cinematography.get("transition_out", {})
            transition_out = Transition(
                type=transition_out_data.get("type", "cut"),
                duration_ms=transition_out_data.get("duration_ms", 0),
                easing=transition_out_data.get("easing", "linear")
            )
            
            # Build SceneDirection
            scene_direction = SceneDirection(
                scene_number=scene_number,
                title=f"Scene {scene_number}",
                duration_seconds=duration,
                script_excerpt=script_text[:100],
                visual_description=visual_description,
                camera_angle=camera_angle,
                lighting=cinematography.get("lighting", {}),
                transition_in=transition_in,
                transition_out=transition_out,
                on_screen_elements=cinematography.get("on_screen_elements", []),
                music_cue=cinematography.get("music_cue", "neutral"),
                special_effects=cinematography.get("special_effects", []),
                actors_needed=[]
            )
            
            return scene_direction
            
        except Exception as e:
            logger.error(f"Scene direction failed for scene {scene_number}: {str(e)}")
            # Return default scene on error
            return self._create_default_scene(scene_number, duration)
    
    def _create_default_scene(self, scene_number: int, duration: float) -> SceneDirection:
        """Create a default scene when AI fails"""
        return SceneDirection(
            scene_number=scene_number,
            title=f"Scene {scene_number}",
            duration_seconds=duration,
            script_excerpt="",
            visual_description="",
            camera_angle=CameraAngle(
                name="medium",
                description="Medium shot",
                duration_seconds=duration,
                position={"x": 0, "y": 0, "z": 5},
                rotation={"pitch": 0, "yaw": 0, "roll": 0},
                focal_length=50,
                motion="static",
                motion_speed=0
            ),
            lighting={
                "brightness": 0.8,
                "color_temp_k": 5600,
                "mood": "neutral"
            },
            transition_in=None if scene_number == 1 else Transition("cut", 0, "linear"),
            transition_out=Transition("cut", 0, "linear"),
            on_screen_elements=[],
            music_cue="neutral",
            special_effects=[],
            actors_needed=[]
        )
    
    def _generate_cinematic_notes(self, storyboard: List[SceneDirection]) -> str:
        """Generate cinematic notes for the entire storyboard"""
        notes = "CINEMATIC DIRECTION NOTES:\n\n"
        
        # Pacing analysis
        notes += "PACING:\n"
        avg_scene_duration = sum(s.duration_seconds for s in storyboard) / len(storyboard)
        notes += f"- Average scene length: {avg_scene_duration:.1f} seconds\n"
        notes += f"- Shortest scene: {min(s.duration_seconds for s in storyboard):.1f}s\n"
        notes += f"- Longest scene: {max(s.duration_seconds for s in storyboard):.1f}s\n\n"
        
        # Camera variety
        notes += "CAMERA ANGLES USED:\n"
        angles = set(s.camera_angle.name for s in storyboard)
        for angle in angles:
            count = sum(1 for s in storyboard if s.camera_angle.name == angle)
            notes += f"- {angle.capitalize()}: {count} scenes\n"
        
        notes += "\nTRANSITION PLAN:\n"
        for idx, scene in enumerate(storyboard):
            if scene.transition_out:
                notes += f"- Scene {idx+1} to {idx+2}: {scene.transition_out.type}\n"
        
        return notes
    
    def get_storyboard(self, storyboard_id: str) -> Optional[List[SceneDirection]]:
        """Retrieve a storyboard by ID"""
        return self.storyboards.get(storyboard_id)
    
    async def generate_scene_breakdown(self, storyboard: List[SceneDirection]) -> Dict[str, Any]:
        """Generate detailed scene breakdown for video generation"""
        breakdown = {
            "total_scenes": len(storyboard),
            "total_duration": sum(s.duration_seconds for s in storyboard),
            "scenes": []
        }
        
        for scene in storyboard:
            breakdown["scenes"].append({
                "scene_number": scene.scene_number,
                "title": scene.title,
                "duration": scene.duration_seconds,
                "camera": asdict(scene.camera_angle),
                "lighting": scene.lighting,
                "music": scene.music_cue,
                "elements": scene.on_screen_elements,
                "effects": scene.special_effects
            })
        
        return breakdown


# Global instance
_scene_director = None


def get_scene_director_service() -> SceneDirectorService:
    """Get or create scene director service"""
    global _scene_director
    if _scene_director is None:
        _scene_director = SceneDirectorService()
    return _scene_director
