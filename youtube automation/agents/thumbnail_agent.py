from typing import Dict, Any
from agents.base_agent import BaseAgent, AgentRole
from services.thumbnail_service import create_ai_thumbnail
from services.memory_service import MemoryService
from utils.logger import logger


class ThumbnailAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_id="thumbnail_agent", role=AgentRole.THUMBNAIL)
        self.memory_service = MemoryService()

    async def _think(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        topic = input_data.get("topic", "AI Video")
        language = input_data.get("language", "English")
        return {
            "prompt": topic,
            "language": language,
            "style": input_data.get("thumbnail_style", "cinematic")
        }

    async def _execute(self, analysis: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
        thumbnail_path = create_ai_thumbnail(
            topic=analysis["prompt"],
            language=analysis["language"]
        )
        return {
            "thumbnail_path": thumbnail_path,
            "predicted_ctr": 0.12,
            "style": analysis["style"]
        }

    async def _learn(self, input_data: Dict[str, Any], result: Dict[str, Any]):
        if result.get("thumbnail_path"):
            self.memory_service.remember_channel_tone({"bold_thumbnail": 1.0})
        logger.info("ThumbnailAgent stored thumbnail insights")
