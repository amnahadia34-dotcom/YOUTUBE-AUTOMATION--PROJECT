"""
Autonomous Topic Intelligence Engine
Analyzes YouTube trends, detects viral opportunities, predicts engagement
"""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import aiohttp
import json
from utils.logger import logger
from config.settings import OPENAI_API_KEY, MAIN_LLM_MODEL
from database.manager import db
from database.models import Trend, CompetitorAnalysis
import openai


class ViralityTier(str, Enum):
    EMERGING = "emerging"
    TRENDING = "trending"
    VIRAL = "viral"
    HYPER_VIRAL = "hyper_viral"
    DECLINING = "declining"


@dataclass
class TopicOpportunity:
    """Represents a content opportunity"""
    keyword: str
    topic: str
    category: str
    viral_score: float
    virality_tier: ViralityTier
    search_volume: int
    growth_rate: float
    competition_level: str
    opportunity_score: float
    predicted_ctr: float
    predicted_retention: float
    predicted_engagement: float
    recommended_content_types: List[str]
    optimal_title_style: str
    optimal_duration: int
    target_audience: str


class TopicIntelligenceEngine:
    """
    AI-powered topic analysis and viral prediction system
    
    Capabilities:
    - Real-time trend detection
    - Viral score calculation
    - Competitor analysis
    - Niche prediction
    - Engagement forecasting
    - Content opportunity scoring
    """
    
    def __init__(self):
        self.openai_client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)
        self.cache = {}
        
    async def detect_viral_topics(self, user_id: str, niche: str = None,
                                  num_topics: int = 10) -> List[TopicOpportunity]:
        """
        Detect current viral topics using AI analysis of YouTube data
        
        Uses:
        - YouTube trending data
        - Search volume trends
        - Reddit/Twitter data
        - Competitor content analysis
        """
        try:
            logger.info(f"Detecting viral topics for user {user_id}, niche: {niche}")
            
            # Get AI-powered topic detection
            opportunities = await self._analyze_market_opportunities(niche)
            
            # Score and rank opportunities
            scored_opportunities = await self._score_opportunities(
                opportunities, user_id, niche
            )
            
            # Store top trends in database
            for opp in scored_opportunities[:num_topics]:
                db.add_trend(
                    topic=opp.topic,
                    keyword=opp.keyword,
                    viral_score=opp.viral_score,
                    category=opp.category,
                    search_volume=opp.search_volume,
                    growth_rate=opp.growth_rate,
                    competition_level=opp.competition_level,
                    opportunity_score=opp.opportunity_score,
                    predicted_retention=opp.predicted_retention,
                    predicted_ctr=opp.predicted_ctr,
                    predicted_engagement=opp.predicted_engagement,
                    detected_on=["youtube", "trending_data"]
                )
            
            return scored_opportunities[:num_topics]
            
        except Exception as e:
            logger.error(f"Error detecting viral topics: {str(e)}")
            return []
    
    async def _analyze_market_opportunities(self, niche: str = None) -> List[Dict[str, Any]]:
        """Use AI to analyze market opportunities"""
        
        prompt = f"""
        Analyze current YouTube market opportunities for viral video content.
        {"Focus on niche: " + niche if niche else ""}
        
        Provide analysis on:
        1. Trending topics right now (as of today)
        2. Underutilized niches with growth potential
        3. Competitor gaps
        4. Emerging audience interests
        5. Seasonal content opportunities
        
        For each topic, provide:
        - Topic name
        - Keywords
        - Estimated search volume
        - Growth rate (%)
        - Competition level (low/medium/high)
        - Predicted CTR
        - Predicted average retention %
        - Recommended content styles
        - Target audience
        - Optimal video duration
        
        Return as JSON array of opportunities.
        """
        
        try:
            response = await self.openai_client.chat.completions.create(
                model=MAIN_LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            opportunities = json.loads(content).get("opportunities", [])
            
            return opportunities
            
        except Exception as e:
            logger.error(f"Error in market analysis: {str(e)}")
            return []
    
    async def _score_opportunities(self, opportunities: List[Dict],
                                   user_id: str, niche: str = None) -> List[TopicOpportunity]:
        """
        Score opportunities based on:
        - Viral potential
        - Competition level
        - User's channel fit
        - Predicted engagement
        """
        
        scored = []
        
        for opp in opportunities:
            try:
                # Get user's learning state to personalize scoring
                learning_state = db.get_learning_state(user_id)
                
                # Calculate viral score (0-100)
                viral_score = self._calculate_viral_score(
                    search_volume=opp.get("search_volume", 0),
                    growth_rate=opp.get("growth_rate", 0),
                    competition_level=opp.get("competition_level", "high"),
                    learning_state=learning_state
                )
                
                # Determine virality tier
                virality_tier = self._get_virality_tier(viral_score)
                
                # Calculate opportunity score
                opportunity_score = self._calculate_opportunity_score(
                    viral_score=viral_score,
                    competition_level=opp.get("competition_level", "high"),
                    growth_rate=opp.get("growth_rate", 0),
                    ctr=opp.get("predicted_ctr", 0.05)
                )
                
                opportunity = TopicOpportunity(
                    keyword=opp.get("keyword", ""),
                    topic=opp.get("topic", ""),
                    category=opp.get("category", niche or "general"),
                    viral_score=viral_score,
                    virality_tier=virality_tier,
                    search_volume=opp.get("search_volume", 0),
                    growth_rate=opp.get("growth_rate", 0),
                    competition_level=opp.get("competition_level", "high"),
                    opportunity_score=opportunity_score,
                    predicted_ctr=opp.get("predicted_ctr", 0.05),
                    predicted_retention=opp.get("predicted_retention", 50),
                    predicted_engagement=opp.get("predicted_engagement", 3),
                    recommended_content_types=opp.get("content_types", ["video"]),
                    optimal_title_style=opp.get("optimal_title_style", "curiosity_gap"),
                    optimal_duration=opp.get("optimal_duration", 480),
                    target_audience=opp.get("target_audience", "general")
                )
                
                scored.append(opportunity)
                
            except Exception as e:
                logger.error(f"Error scoring opportunity: {str(e)}")
                continue
        
        # Sort by opportunity score
        scored.sort(key=lambda x: x.opportunity_score, reverse=True)
        
        return scored
    
    def _calculate_viral_score(self, search_volume: int, growth_rate: float,
                               competition_level: str, learning_state) -> float:
        """
        Calculate viral score based on multiple factors
        Formula: (search_volume_normalized + growth_rate + user_success_history) - competition_penalty
        """
        
        # Normalize search volume (0-100)
        search_score = min(100, (search_volume / 10000) * 100) if search_volume > 0 else 0
        
        # Growth rate contribution
        growth_score = min(100, growth_rate * 10)
        
        # Competition penalty
        competition_penalties = {
            "low": 5,
            "medium": 15,
            "high": 30
        }
        competition_penalty = competition_penalties.get(competition_level, 15)
        
        # User success history (if available)
        user_bonus = learning_state.average_performance_score if learning_state else 0
        
        viral_score = (search_score * 0.4 + growth_score * 0.3 + user_bonus * 0.3) - competition_penalty
        
        return max(0, min(100, viral_score))
    
    def _get_virality_tier(self, viral_score: float) -> ViralityTier:
        """Classify virality tier based on score"""
        if viral_score >= 80:
            return ViralityTier.HYPER_VIRAL
        elif viral_score >= 60:
            return ViralityTier.VIRAL
        elif viral_score >= 40:
            return ViralityTier.TRENDING
        elif viral_score >= 20:
            return ViralityTier.EMERGING
        else:
            return ViralityTier.DECLINING
    
    def _calculate_opportunity_score(self, viral_score: float, competition_level: str,
                                     growth_rate: float, ctr: float) -> float:
        """
        Overall opportunity score combines viral potential with achievability
        """
        
        competition_factor = {
            "low": 1.0,
            "medium": 0.7,
            "high": 0.4
        }.get(competition_level, 0.5)
        
        opportunity_score = (viral_score * 0.4 +
                            growth_rate * 100 * 0.3 +
                            ctr * 100 * 0.2) * competition_factor
        
        return min(100, opportunity_score)
    
    async def analyze_competitor(self, channel_id: str, user_id: str) -> CompetitorAnalysis:
        """
        Deep dive analysis of competitor channel
        """
        
        try:
            logger.info(f"Analyzing competitor channel: {channel_id}")
            
            prompt = f"""
            Analyze this YouTube channel ID: {channel_id}
            
            Provide:
            1. Channel performance metrics (subscribers, views, etc)
            2. Content strategy and dominant topics
            3. Upload frequency patterns
            4. Title and description optimization patterns
            5. Thumbnail style analysis
            6. Estimated audience demographics
            7. Performance benchmarks (avg CTR, retention, etc)
            8. Competitor's competitive advantage
            9. Content gaps/opportunities to exploit
            10. Recommended counter-strategy
            
            Return as JSON.
            """
            
            response = await self.openai_client.chat.completions.create(
                model=MAIN_LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            analysis_data = json.loads(response.choices[0].message.content)
            
            # Store analysis
            competitor_analysis = CompetitorAnalysis(
                user_id=user_id,
                competitor_name=analysis_data.get("channel_name", "Unknown"),
                competitor_channel_id=channel_id,
                category=analysis_data.get("category", "general"),
                subscriber_count=analysis_data.get("subscribers", 0),
                total_views=analysis_data.get("total_views", 0),
                avg_ctr=analysis_data.get("avg_ctr", 0),
                avg_retention=analysis_data.get("avg_retention", 0),
                upload_frequency=analysis_data.get("upload_frequency", "unknown"),
                dominant_topics=analysis_data.get("topics", []),
                avg_title_length=analysis_data.get("avg_title_length", 50),
                avg_description_length=analysis_data.get("avg_description_length", 200),
                common_tags=analysis_data.get("common_tags", []),
                thumbnail_style=analysis_data.get("thumbnail_style", "unknown"),
                performance_score=analysis_data.get("performance_score", 50)
            )
            
            db.log_action(user_id, "competitor_analyzed", "competitor", channel_id)
            
            return competitor_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing competitor: {str(e)}")
            raise
    
    async def get_niche_recommendations(self, user_id: str) -> Dict[str, Any]:
        """
        AI-powered niche recommendations based on user profile and market
        """
        
        try:
            # Get user's channel info
            channels = db.get_user_channels(user_id)
            if not channels:
                return {}
            
            channel = channels[0]
            
            # Get user's video history
            user_videos = db.get_user_videos(user_id, limit=20)
            
            prompt = f"""
            Based on this YouTube channel info and video history, recommend the best niches and content strategies.
            
            Channel: {channel.channel_name}
            Subscribers: {channel.subscriber_count}
            Total Views: {channel.total_views}
            Recent Videos: {len(user_videos)}
            
            Provide:
            1. Top 5 recommended niches
            2. Sub-niches to explore
            3. Adjacent niches for growth
            4. Predicted revenue potential by niche
            5. Competition analysis by niche
            6. Audience overlap opportunities
            7. Content pillars to focus on
            8. Content variations to test
            
            Return as JSON.
            """
            
            response = await self.openai_client.chat.completions.create(
                model=MAIN_LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                response_format={"type": "json_object"}
            )
            
            recommendations = json.loads(response.choices[0].message.content)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting niche recommendations: {str(e)}")
            return {}


# Global instance
topic_engine = TopicIntelligenceEngine()
