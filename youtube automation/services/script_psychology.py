"""
Advanced Script Psychology Engine
Generates high-retention scripts using psychological principles, hooks, and pacing
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import json
from enum import Enum
import openai
from config.settings import OPENAI_API_KEY, MAIN_LLM_MODEL, FAST_LLM_MODEL
from utils.logger import logger


class HookType(str, Enum):
    CURIOSITY_GAP = "curiosity_gap"
    PATTERN_INTERRUPT = "pattern_interrupt"
    STORY_HOOK = "story_hook"
    QUESTION_HOOK = "question_hook"
    STATEMENT_HOOK = "statement_hook"
    MYSTERY_HOOK = "mystery_hook"
    CONTRADICTION_HOOK = "contradiction_hook"


class PacingStyle(str, Enum):
    SLOW_BURN = "slow_burn"  # Gradual tension building
    FAST_PACED = "fast_paced"  # Quick cuts, rapid info
    RHYTHMIC = "rhythmic"  # Pattern-based pacing
    CRESCENDO = "crescendo"  # Builds to climax
    WAVE = "wave"  # Ups and downs


class RetentionCheckpoint(str, Enum):
    HOOK = "hook"  # First 3 seconds
    PREVIEW = "preview"  # 5-10 seconds - Show what's coming
    CURIOSITY = "curiosity"  # Introduce mystery/problem
    SOLUTION_TEASE = "solution_tease"  # Hint at solution
    VALUE_DROP = "value_drop"  # Deliver core value
    RETENTION_LOOP = "retention_loop"  # Keep them watching
    CLIMAX = "climax"  # Peak moment
    CTA = "cta"  # Call to action


@dataclass
class HookAnalysis:
    """Analysis of hook effectiveness"""
    hook_type: HookType
    hook_text: str
    psychological_trigger: str
    expected_retention_improvement: float  # 0-100%


@dataclass
class PacingPlan:
    """Video pacing strategy"""
    style: PacingStyle
    segments: List[Dict[str, Any]]  # [{duration: 10, intensity: 8, description: "..."}]
    total_duration: int


@dataclass
class RetentionStrategy:
    """Strategy to maintain viewer retention"""
    checkpoints: List[Dict[str, Any]]
    cliffhangers: List[str]
    curiosity_gaps: List[str]
    pattern_breaks: List[str]
    callbacks: List[str]  # References to earlier content


class ScriptPsychologyEngine:
    """
    AI-powered script generation with psychological principles
    
    Features:
    - Hook generation with psychology principles
    - Retention checkpoint strategy
    - Pacing optimization
    - Curiosity gap creation
    - Emotional arc design
    - CTA optimization
    - Story structure optimization
    """
    
    def __init__(self):
        self.openai_client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)
    
    async def generate_high_retention_script(
        self,
        topic: str,
        video_type: str,
        duration_seconds: int,
        hook_type: HookType = HookType.CURIOSITY_GAP,
        pacing_style: PacingStyle = PacingStyle.FAST_PACED,
        target_retention: float = 75.0,
        audience: str = "general",
        tone: str = "energetic",
        language: str = "english"
    ) -> Dict[str, Any]:
        """
        Generate complete high-retention script
        """
        
        try:
            logger.info(f"Generating high-retention script: {topic}")
            
            # Step 1: Generate hook
            hook = await self._generate_hook(topic, hook_type, audience, tone)
            
            # Step 2: Create retention strategy
            retention_strategy = await self._create_retention_strategy(
                topic, duration_seconds, target_retention
            )
            
            # Step 3: Plan pacing
            pacing_plan = await self._plan_pacing(
                duration_seconds, pacing_style, video_type
            )
            
            # Step 4: Generate full script
            script = await self._generate_full_script(
                topic=topic,
                hook=hook,
                retention_strategy=retention_strategy,
                pacing_plan=pacing_plan,
                duration_seconds=duration_seconds,
                audience=audience,
                tone=tone,
                language=language
            )
            
            # Step 5: Optimize for CTA
            script_with_cta = await self._optimize_cta(script, video_type)
            
            return {
                "script": script_with_cta,
                "hook": hook,
                "retention_strategy": retention_strategy,
                "pacing_plan": pacing_plan,
                "estimated_retention": target_retention,
                "psychological_triggers": await self._extract_triggers(script_with_cta)
            }
            
        except Exception as e:
            logger.error(f"Error generating script: {str(e)}")
            raise
    
    async def _generate_hook(self, topic: str, hook_type: HookType,
                            audience: str, tone: str) -> HookAnalysis:
        """Generate psychologically powerful hook"""
        
        psychology_info = {
            HookType.CURIOSITY_GAP: "Creates information gap that forces brain to watch",
            HookType.PATTERN_INTERRUPT: "Breaks viewer's attention pattern in first seconds",
            HookType.STORY_HOOK: "Uses narrative tension",
            HookType.QUESTION_HOOK: "Poses compelling question",
            HookType.STATEMENT_HOOK: "Makes provocative statement",
            HookType.MYSTERY_HOOK: "Introduces mystery",
            HookType.CONTRADICTION_HOOK: "Presents paradox"
        }
        
        prompt = f"""
        Generate a powerful {hook_type.value} hook for this YouTube video:
        
        Topic: {topic}
        Audience: {audience}
        Tone: {tone}
        Psychology Type: {psychology_info.get(hook_type, "")}
        
        Requirements:
        - Must be said in FIRST 3 SECONDS maximum
        - Should stop scrollers mid-scroll
        - Use {hook_type.value} psychology principle
        - Be specific and concrete (not generic)
        - Create curiosity gap or pattern interrupt
        - Language: {tone}
        
        Provide:
        {{
            "hook_text": "...",
            "psychological_trigger": "...",
            "why_it_works": "...",
            "expected_retention_improvement": 15.0
        }}
        """
        
        response = await self.openai_client.chat.completions.create(
            model=FAST_LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.9,
            response_format={"type": "json_object"}
        )
        
        hook_data = json.loads(response.choices[0].message.content)
        
        return HookAnalysis(
            hook_type=hook_type,
            hook_text=hook_data["hook_text"],
            psychological_trigger=hook_data["psychological_trigger"],
            expected_retention_improvement=hook_data.get("expected_retention_improvement", 15)
        )
    
    async def _create_retention_strategy(self, topic: str, duration: int,
                                        target_retention: float) -> RetentionStrategy:
        """Create multi-point retention strategy"""
        
        prompt = f"""
        Create retention strategy for YouTube video:
        
        Topic: {topic}
        Duration: {duration} seconds
        Target Retention: {target_retention}%
        
        Design retention checkpoints that maintain viewer interest:
        
        {{
            "checkpoints": [
                {{
                    "time_seconds": 0,
                    "type": "hook",
                    "action": "Stop scrollers",
                    "duration": 3
                }},
                {{
                    "time_seconds": 5,
                    "type": "preview",
                    "action": "Show what's coming",
                    "duration": 5
                }},
                ... more checkpoints
            ],
            "cliffhangers": ["...", "..."],
            "curiosity_gaps": ["...", "..."],
            "pattern_breaks": ["...", "..."],
            "callbacks": ["reference to earlier content"],
            "retention_boosters": ["...", "..."]
        }}
        """
        
        response = await self.openai_client.chat.completions.create(
            model=MAIN_LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            response_format={"type": "json_object"}
        )
        
        strategy_data = json.loads(response.choices[0].message.content)
        
        return RetentionStrategy(
            checkpoints=strategy_data.get("checkpoints", []),
            cliffhangers=strategy_data.get("cliffhangers", []),
            curiosity_gaps=strategy_data.get("curiosity_gaps", []),
            pattern_breaks=strategy_data.get("pattern_breaks", []),
            callbacks=strategy_data.get("callbacks", [])
        )
    
    async def _plan_pacing(self, duration: int, style: PacingStyle,
                          video_type: str) -> PacingPlan:
        """Design optimal pacing structure"""
        
        prompt = f"""
        Design pacing for {duration} second video using {style.value} style.
        Video type: {video_type}
        
        Return segment-by-segment pacing:
        {{
            "segments": [
                {{
                    "segment": 1,
                    "duration": 15,
                    "intensity": 9,
                    "type": "hook",
                    "description": "..."
                }},
                ... more segments
            ],
            "pacing_notes": "..."
        }}
        """
        
        response = await self.openai_client.chat.completions.create(
            model=FAST_LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        pacing_data = json.loads(response.choices[0].message.content)
        
        return PacingPlan(
            style=style,
            segments=pacing_data.get("segments", []),
            total_duration=duration
        )
    
    async def _generate_full_script(self, topic: str, hook: HookAnalysis,
                                   retention_strategy: RetentionStrategy,
                                   pacing_plan: PacingPlan,
                                   duration_seconds: int,
                                   audience: str, tone: str,
                                   language: str) -> str:
        """Generate complete script with all elements"""
        
        prompt = f"""
        Generate complete YouTube script combining all elements:
        
        Topic: {topic}
        Duration: {duration_seconds} seconds
        Audience: {audience}
        Tone: {tone}
        Language: {language}
        
        Hook (first 3 sec): {hook.hook_text}
        
        Retention Checkpoints: {json.dumps(retention_strategy.checkpoints)}
        Pacing: {pacing_plan.style.value}
        
        Requirements:
        - Start with EXACT hook provided
        - Hit all retention checkpoints
        - Include cliffhangers: {retention_strategy.cliffhangers}
        - Create curiosity gaps: {retention_strategy.curiosity_gaps}
        - Pattern breaks: {retention_strategy.pattern_breaks}
        - Follow pacing plan
        - End with compelling CTA
        - Natural, conversational tone
        - Concise (~1-2 minutes of dialogue)
        
        Format as natural narration script.
        """
        
        response = await self.openai_client.chat.completions.create(
            model=MAIN_LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.85
        )
        
        return response.choices[0].message.content
    
    async def _optimize_cta(self, script: str, video_type: str) -> str:
        """Optimize call-to-action for maximum conversion"""
        
        prompt = f"""
        Optimize the call-to-action in this script for maximum viewer action.
        Video Type: {video_type}
        
        Script:
        {script}
        
        Improve/add CTA that:
        1. Creates urgency
        2. Is specific and clear
        3. Offers value
        4. Uses pattern interrupt if needed
        5. Asks for specific action
        
        Return optimized script.
        """
        
        response = await self.openai_client.chat.completions.create(
            model=FAST_LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        return response.choices[0].message.content
    
    async def _extract_triggers(self, script: str) -> List[str]:
        """Extract psychological triggers used in script"""
        
        prompt = f"""
        Identify all psychological triggers in this script:
        
        {script}
        
        Return JSON with:
        {{
            "triggers": ["trigger1", "trigger2", ...]
        }}
        """
        
        response = await self.openai_client.chat.completions.create(
            model=FAST_LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            response_format={"type": "json_object"}
        )
        
        data = json.loads(response.choices[0].message.content)
        return data.get("triggers", [])
    
    async def generate_multiple_hooks(self, topic: str, num_hooks: int = 5,
                                     audience: str = "general") -> List[HookAnalysis]:
        """Generate multiple hook variations for A/B testing"""
        
        hooks = []
        hook_types = [
            HookType.CURIOSITY_GAP,
            HookType.PATTERN_INTERRUPT,
            HookType.STORY_HOOK,
            HookType.QUESTION_HOOK,
            HookType.MYSTERY_HOOK
        ]
        
        for hook_type in hook_types[:num_hooks]:
            try:
                hook = await self._generate_hook(topic, hook_type, audience, "energetic")
                hooks.append(hook)
            except Exception as e:
                logger.error(f"Error generating hook type {hook_type}: {str(e)}")
                continue
        
        return hooks


# Global instance
script_engine = ScriptPsychologyEngine()
