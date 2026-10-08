"""
SEO AGENT - Predictive SEO & Viral Engine

Responsibilities:
- Estimated CTR prediction
- Viral probability calculation
- Best upload timing analysis
- Audience matching
- SEO optimization
- Ranking prediction
"""

import json
from typing import Dict, Any, List
from agents.base_agent import BaseAgent, AgentRole
from config.settings import OPENAI_API_KEY
from openai import OpenAI
from utils.logger import logger


class SEOAgent(BaseAgent):
    """
    SEO Agent for viral prediction and optimization
    """
    
    def __init__(self, agent_id: str = "seo_agent_1"):
        super().__init__(agent_id, AgentRole.SEO)
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.learning_state = {
            "successful_optimizations": [],
            "failed_keywords": [],
            "best_upload_times": []
        }
    
    async def _think(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze SEO requirements"""
        logger.info("SEO Agent analyzing requirements")
        
        return {
            "topic": input_data.get("topic"),
            "research_data": input_data.get("research_data", {}),
            "competitors": input_data.get("competitors", []),
            "target_audience": input_data.get("target_audience", "general"),
            "optimization_goals": [
                "maximize_ctr",
                "predict_virality",
                "rank_higher",
                "increase_engagement"
            ]
        }
    
    async def _execute(self, analysis: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute SEO optimization"""
        try:
            topic = analysis.get("topic")
            research_data = analysis.get("research_data", {})
            
            prompt = f"""
As an elite YouTube SEO strategist, optimize this content for viral potential and ranking:

TOPIC: {topic}
RESEARCH: {json.dumps(research_data, indent=2)}

Provide optimization as JSON:
{{
    "optimized_title": "Best YouTube title (max 60 chars)",
    "seo_description": "Optimized description (2-3 paragraphs)",
    "keywords": ["keyword1", "keyword2", ...],
    "hashtags": ["#hashtag1", "#hashtag2"],
    "estimated_ctr": 0.0,
    "viral_probability": 0.0,
    "best_upload_time": "HH:MM (UTC)",
    "upload_day": "Monday-Sunday",
    "ranking_difficulty": 0.0,
    "content_gaps": ["gap1", "gap2"],
    "seo_score": 0.0,
    "optimization_notes": "Strategy notes"
}}

Return ONLY valid JSON.
"""
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a YouTube SEO expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            seo_data = json.loads(response.choices[0].message.content)
            
            return {
                "topic": topic,
                "seo_optimization": seo_data,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"SEO execution failed: {str(e)}")
            return {"error": str(e), "status": "failed"}
    
    async def _learn(self, input_data: Dict[str, Any], result: Dict[str, Any]):
        """Learn from SEO optimizations"""
        if result.get("status") == "success":
            self.learning_state["successful_optimizations"].append({
                "topic": result.get("topic"),
                "seo_data": result.get("seo_optimization")
            })
    
    async def predict_ctr(self, title: str, thumbnail: str, script: str) -> float:
        """Predict CTR based on content"""
        logger.info("Predicting CTR")
        
        prompt = f"""
Predict the CTR (Click-Through Rate) for this YouTube video:

TITLE: {title}
THUMBNAIL: {thumbnail}
SCRIPT PREVIEW: {script[:200]}

Return ONLY a number between 0 and 1 representing estimated CTR.
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a YouTube analytics expert."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            ctr_str = response.choices[0].message.content.strip()
            ctr = float(ctr_str)
            return min(max(ctr, 0.0), 1.0)
            
        except Exception as e:
            logger.error(f"CTR prediction failed: {str(e)}")
            return 0.05  # Default CTR
    
    async def predict_virality(self, content_data: Dict[str, Any]) -> float:
        """Predict viral probability (0-1)"""
        logger.info("Predicting virality")
        
        prompt = f"""
What is the viral probability (0-1) for this content?

{json.dumps(content_data, indent=2)}

Return ONLY a number between 0 and 1.
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a viral content expert."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            viral_str = response.choices[0].message.content.strip()
            viral = float(viral_str)
            return min(max(viral, 0.0), 1.0)
            
        except Exception as e:
            logger.error(f"Virality prediction failed: {str(e)}")
            return 0.5
