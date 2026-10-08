"""
SCRIPT AGENT - AI Script Intelligence Engine

Responsibilities:
- Hook optimization
- Emotional pacing
- Storytelling structure
- Retention optimization
- CTA generation
- Multi-language scripts
"""

import asyncio
from typing import Dict, Any, List
from agents.base_agent import BaseAgent, AgentRole
from config.settings import OPENAI_API_KEY
from openai import OpenAI
from utils.logger import logger
from services.memory_service import get_memory_service
import json


class ScriptAgent(BaseAgent):
    """
    Script Agent for cinematic, human-like script generation.
    Optimizes for retention, hooks, and engagement.
    """
    
    def __init__(self, agent_id: str = "script_agent_1"):
        super().__init__(agent_id, AgentRole.SCRIPT)
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.memory_service = get_memory_service()
        self.learning_state = {
            "successful_patterns": [],
            "hook_performance": {},
            "pacing_templates": []
        }
    
    async def _think(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze script requirements and plan approach
        """
        topic = input_data.get("topic", "")
        language = input_data.get("language", "english")
        
        logger.info(f"Script Agent thinking about: {topic}")
        
        # Get best performing patterns from memory
        best_patterns = self.memory_service.get_best_script_patterns(5)
        channel_tone = self.memory_service.get_channel_tone()
        
        script_plan = {
            "topic": topic,
            "language": language,
            "duration": input_data.get("duration", 300),
            "target_audience": input_data.get("target_audience", "general"),
            "hook_style": "cinematic",  # Can be: cinematic, curiosity, emotional, question
            "pacing": "retention_optimized",
            "call_to_action": input_data.get("cta", "subscribe"),
            "research_data": input_data.get("research_data", {}),
            "previous_patterns": best_patterns,
            "channel_tone": channel_tone,
            "optimization_focus": [
                "hook_optimization",
                "retention_curve",
                "emotional_peaks",
                "curiosity_loops",
                "pattern_interrupts"
            ]
        }
        
        return script_plan
    
    async def _execute(self, analysis: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate optimized, cinematic script
        """
        topic = analysis.get("topic", "")
        language = analysis.get("language", "english")
        duration = analysis.get("duration", 300)
        
        try:
            # Build comprehensive prompt
            prompt = f"""
You are a premium YouTube script writer specializing in cinematic, emotionally engaging content.

TOPIC: {topic}
LANGUAGE: {language}
VIDEO DURATION: {duration} seconds
TARGET AUDIENCE: {analysis.get('target_audience', 'general')}

REQUIREMENTS:
1. Generate a CINEMATIC, human-like script
2. Include 3 "curiosity loops" to maintain retention
3. Start with a powerful hook (first 3 seconds)
4. Build emotional arc throughout
5. Include strategic pattern interrupts (every 30-45 seconds)
6. End with strong CTA
7. Optimize for YouTube algorithm
8. Break into scenes with [SCENE BREAK] markers
9. Include visual descriptions for each scene
10. Add suggested music mood for each section

CHANNEL TONE PREFERENCES:
{json.dumps(analysis.get('channel_tone', {}), indent=2)}

PREVIOUS SUCCESSFUL PATTERNS:
{json.dumps(analysis.get('previous_patterns', [])[:3], indent=2)}

Generate the script in this JSON format:
{{
    "hook": "First 3-second hook",
    "intro": "Introduction section",
    "scenes": [
        {{
            "scene_number": 1,
            "duration_seconds": 0,
            "script_text": "Scene content",
            "visual_description": "What should be on screen",
            "music_mood": "energetic/calm/dramatic",
            "on_screen_text": "Any overlays or captions"
        }}
    ],
    "retention_hooks": ["Hook 1", "Hook 2", "Hook 3"],
    "curiosity_loops": ["Loop 1", "Loop 2", "Loop 3"],
    "cta": "Call to action",
    "outro": "Outro section",
    "estimated_retention_rate": 0.0,
    "key_moments": ["Moment 1", "Moment 2"],
    "seo_keywords": ["keyword1", "keyword2"]
}}

Return ONLY valid JSON, no markdown.
"""
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an elite YouTube script writer. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                top_p=0.95
            )
            
            script_data = json.loads(response.choices[0].message.content)
            
            # Calculate estimated retention
            retention_score = self._calculate_retention_score(script_data)
            script_data["retention_score"] = retention_score
            
            return {
                "topic": topic,
                "script": script_data,
                "status": "success",
                "word_count": self._count_words(script_data),
                "estimated_duration": duration
            }
            
        except Exception as e:
            logger.error(f"Script generation failed: {str(e)}")
            return {
                "topic": topic,
                "error": str(e),
                "status": "failed"
            }
    
    async def _learn(self, input_data: Dict[str, Any], result: Dict[str, Any]):
        """
        Learn from script generation results
        """
        if result.get("status") == "success":
            script_data = result.get("script", {})
            
            # Save script pattern for future use
            pattern_name = f"pattern_{len(self.learning_state['successful_patterns'])}"
            self.memory_service.save_script_pattern(
                pattern_name,
                json.dumps(script_data),
                script_data.get("retention_score", 0.5)
            )
            
            # Store hook performance
            for hook in script_data.get("retention_hooks", []):
                if hook not in self.learning_state["hook_performance"]:
                    self.learning_state["hook_performance"][hook] = {"count": 0, "effectiveness": 0}
                self.learning_state["hook_performance"][hook]["count"] += 1
            
            logger.info(f"Script Agent learned from successful generation")
    
    def _calculate_retention_score(self, script_data: Dict) -> float:
        """
        Calculate estimated retention score based on script structure
        """
        score = 0.7  # Base score
        
        # Bonus for hooks
        if script_data.get("retention_hooks"):
            score += 0.1 * len(script_data.get("retention_hooks", []))
        
        # Bonus for curiosity loops
        if script_data.get("curiosity_loops"):
            score += 0.15
        
        # Cap at 0.95
        return min(score, 0.95)
    
    def _count_words(self, script_data: Dict) -> int:
        """Count total words in script"""
        total_words = 0
        
        if script_data.get("hook"):
            total_words += len(script_data["hook"].split())
        if script_data.get("intro"):
            total_words += len(script_data["intro"].split())
        if script_data.get("cta"):
            total_words += len(script_data["cta"].split())
        
        for scene in script_data.get("scenes", []):
            total_words += len(scene.get("script_text", "").split())
        
        return total_words
    
    async def optimize_for_retention(self, script: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimize existing script for better retention
        """
        logger.info("Optimizing script for retention")
        
        optimization_prompt = f"""
Analyze this YouTube script and suggest retention optimizations:

{json.dumps(script, indent=2)}

Return JSON with:
- improvement_suggestions: [...]
- new_hooks: [...]
- pattern_interrupt_recommendations: [...]
- estimated_improvement_percentage: 0-100
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a retention optimization expert."},
                    {"role": "user", "content": optimization_prompt}
                ]
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"Script optimization failed: {str(e)}")
            return {"error": str(e)}
