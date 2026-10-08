from typing import Dict, Any
from agents.base_agent import BaseAgent, AgentRole
from services.analytics_service import AnalyticsTracker
from services.memory_service import MemoryService
from utils.logger import logger


class AnalyticsAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_id="analytics_agent", role=AgentRole.ANALYTICS)
        self.analytics = AnalyticsTracker()
        self.memory_service = MemoryService()

    async def _think(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "video_id": input_data.get("video_id"),
            "performance": input_data.get("performance", {}),
            "analysis_window": input_data.get("analysis_window", 30)
        }

    async def _execute(self, analysis: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
        if analysis["performance"]:
            recorded = self.analytics.record_video_metrics({
                "video_id": analysis["video_id"],
                "title": input_data.get("title", ""),
                "topic": input_data.get("topic", ""),
                "script": input_data.get("script", ""),
                "thumbnail_path": input_data.get("thumbnail_path", ""),
                "published_at": input_data.get("published_at"),
                "ctr": analysis["performance"].get("ctr", 0.0),
                "watch_time_minutes": analysis["performance"].get("watch_time_minutes", 0.0),
                "retention_percentage": analysis["performance"].get("retention_percentage", 0.0),
                "likes": analysis["performance"].get("likes", 0),
                "comments": analysis["performance"].get("comments", 0),
                "shares": analysis["performance"].get("shares", 0),
                "audience_demographics": analysis["performance"].get("audience_demographics", {})
            })
            return {
                "status": "recorded" if recorded else "failed",
                "summary": self.analytics.get_video_analytics(analysis["video_id"])
            }

        return {"status": "no_data", "summary": self.analytics.get_channel_overview()}

    async def _learn(self, input_data: Dict[str, Any], result: Dict[str, Any]):
        self.memory_service.update_audience_interests({
            input_data.get("topic", "unknown"): input_data.get("performance", {}).get("ctr", 0.0)
        })
        logger.info("AnalyticsAgent updated memory and audience interest")
