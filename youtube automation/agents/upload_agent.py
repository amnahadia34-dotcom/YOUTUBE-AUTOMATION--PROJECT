from typing import Dict, Any
from datetime import datetime
from agents.base_agent import BaseAgent, AgentRole
from services.youtube_service import upload_video_real
from services.scheduler_service import schedule_upload
from services.memory_service import MemoryService
from utils.logger import logger


class UploadAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_id="upload_agent", role=AgentRole.PUBLISHING)
        self.memory_service = MemoryService()

    async def _think(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "video_path": input_data.get("video_path"),
            "title": input_data.get("title"),
            "description": input_data.get("description"),
            "tags": input_data.get("tags", []),
            "privacy_status": input_data.get("privacy_status", "public"),
            "auto_upload": input_data.get("auto_upload", False),
            "schedule_publish": input_data.get("schedule_publish", False),
            "publish_at": input_data.get("publish_at")
        }

    async def _execute(self, analysis: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
        if analysis["schedule_publish"]:
            schedule_job = schedule_upload(
                video_path=analysis["video_path"],
                title=analysis["title"],
                description=analysis["description"],
                publish_at=analysis["publish_at"],
                privacy_status=analysis["privacy_status"]
            )
            return {
                "status": "scheduled",
                "schedule_job": schedule_job
            }

        if analysis["auto_upload"]:
            youtube_url = upload_video_real(
                video_path=analysis["video_path"],
                title=analysis["title"],
                description=analysis["description"],
                tags=analysis["tags"],
                privacy_status=analysis["privacy_status"]
            )
            return {
                "status": "uploaded",
                "youtube_url": youtube_url,
                "published_at": datetime.utcnow().isoformat()
            }

        return {
            "status": "ready",
            "note": "Video is ready for manual upload."
        }

    async def _learn(self, input_data: Dict[str, Any], result: Dict[str, Any]):
        if result.get("youtube_url"):
            self.memory_service.save_video_record({
                "video_id": input_data.get("video_id", "unknown"),
                "title": input_data.get("title", ""),
                "topic": input_data.get("topic", ""),
                "script": input_data.get("script", ""),
                "thumbnail_path": input_data.get("thumbnail_path", ""),
                "published_at": result.get("published_at", datetime.utcnow().isoformat()),
                "ctr": 0.0,
                "watch_time_minutes": 0.0,
                "retention_percentage": 0.0,
                "likes": 0,
                "comments": 0,
                "shares": 0
            })
        logger.info("UploadAgent updated memory state")
