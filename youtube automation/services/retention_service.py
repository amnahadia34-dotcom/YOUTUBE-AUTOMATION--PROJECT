"""
RETENTION OPTIMIZATION ENGINE

Responsibilities:
- Hook optimization for first 3 seconds
- Suspense insertion and curiosity loops
- Pacing optimization
- Pattern interrupts
- Retention curve improvement
"""

import json
from typing import Dict, Any, List
from config.settings import OPENAI_API_KEY
from openai import OpenAI
from utils.logger import logger


class RetentionOptimizationService:
    """
    Optimizes scripts and videos for viewer retention
    """
    
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        logger.info("Retention Optimization Service initialized")
    
    async def optimize_script(self, script: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze and optimize script for retention
        """
        try:
            logger.info("Optimizing script for retention")
            
            prompt = f"""
Analyze this YouTube script for viewer retention and provide optimization recommendations:

SCRIPT:
{json.dumps(script, indent=2)}

Provide detailed retention analysis:
{{
    "current_retention_estimate": 0.0,
    "optimized_retention_estimate": 0.0,
    "hook_score": 0.0,
    "first_30_seconds": "Is it engaging?",
    "curiosity_loops": ["loop 1", "loop 2"],
    "pattern_interrupts": ["interrupt 1", "interrupt 2"],
    "retention_dips": ["potential dip point 1"],
    "improvements": ["improvement 1"],
    "retention_curve": {{"0-10s": 0.95, "10-30s": 0.85}},
    "estimated_avg_view_duration": "percentage of video"
}}

Return ONLY valid JSON.
"""
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a YouTube retention expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            analysis = json.loads(response.choices[0].message.content)
            
            return {
                "status": "success",
                "retention_analysis": analysis,
                "optimization_suggestions": analysis.get("improvements", [])
            }
            
        except Exception as e:
            logger.error(f"Script optimization failed: {str(e)}")
            return {"error": str(e), "status": "failed"}
    
    async def generate_retention_hooks(self, topic: str, duration: float) -> List[str]:
        """
        Generate retention hooks for a video
        """
        try:
            logger.info(f"Generating retention hooks for {topic}")
            
            prompt = f"""
Generate 5 powerful retention hooks for a YouTube video:

TOPIC: {topic}
DURATION: {duration} seconds

Hooks should be:
1. Placed at strategic moments to prevent drop-off
2. Curiosity-driven
3. Promise value or answers
4. Emotionally engaging
5. Natural to the content

Return as JSON array:
["hook1", "hook2", "hook3", "hook4", "hook5"]

Return ONLY valid JSON.
"""
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert YouTube content strategist."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            hooks = json.loads(response.choices[0].message.content)
            return hooks
            
        except Exception as e:
            logger.error(f"Hook generation failed: {str(e)}")
            return []
    
    async def analyze_pacing(self, script: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze and optimize video pacing
        """
        try:
            logger.info("Analyzing video pacing")
            
            scenes = script.get("scenes", [])
            total_duration = sum(s.get("duration_seconds", 0) for s in scenes)
            
            pacing_analysis = {
                "total_duration": total_duration,
                "average_scene_duration": total_duration / len(scenes) if scenes else 0,
                "pacing_rhythm": self._calculate_pacing_rhythm(scenes),
                "recommendations": self._get_pacing_recommendations(scenes, total_duration)
            }
            
            return {
                "status": "success",
                "pacing_analysis": pacing_analysis
            }
            
        except Exception as e:
            logger.error(f"Pacing analysis failed: {str(e)}")
            return {"error": str(e), "status": "failed"}
    
    def _calculate_pacing_rhythm(self, scenes: List[Dict]) -> str:
        """Calculate pacing rhythm pattern"""
        if not scenes:
            return "unknown"
        
        durations = [s.get("duration_seconds", 10) for s in scenes]
        avg = sum(durations) / len(durations)
        variance = sum((d - avg) ** 2 for d in durations) / len(durations)
        
        if variance < 5:
            return "steady"
        elif variance < 25:
            return "moderate_variation"
        else:
            return "high_variation"
    
    def _get_pacing_recommendations(self, scenes: List[Dict], total_duration: float) -> List[str]:
        """Get pacing recommendations"""
        recommendations = []
        
        if total_duration > 600:
            recommendations.append("Consider breaking into shorter segments for better retention")
        
        if total_duration < 180:
            recommendations.append("Video might be too short - consider expanding with more content")
        
        return recommendations


# Global instance
_retention_service = None


def get_retention_optimization_service() -> RetentionOptimizationService:
    """Get or create retention optimization service"""
    global _retention_service
    if _retention_service is None:
        _retention_service = RetentionOptimizationService()
    return _retention_service
