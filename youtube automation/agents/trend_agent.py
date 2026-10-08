import asyncio
from typing import Dict, Any, List
from agents.base_agent import BaseAgent, AgentTask, AgentRole
from services.topic_service import TopicService
from services.competitor_service import CompetitorService
from services.memory_service import MemoryService
from utils.logger import logger


class TrendAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_id="trend_agent", role=AgentRole.RESEARCH)
        self.topic_service = TopicService()
        self.competitor_service = CompetitorService()
        self.memory_service = MemoryService()

    async def _think(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        topic = input_data.get("topic", "AI trends")
        language = input_data.get("language", "English")
        suggested = await self.topic_service.suggest_topics(topic, language)
        return {
            "topic": suggested["suggested_topics"][0] if suggested.get("suggested_topics") else topic,
            "language": language,
            "suggestions": suggested,
            "competitor_channels": input_data.get("competitor_channels", [])
        }

    async def _execute(self, analysis: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
        topic = analysis["topic"]
        language = analysis["language"]
        competitor_data = await self.competitor_service.analyze_competitors(
            topic=topic,
            competitor_channels=analysis.get("competitor_channels", []),
            language=language
        )
        research_data = await self.topic_service.research_topic(topic, language)
        return {
            "topic": topic,
            "language": language,
            "research": research_data,
            "competitor_analysis": competitor_data,
            "audience_insights": research_data.get("audience_intent", "")
        }

    async def _learn(self, input_data: Dict[str, Any], result: Dict[str, Any]):
        topic = result.get("topic")
        audience_signal = result.get("audience_insights")
        if topic:
            self.memory_service.remember_topic(topic, {"ctr": 0.0, "watch_time": 0.0})
            if isinstance(audience_signal, str):
                self.memory_service.update_audience_interests({topic: 0.5})
        logger.info(f"TrendAgent learned from topic: {topic}")
