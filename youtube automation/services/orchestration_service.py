"""
Master Orchestration Service - THE BRAIN OF THE AI MEDIA OPERATING SYSTEM

This service coordinates all components:
- Research and topic generation
- Script creation with optimization
- Scene planning and storyboarding
- Video generation and rendering
- Voice generation and dubbing
- Thumbnail creation
- SEO optimization
- Publishing and scheduling
- Analytics and learning
"""

import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
from openai import OpenAI
from config.settings import OPENAI_API_KEY, MAIN_LLM_MODEL, FAST_LLM_MODEL
from utils.logger import logger


class PipelineStage(str, Enum):
    """Pipeline execution stages"""
    RESEARCH = "research"
    SCRIPTING = "scripting"
    SCENE_PLANNING = "scene_planning"
    RENDERING = "rendering"
    VOICE_GENERATION = "voice_generation"
    DUBBING = "dubbing"
    THUMBNAIL_CREATION = "thumbnail_creation"
    SEO_OPTIMIZATION = "seo_optimization"
    PUBLISHING = "publishing"
    COMPLETED = "completed"


@dataclass
class PipelineTask:
    task_id: str
    stage: PipelineStage
    status: str
    progress: float
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    error: Optional[str] = None
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["stage"] = self.stage.value
        data["created_at"] = self.created_at.isoformat() if self.created_at else None
        data["started_at"] = self.started_at.isoformat() if self.started_at else None
        data["completed_at"] = self.completed_at.isoformat() if self.completed_at else None
        return data


class OrchestrationService:
    def __init__(self):
        self.active_tasks: Dict[str, PipelineTask] = {}
        self.task_history: List[PipelineTask] = []
        self._load_services()
        self._register_agents()
        logger.info("Orchestration Service initialized")

    def _load_services(self):
        from services.topic_service import TopicService
        from services.competitor_service import CompetitorService
        from services.avatar_service import AvatarService
        from services.dubbing_service import DubbingService
        from services.music_service import MusicService
        from services.thumbnail_service import create_ai_thumbnail
        from services.analytics_service import AnalyticsService
        from services.memory_service import MemoryService
        from services.scene_director import SceneDirectorService
        from services.retention_service import get_retention_optimization_service

        self.topic_service = TopicService()
        self.competitor_service = CompetitorService()
        self.avatar_service = AvatarService()
        self.dubbing_service = DubbingService()
        self.music_service = MusicService()
        self.thumbnail_service = create_ai_thumbnail
        self.analytics_service = AnalyticsService()
        self.memory_service = MemoryService()
        self.scene_director_service = SceneDirectorService()
        self.retention_service = get_retention_optimization_service()

    def _register_agents(self):
        from agents.base_agent import get_agent_coordinator
        from agents.trend_agent import TrendAgent
        from agents.thumbnail_agent import ThumbnailAgent
        from agents.video_agent import VideoAgent
        from agents.upload_agent import UploadAgent
        from agents.analytics_agent import AnalyticsAgent
        from agents.script_agent import ScriptAgent
        from agents.seo_agent import SEOAgent

        self.agent_coordinator = get_agent_coordinator()
        self.agent_coordinator.register_agent(TrendAgent())
        self.agent_coordinator.register_agent(ThumbnailAgent())
        self.agent_coordinator.register_agent(VideoAgent())
        self.agent_coordinator.register_agent(UploadAgent())
        self.agent_coordinator.register_agent(AnalyticsAgent())
        self.agent_coordinator.register_agent(ScriptAgent())
        self.agent_coordinator.register_agent(SEOAgent())

    async def start_autonomous_pipeline(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        task_id = request_data.get("task_id") or self._generate_task_id()
        task = self._create_pipeline_task(task_id, request_data)
        self.active_tasks[task_id] = task
        self._persist_task(task)

        try:
            logger.info(f"Starting autonomous pipeline: {task_id}")
            await self._execute_stage(task, PipelineStage.RESEARCH)
            await self._execute_stage(task, PipelineStage.SCRIPTING)
            await self._execute_stage(task, PipelineStage.SCENE_PLANNING)
            await self._execute_stage(task, PipelineStage.RENDERING)
            await self._execute_stage(task, PipelineStage.VOICE_GENERATION)
            if task.input_data.get("enable_dubbing", False):
                await self._execute_stage(task, PipelineStage.DUBBING)
            await self._execute_stage(task, PipelineStage.THUMBNAIL_CREATION)
            await self._execute_stage(task, PipelineStage.SEO_OPTIMIZATION)
            await self._execute_stage(task, PipelineStage.PUBLISHING)

            task.stage = PipelineStage.COMPLETED
            task.status = "completed"
            task.progress = 100.0
            task.completed_at = datetime.utcnow()
            self.task_history.append(task)
            self._persist_task(task)

            return {
                "task_id": task_id,
                "status": task.status,
                "progress": task.progress,
                "output": task.output_data,
                "created_at": task.created_at.isoformat()
            }
        except Exception as exc:
            logger.error(f"Pipeline failed: {str(exc)}", exc_info=True)
            task.status = "failed"
            task.error = str(exc)
            task.completed_at = datetime.utcnow()
            self._persist_task(task)
            return {
                "task_id": task_id,
                "status": "failed",
                "error": str(exc),
                "output": task.output_data
            }

    async def _execute_stage(self, task: PipelineTask, stage: PipelineStage):
        logger.info(f"Executing stage {stage.value} for task {task.task_id}")
        task.stage = stage
        task.status = "processing"
        task.started_at = datetime.utcnow()

        if stage == PipelineStage.RESEARCH:
            await self._research_stage(task)
        elif stage == PipelineStage.SCRIPTING:
            await self._scripting_stage(task)
        elif stage == PipelineStage.SCENE_PLANNING:
            await self._scene_planning_stage(task)
        elif stage == PipelineStage.RENDERING:
            await self._rendering_stage(task)
        elif stage == PipelineStage.VOICE_GENERATION:
            await self._voice_stage(task)
        elif stage == PipelineStage.DUBBING:
            await self._dubbing_stage(task)
        elif stage == PipelineStage.THUMBNAIL_CREATION:
            await self._thumbnail_stage(task)
        elif stage == PipelineStage.SEO_OPTIMIZATION:
            await self._seo_stage(task)
        elif stage == PipelineStage.PUBLISHING:
            await self._publishing_stage(task)

        task.status = "completed"
        task.completed_at = datetime.utcnow()
        self._persist_task(task)

    async def _research_stage(self, task: PipelineTask):
        task.progress = 10
        research_agent = self.agent_coordinator.agents.get("research")
        research_task = AgentTask(
            task_id=f"{task.task_id}_research",
            role=research_agent.role,
            input_data={
                "topic": task.input_data.get("topic", "AI automation"),
                "language": task.input_data.get("language", "English"),
                "competitor_channels": task.input_data.get("competitor_channels", [])
            },
            output_data={}
        )
        task.output_data["research"] = await research_agent.execute_task(research_task)
        task.input_data["topic"] = task.output_data["research"].get("topic", task.input_data.get("topic"))
        self._persist_task(task)

    async def _scripting_stage(self, task: PipelineTask):
        task.progress = 25
        script_agent = self.agent_coordinator.agents.get("script")
        script_task = AgentTask(
            task_id=f"{task.task_id}_script",
            role=script_agent.role,
            input_data={
                "topic": task.input_data.get("topic"),
                "language": task.input_data.get("language", "English"),
                "video_style": task.input_data.get("video_style", "cinematic")
            },
            output_data={}
        )
        task.output_data["script"] = await script_agent.execute_task(script_task)
        self._persist_task(task)

    async def _scene_planning_stage(self, task: PipelineTask):
        task.progress = 35
        script_data = task.output_data.get("script", {})
        script_text = script_data.get("full_script") or script_data.get("script") or script_data
        storyboard = await self.scene_director_service.create_storyboard(
            script={"topic": task.input_data.get("topic"), "scenes": self._convert_script_to_scenes(script_text)},
            research_data=task.output_data.get("research", {})
        )
        task.output_data["scene_plan"] = storyboard
        self._persist_task(task)

    async def _rendering_stage(self, task: PipelineTask):
        task.progress = 55
        video_agent = self.agent_coordinator.agents.get("video")
        video_task = AgentTask(
            task_id=f"{task.task_id}_video",
            role=video_agent.role,
            input_data={
                "script": task.output_data.get("script", {}).get("full_script"),
                "language": task.input_data.get("language", "English"),
                "video_style": task.input_data.get("video_style", "cinematic"),
                "enable_avatar": task.input_data.get("enable_avatar", False),
                "enable_shorts": task.input_data.get("enable_shorts", True),
                "shorts_count": task.input_data.get("shorts_count", 3),
                "music_mood": task.input_data.get("music_mood", "motivational"),
                "music_genre": task.input_data.get("music_genre", "cinematic"),
                "intro_text": task.input_data.get("intro_text"),
                "outro_text": task.input_data.get("outro_text")
            },
            output_data={}
        )
        task.output_data["rendering"] = await video_agent.execute_task(video_task)
        self._persist_task(task)

    async def _voice_stage(self, task: PipelineTask):
        task.progress = 65
        if not task.output_data.get("rendering", {}).get("voice_path"):
            from services.voice_service import generate_voice
            script_text = task.output_data.get("script", {}).get("full_script")
            voice_path = generate_voice(script_text, task.input_data.get("language", "English"))
            task.output_data.setdefault("rendering", {})["voice_path"] = voice_path
        self._persist_task(task)

    async def _dubbing_stage(self, task: PipelineTask):
        task.progress = 75
        target_languages = task.input_data.get("dubbing_languages", ["Spanish", "French", "Hindi"])
        script_text = task.output_data.get("script", {}).get("full_script")
        dubbed_versions = {}
        for language in target_languages:
            translated = self.dubbing_service.translate_script(
                script_text,
                task.input_data.get("language", "English"),
                language
            )
            audio_path = self.dubbing_service.generate_dubbed_audio(translated, language)
            dubbed_versions[language] = self.dubbing_service.create_dubbed_video(
                video_path=task.output_data.get("rendering", {}).get("mixed_video_path", task.output_data.get("rendering", {}).get("video_path")),
                dubbed_audio_path=audio_path,
                target_language=language
            )
        task.output_data["dubbing"] = dubbed_versions
        self._persist_task(task)

    async def _thumbnail_stage(self, task: PipelineTask):
        task.progress = 85
        thumbnail_agent = self.agent_coordinator.agents.get("thumbnail")
        thumbnail_task = AgentTask(
            task_id=f"{task.task_id}_thumbnail",
            role=thumbnail_agent.role,
            input_data={
                "topic": task.input_data.get("topic"),
                "language": task.input_data.get("language", "English"),
                "thumbnail_style": task.input_data.get("thumbnail_style", "cinematic")
            },
            output_data={}
        )
        task.output_data["thumbnail"] = await thumbnail_agent.execute_task(thumbnail_task)
        self._persist_task(task)

    async def _seo_stage(self, task: PipelineTask):
        task.progress = 90
        seo_agent = self.agent_coordinator.agents.get("seo")
        seo_task = AgentTask(
            task_id=f"{task.task_id}_seo",
            role=seo_agent.role,
            input_data={
                "topic": task.input_data.get("topic"),
                "script": task.output_data.get("script", {}).get("full_script"),
                "language": task.input_data.get("language", "English")
            },
            output_data={}
        )
        task.output_data["seo"] = await seo_agent.execute_task(seo_task)
        self._persist_task(task)

    async def _publishing_stage(self, task: PipelineTask):
        task.progress = 95
        upload_agent = self.agent_coordinator.agents.get("publishing")
        upload_task = AgentTask(
            task_id=f"{task.task_id}_publish",
            role=upload_agent.role,
            input_data={
                "video_path": task.output_data.get("rendering", {}).get("mixed_video_path", task.output_data.get("rendering", {}).get("video_path")),
                "title": task.output_data.get("seo", {}).get("title", task.input_data.get("manual_title", task.input_data.get("topic"))),
                "description": task.output_data.get("seo", {}).get("description", task.input_data.get("manual_description", "")),
                "tags": task.output_data.get("seo", {}).get("tags", []),
                "privacy_status": task.input_data.get("privacy_status", "public"),
                "auto_upload": task.input_data.get("auto_upload", False),
                "schedule_publish": task.input_data.get("schedule_publish", False),
                "publish_at": task.input_data.get("publish_at")
            },
            output_data={}
        )
        task.output_data["publishing"] = await upload_agent.execute_task(upload_task)
        self._record_analytics(task)
        self._persist_task(task)

    def _convert_script_to_scenes(self, script_text: str) -> List[Dict[str, Any]]:
        sentences = [sentence.strip() for sentence in script_text.split('.') if sentence.strip()]
        scenes = []
        for index, sentence in enumerate(sentences[:5], start=1):
            scenes.append({
                "scene_number": index,
                "script_text": sentence,
                "duration_seconds": max(6, min(12, len(sentence) / 16)),
                "visual_description": sentence[:120]
            })
        return scenes

    def _record_analytics(self, task: PipelineTask):
        performance = task.input_data.get("performance", {})
        self.analytics_service.record_video_metrics(
            video_id=task.task_id,
            title=task.output_data.get("seo", {}).get("title", task.input_data.get("topic", "")),
            topic=task.input_data.get("topic", ""),
            script=task.output_data.get("script", {}).get("full_script", ""),
            thumbnail_path=task.output_data.get("thumbnail", {}).get("thumbnail_path", ""),
            views=performance.get("views", 0),
            likes=performance.get("likes", 0),
            watch_time_seconds=performance.get("watch_time_seconds", 0.0),
            retention_rate=performance.get("retention_percentage", 0.0),
            comments=performance.get("comments", 0),
            shares=performance.get("shares", 0),
            ctr=performance.get("ctr", 0.0)
        )

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        task = self.active_tasks.get(task_id)
        return task.to_dict() if task else None

    def get_all_active_tasks(self) -> List[Dict[str, Any]]:
        return [task.to_dict() for task in self.active_tasks.values()]

    def get_task_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        return [task.to_dict() for task in self.task_history[-limit:]]

    def _create_pipeline_task(self, task_id: str, request_data: Dict[str, Any]) -> PipelineTask:
        return PipelineTask(
            task_id=task_id,
            stage=PipelineStage.RESEARCH,
            status="pending",
            progress=0.0,
            input_data=request_data,
            output_data={},
            created_at=datetime.utcnow()
        )

    def _generate_task_id(self) -> str:
        return f"task_{uuid.uuid4().hex[:12]}"

    async def get_pipeline_progress(self, task_id: str) -> Dict[str, Any]:
        task = self.active_tasks.get(task_id)
        if not task:
            return {"error": "Task not found"}
        return {
            "task_id": task_id,
            "stage": task.stage.value,
            "progress": task.progress,
            "status": task.status,
            "output_data": task.output_data
        }

    def _persist_task(self, task: PipelineTask):
        from database.database import DatabaseManager
        DatabaseManager.save_task(
            task_id=task.task_id,
            user_id=task.input_data.get("user_id", "anonymous"),
            topic=task.input_data.get("topic", ""),
            mode=task.input_data.get("mode", "Full AI Auto Mode"),
            payload=task.input_data,
            status=task.status,
            progress=int(task.progress),
            result=task.output_data,
            error=task.error
        )


_orchestration_service: Optional[OrchestrationService] = None


def get_orchestration_service() -> OrchestrationService:
    global _orchestration_service
    if _orchestration_service is None:
        _orchestration_service = OrchestrationService()
    return _orchestration_service
