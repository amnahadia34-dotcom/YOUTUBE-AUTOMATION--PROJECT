"""
RESEARCH AGENT - AI Topic Intelligence Engine

Responsibilities:
- YouTube trend analysis
- Competitor monitoring
- Viral topic prediction
- Audience interest analysis
- Niche opportunity detection
"""

import asyncio
from typing import Dict, Any, List
from agents.base_agent import BaseAgent, AgentRole
from config.settings import OPENAI_API_KEY
from openai import OpenAI
from utils.logger import logger
import json


class ResearchAgent(BaseAgent):
    """
    Research Agent for autonomous topic intelligence.
    Analyzes trends, competitors, and predicts viral opportunities.
    """
    
    def __init__(self, agent_id: str = "research_agent_1"):
        super().__init__(agent_id, AgentRole.RESEARCH)
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.learning_state = {
            "successful_topics": [],
            "failed_topics": [],
            "trend_history": []
        }
    
    async def _think(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze research requirements and plan approach
        """
        logger.info(f"Research Agent thinking about: {input_data.get('topic', 'general')}")
        
        user_topic = input_data.get("topic", "")
        language = input_data.get("language", "english")
        niche = input_data.get("niche", "general")
        
        # Analysis plan
        analysis_plan = {
            "topic": user_topic,
            "research_dimensions": [
                "trend_score",
                "viral_probability",
                "audience_interests",
                "competitor_analysis",
                "opportunity_gaps",
                "content_saturation"
            ],
            "data_sources": [
                "youtube_trends",
                "search_trends",
                "social_media",
                "news_api",
                "competitor_content"
            ],
            "language": language,
            "niche": niche
        }
        
        return analysis_plan
    
    async def _execute(self, analysis: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute comprehensive research on the topic
        """
        topic = analysis.get("topic", "")
        language = analysis.get("language", "english")
        
        try:
            # Use OpenAI for intelligent research
            prompt = f"""
You are an elite YouTube content research specialist. Perform comprehensive market research for a YouTube video.

Topic: {topic}
Language: {language}
Target Niche: {analysis.get('niche', 'general')}

Provide detailed analysis in JSON format with these fields:
1. trend_score (0-10): How trending is this topic currently
2. viral_probability (0-1): Estimated probability of going viral
3. estimated_ctr (0-1): Expected click-through rate
4. optimal_upload_time: Best time to upload
5. trending_keywords: Related trending keywords
6. competitor_analysis: What competitors are doing
7. content_gaps: Underserved content angles
8. audience_demographics: Target audience profile
9. content_saturation (0-10): How saturated is this topic
10. opportunity_level: Level of opportunity (low/medium/high)
11. recommended_hooks: Suggested video hooks
12. content_angles: Different angles to approach this topic
13. related_topics: Related topics that might perform well
14. success_factors: Key factors for success
15. risk_factors: Potential risks

Return ONLY valid JSON, no markdown.
"""
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert YouTube research analyst. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                top_p=0.9
            )
            
            research_data = json.loads(response.choices[0].message.content)
            
            return {
                "topic": topic,
                "research_data": research_data,
                "status": "success",
                "analysis_timestamp": asyncio.get_event_loop().time()
            }
            
        except Exception as e:
            logger.error(f"Research execution failed: {str(e)}")
            return {
                "topic": topic,
                "error": str(e),
                "status": "failed"
            }
    
    async def _learn(self, input_data: Dict[str, Any], result: Dict[str, Any]):
        """
        Learn from research results for future improvements
        """
        topic = result.get("topic", "")
        
        if result.get("status") == "success":
            research_data = result.get("research_data", {})
            
            # Store successful topics
            if research_data.get("viral_probability", 0) > 0.7:
                self.learning_state["successful_topics"].append({
                    "topic": topic,
                    "viral_probability": research_data.get("viral_probability"),
                    "trend_score": research_data.get("trend_score")
                })
            
            # Store trend data for pattern recognition
            self.learning_state["trend_history"].append({
                "topic": topic,
                "research_data": research_data,
                "timestamp": asyncio.get_event_loop().time()
            })
            
            logger.info(f"Research Agent learning: Successfully researched {topic}")
        else:
            self.learning_state["failed_topics"].append(topic)
    
    async def analyze_competitors(self, competitor_channels: List[str]) -> Dict[str, Any]:
        """
        Analyze competitor channels for insights
        """
        logger.info(f"Analyzing {len(competitor_channels)} competitor channels")
        
        # This would integrate with YouTube API to pull competitor data
        analysis = {
            "competitors": competitor_channels,
            "average_ctr": 0.0,
            "common_topics": [],
            "upload_frequency": 0,
            "average_engagement": 0,
            "content_themes": []
        }
        
        return analysis
    
    async def predict_next_trends(self) -> List[Dict[str, Any]]:
        """
        Use learning state to predict next trending topics
        """
        if not self.learning_state["trend_history"]:
            return []
        
        prompt = f"""
Based on this trend history data, predict the top 5 next trending YouTube topics:

{json.dumps(self.learning_state['trend_history'][-10:], indent=2)}

Return as JSON array with objects containing: topic, confidence, reasoning, recommended_angle
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a trend prediction expert."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            predictions = json.loads(response.choices[0].message.content)
            return predictions
            
        except Exception as e:
            logger.error(f"Trend prediction failed: {str(e)}")
            return []
