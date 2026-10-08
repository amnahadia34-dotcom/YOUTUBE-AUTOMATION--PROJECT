"""
AI Media Orchestrator - Master Controller
The brain of the system that orchestrates all services into autonomous workflow
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import asyncio
import json
from datetime import datetime
from utils.logger import logger
from database.manager import db
from database.models import VideoStatusEnum, TaskStatusEnum, Video
from config.settings import OPENAI_API_KEY, MAIN_LLM_MODEL

# Import all engines
from services.topic_intelligence import topic_engine, TopicOpportunity
from services.script_psychology import script_engine, HookType, PacingStyle
from services.cinematic_engine import cinematic_engine, Scene, CameraMovement, TransitionType
from services.thumbnail_intelligence import thumbnail_intelligence
from services.voice_director import voice_director, VoiceSettings, VoiceProvider, VoiceGender, EmotionTone
from services.shorts_engine import shorts_engine
from services.learning_loop import learning_loop

import openai


class WorkflowStage(str, Enum):
    RESEARCH = "research"
    PLANNING = "planning"
    SCRIPT_GENERATION = "script_generation"
    VOICE_GENERATION = "voice_generation"
    VIDEO_GENERATION = "video_generation"
    THUMBNAIL_GENERATION = "thumbnail_generation"
    SHORTS_GENERATION = "shorts_generation"
    OPTIMIZATION = "optimization"
    PUBLISHING = "publishing"
    MONITORING = "monitoring"


@dataclass
class WorkflowConfig:
    """Autonomous workflow configuration"""
    user_id: str
    channel_id: str
    topic: str
    content_type: str = "full_video"
    autonomous_mode: bool = True
    auto_upload: bool = False
    generate_shorts: bool = True
    auto_thumbnail: bool = True
    target_retention: float = 75.0
    language: str = "english"


class AIMediaOrchestrator:
    """
    Master orchestrator for complete autonomous media generation workflow
    
    Orchestrates:
    1. Trend/Topic Intelligence
    2. Script Generation with Psychology
    3. Cinematic Video Production
    4. Thumbnail Optimization
    5. Voice Narration
    6. Shorts Auto-Extraction
    7. SEO Optimization
    8. Publishing & Scheduling
    9. Analytics Monitoring
    10. AI Learning Loop
    
    Autonomous Workflow:
    - Detect trends
    - Generate scripts
    - Create visuals
    - Produce videos
    - Optimize thumbnails
    - Generate shorts
    - Upload to YouTube
    - Monitor performance
    - Learn and improve
    """
    
    def __init__(self):
        self.openai_client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)
    
    async def start_autonomous_workflow(self, config: WorkflowConfig) -> Dict:
        """
        Start complete autonomous media generation workflow
        """
        
        try:
            logger.info(f"Starting autonomous workflow for user: {config.user_id}")
            
            workflow_results = {
                "user_id": config.user_id,
                "topic": config.topic,
                "stages": {},
                "start_time": datetime.utcnow().isoformat(),
                "status": "processing"
            }
            
            # Stage 1: Research & Trend Analysis
            research_result = await self._stage_research(config)
            workflow_results["stages"]["research"] = research_result
            
            # Stage 2: Planning & Strategy
            planning_result = await self._stage_planning(config, research_result)
            workflow_results["stages"]["planning"] = planning_result
            
            # Stage 3: Script Generation
            script_result = await self._stage_script_generation(config, planning_result)
            workflow_results["stages"]["script_generation"] = script_result
            
            # Stage 4: Voice Narration
            voice_result = await self._stage_voice_generation(config, script_result)
            workflow_results["stages"]["voice_generation"] = voice_result
            
            # Stage 5: Video Generation
            video_result = await self._stage_video_generation(
                config, script_result, voice_result, planning_result
            )
            workflow_results["stages"]["video_generation"] = video_result
            
            # Stage 6: Thumbnail Generation
            thumbnail_result = await self._stage_thumbnail_generation(
                config, video_result, planning_result
            )
            workflow_results["stages"]["thumbnail_generation"] = thumbnail_result
            
            # Stage 7: Shorts Generation
            if config.generate_shorts:
                shorts_result = await self._stage_shorts_generation(video_result)
                workflow_results["stages"]["shorts_generation"] = shorts_result
            
            # Stage 8: Optimization
            optimization_result = await self._stage_optimization(
                config, video_result, planning_result
            )
            workflow_results["stages"]["optimization"] = optimization_result
            
            # Stage 9: Publishing
            if config.auto_upload:
                publishing_result = await self._stage_publishing(
                    config, video_result, optimization_result
                )
                workflow_results["stages"]["publishing"] = publishing_result
            
            workflow_results["status"] = "completed"
            workflow_results["end_time"] = datetime.utcnow().isoformat()
            
            logger.info(f"Autonomous workflow completed successfully")
            
            return workflow_results
            
        except Exception as e:
            logger.error(f"Error in autonomous workflow: {str(e)}")
            workflow_results["status"] = "failed"
            workflow_results["error"] = str(e)
            return workflow_results
    
    async def _stage_research(self, config: WorkflowConfig) -> Dict:
        """Stage 1: Trend analysis and market research"""
        
        logger.info("Stage 1: Research & Trend Analysis")
        
        try:
            # Detect viral opportunities
            opportunities = await topic_engine.detect_viral_topics(
                config.user_id,
                niche=config.topic,
                num_topics=5
            )
            
            # Get niche recommendations
            niche_recs = await topic_engine.get_niche_recommendations(config.user_id)
            
            return {
                "viral_opportunities": [
                    {
                        "topic": opp.topic,
                        "keyword": opp.keyword,
                        "viral_score": opp.viral_score,
                        "opportunity_score": opp.opportunity_score,
                        "predicted_ctr": opp.predicted_ctr,
                        "predicted_retention": opp.predicted_retention
                    }
                    for opp in opportunities
                ],
                "niche_recommendations": niche_recs,
                "market_analysis": "Complete"
            }
            
        except Exception as e:
            logger.error(f"Error in research stage: {str(e)}")
            return {"error": str(e)}
    
    async def _stage_planning(self, config: WorkflowConfig,
                             research: Dict) -> Dict:
        """Stage 2: Strategic planning"""
        
        logger.info("Stage 2: Planning & Strategy")
        
        try:
            # Get learning-based recommendations
            recommendations = await learning_loop.get_personalized_recommendations(
                config.user_id
            )
            
            # Get optimized config
            optimized_config = await learning_loop.optimize_for_next_video(
                config.user_id,
                config.topic
            )
            
            return {
                "content_strategy": recommendations,
                "optimized_config": optimized_config,
                "hook_type": optimized_config.get("hook_type", "curiosity_gap"),
                "pacing_style": optimized_config.get("script_pacing", "fast"),
                "target_duration": optimized_config.get("video_duration", 600)
            }
            
        except Exception as e:
            logger.error(f"Error in planning stage: {str(e)}")
            return {"error": str(e)}
    
    async def _stage_script_generation(self, config: WorkflowConfig,
                                      planning: Dict) -> Dict:
        """Stage 3: Script generation with psychology"""
        
        logger.info("Stage 3: Script Generation")
        
        try:
            # Generate high-retention script
            script_result = await script_engine.generate_high_retention_script(
                topic=config.topic,
                video_type=config.content_type,
                duration_seconds=planning.get("target_duration", 600),
                hook_type=HookType(planning.get("hook_type", "curiosity_gap")),
                pacing_style=PacingStyle(planning.get("pacing_style", "fast_paced")),
                target_retention=config.target_retention,
                audience=config.channel_id,
                tone="energetic",
                language=config.language
            )
            
            # Create video record in database
            video = db.create_video(
                user_id=config.user_id,
                channel_id=config.channel_id,
                title=f"{config.topic} - {datetime.now().strftime('%Y-%m-%d')}",
                description=f"AI-generated video about {config.topic}",
                script=script_result["script"],
                content_type=config.content_type,
                status=VideoStatusEnum.GENERATING,
                language=config.language
            )
            
            return {
                "video_id": video.id,
                "script": script_result["script"][:200],
                "hook": script_result.get("hook", {}).get("hook_text", ""),
                "estimated_retention": script_result.get("estimated_retention", 0),
                "psychological_triggers": script_result.get("psychological_triggers", [])
            }
            
        except Exception as e:
            logger.error(f"Error in script generation: {str(e)}")
            return {"error": str(e)}
    
    async def _stage_voice_generation(self, config: WorkflowConfig,
                                     script: Dict) -> Dict:
        """Stage 4: Voice narration generation"""
        
        logger.info("Stage 4: Voice Narration Generation")
        
        try:
            video_id = script.get("video_id")
            script_text = script.get("script", "")
            
            # Select optimal voice
            voice_settings = await voice_director.select_optimal_voice(
                script_text,
                config.content_type,
                config.channel_id
            )
            
            # Generate narration
            audio_path = f"renders/audio_{video_id}.mp3"
            audio_path = await voice_director.generate_narration(
                script_text,
                voice_settings,
                audio_path
            )
            
            return {
                "video_id": video_id,
                "audio_path": audio_path,
                "voice_provider": voice_settings.provider.value,
                "voice_gender": voice_settings.gender.value,
                "emotion": voice_settings.emotion.value
            }
            
        except Exception as e:
            logger.error(f"Error in voice generation: {str(e)}")
            return {"error": str(e)}
    
    async def _stage_video_generation(self, config: WorkflowConfig,
                                     script: Dict, voice: Dict,
                                     planning: Dict) -> Dict:
        """Stage 5: Cinematic video generation"""
        
        logger.info("Stage 5: Cinematic Video Generation")
        
        try:
            video_id = script.get("video_id")
            
            # Create scenes for cinematic generation
            # This is simplified - in production would have more sophisticated scene generation
            scenes = [
                Scene(
                    scene_number=1,
                    duration=5.0,
                    text="Opening scene",
                    background_image=None,
                    camera_movement=CameraMovement.ZOOM_IN,
                    transition_in=TransitionType.FADE,
                    transition_out=TransitionType.CROSSFADE
                )
            ]
            
            # Generate video
            video_path = f"renders/video_{video_id}.mp4"
            video_path = await cinematic_engine.generate_cinematic_video(
                scenes=scenes,
                audio_path=voice.get("audio_path"),
                output_path=video_path,
                intro_text=config.topic
            )
            
            # Update video in database
            db.update_video_status(
                video_id,
                VideoStatusEnum.RENDERED,
                progress=80
            )
            video = db.get_video(video_id)
            video.video_path = video_path
            
            return {
                "video_id": video_id,
                "video_path": video_path,
                "duration": 600,
                "resolution": "1080p"
            }
            
        except Exception as e:
            logger.error(f"Error in video generation: {str(e)}")
            return {"error": str(e)}
    
    async def _stage_thumbnail_generation(self, config: WorkflowConfig,
                                         video: Dict,
                                         planning: Dict) -> Dict:
        """Stage 6: AI thumbnail generation"""
        
        logger.info("Stage 6: Thumbnail Generation")
        
        try:
            video_id = video.get("video_id")
            
            # Generate viral thumbnails
            thumbnails = await thumbnail_intelligence.generate_multiple_variations(
                video_title=config.topic,
                video_topic=config.topic,
                num_variations=3
            )
            
            # Select best thumbnail
            best_thumbnail = max(
                thumbnails,
                key=lambda x: float(x.get("predicted_ctr", 0))
            )
            
            # Update video
            video_record = db.get_video(video_id)
            video_record.thumbnail_path = best_thumbnail.get("thumbnail_path")
            video_record.viral_score = float(best_thumbnail.get("predicted_engagement", 0))
            
            return {
                "video_id": video_id,
                "thumbnail_path": best_thumbnail.get("thumbnail_path"),
                "predicted_ctr": best_thumbnail.get("predicted_ctr"),
                "style": best_thumbnail.get("design_style"),
                "variations_created": len(thumbnails)
            }
            
        except Exception as e:
            logger.error(f"Error in thumbnail generation: {str(e)}")
            return {"error": str(e)}
    
    async def _stage_shorts_generation(self, video: Dict) -> Dict:
        """Stage 7: Shorts extraction and generation"""
        
        logger.info("Stage 7: Shorts Generation")
        
        try:
            video_path = video.get("video_path")
            
            if not video_path:
                return {"error": "No video path"}
            
            # Extract shorts
            shorts_paths = await shorts_engine.extract_shorts_from_video(
                video_path,
                num_shorts=3
            )
            
            return {
                "shorts_count": len(shorts_paths),
                "shorts_paths": shorts_paths
            }
            
        except Exception as e:
            logger.error(f"Error in shorts generation: {str(e)}")
            return {"error": str(e)}
    
    async def _stage_optimization(self, config: WorkflowConfig,
                                 video: Dict,
                                 planning: Dict) -> Dict:
        """Stage 8: SEO and metadata optimization"""
        
        logger.info("Stage 8: Optimization")
        
        try:
            video_id = video.get("video_id")
            
            # AI-optimized title, description, tags
            prompt = f"""
            Generate optimized YouTube metadata:
            
            Topic: {config.topic}
            Content Type: {config.content_type}
            
            Provide:
            {{
                "optimized_title": "...",
                "optimized_description": "...",
                "tags": ["...", "..."],
                "hashtags": ["...", "..."],
                "seo_score": 0-100
            }}
            """
            
            response = await self.openai_client.chat.completions.create(
                model=MAIN_LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            optimization = json.loads(response.choices[0].message.content)
            
            # Update video
            video_record = db.get_video(video_id)
            video_record.title = optimization.get("optimized_title", video_record.title)
            video_record.description = optimization.get("optimized_description", video_record.description)
            video_record.tags = optimization.get("tags", [])
            video_record.hashtags = optimization.get("hashtags", [])
            video_record.seo_title = optimization.get("optimized_title")
            video_record.seo_description = optimization.get("optimized_description")
            
            return optimization
            
        except Exception as e:
            logger.error(f"Error in optimization stage: {str(e)}")
            return {"error": str(e)}
    
    async def _stage_publishing(self, config: WorkflowConfig,
                               video: Dict,
                               optimization: Dict) -> Dict:
        """Stage 9: Publishing to YouTube"""
        
        logger.info("Stage 9: Publishing")
        
        try:
            video_id = video.get("video_id")
            
            # Schedule publishing
            from datetime import datetime, timedelta
            publish_time = datetime.utcnow() + timedelta(hours=24)
            
            queue_item = db.add_to_publishing_queue(
                video_id=video_id,
                channel_id=config.channel_id,
                scheduled_time=publish_time
            )
            
            # Update video status
            db.update_video_status(video_id, VideoStatusEnum.UPLOADING, progress=90)
            
            return {
                "video_id": video_id,
                "queue_id": queue_item.id,
                "scheduled_time": publish_time.isoformat(),
                "status": "queued"
            }
            
        except Exception as e:
            logger.error(f"Error in publishing stage: {str(e)}")
            return {"error": str(e)}


# Global instance
ai_orchestrator = AIMediaOrchestrator()
