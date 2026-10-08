"""
AI Learning Loop System
Self-improving AI that learns from video performance to optimize future content
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import json
import numpy as np
from datetime import datetime, timedelta
from utils.logger import logger
from database.manager import db
from database.models import VideoAnalytics, PerformanceLearning, ContentLearningState
import openai
from config.settings import OPENAI_API_KEY, MAIN_LLM_MODEL


@dataclass
class LearningInsight:
    """AI learning insight"""
    category: str  # title_style, thumbnail_style, etc
    element: str  # specific element
    effectiveness_score: float  # 0-100
    recommendation: str
    confidence: float  # 0-100


class AILearningLoop:
    """
    Self-improving AI system that:
    - Analyzes video performance
    - Identifies what works
    - Learns patterns
    - Makes smarter recommendations
    - Improves future content
    
    Features:
    - CTR optimization learning
    - Retention curve analysis
    - Title effectiveness scoring
    - Thumbnail design learning
    - Script pattern analysis
    - Audience preference discovery
    - Upload time optimization
    - Niche performance tracking
    """
    
    def __init__(self):
        self.openai_client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)
    
    async def analyze_video_performance(self, video_id: str, user_id: str):
        """
        Comprehensive analysis of video performance for learning
        """
        
        try:
            logger.info(f"Analyzing performance for video: {video_id}")
            
            # Get video data
            video = db.get_video(video_id)
            if not video:
                logger.error(f"Video not found: {video_id}")
                return
            
            # Get analytics
            analytics = db.get_video_analytics_history(video_id, days=30)
            if not analytics:
                logger.warning(f"No analytics for video: {video_id}")
                return
            
            # Extract performance metrics
            latest = analytics[-1] if analytics else None
            
            performance_data = {
                "video_id": video_id,
                "title": video.title,
                "topic": video.script[:100],
                "total_views": latest.views if latest else 0,
                "ctr": latest.ctr if latest else 0,
                "retention": latest.avg_view_percentage if latest else 0,
                "likes_ratio": (latest.like_rate if latest else 0) * 100,
                "comments_ratio": (latest.comment_rate if latest else 0) * 100,
                "shares_ratio": (latest.share_rate if latest else 0) * 100,
                "engagement_rate": sum([
                    (latest.like_rate if latest else 0),
                    (latest.comment_rate if latest else 0),
                    (latest.share_rate if latest else 0)
                ]) * 100 if latest else 0,
                "title_length": len(video.title),
                "description_length": len(video.description or ""),
                "tags_count": len(video.tags or []),
                "seo_score": self._calculate_seo_score(video)
            }
            
            # Analyze title effectiveness
            await self._learn_title_pattern(user_id, video.title, performance_data)
            
            # Analyze thumbnail
            if video.thumbnail_path:
                await self._learn_thumbnail_pattern(user_id, video, performance_data)
            
            # Learn script effectiveness
            await self._learn_script_pattern(user_id, video.script, performance_data)
            
            # Update overall learning state
            await self._update_learning_state(user_id, performance_data)
            
            logger.info(f"Performance analysis complete for video: {video_id}")
            
        except Exception as e:
            logger.error(f"Error analyzing video performance: {str(e)}")
    
    async def _learn_title_pattern(self, user_id: str, title: str,
                                   performance_data: Dict):
        """Learn what title patterns work best"""
        
        try:
            prompt = f"""
            Analyze title effectiveness:
            
            Title: "{title}"
            Performance:
            - Views: {performance_data['total_views']}
            - CTR: {performance_data['ctr']:.2f}%
            - Retention: {performance_data['retention']:.1f}%
            - Engagement: {performance_data['engagement_rate']:.1f}%
            
            Provide:
            {{
                "title_style": "curiosity_gap|numbers|emotional|action",
                "effectiveness_score": 0-100,
                "elements_present": ["..."],
                "why_effective": "...",
                "patterns_to_replicate": ["..."]
            }}
            """
            
            response = await self.openai_client.chat.completions.create(
                model=MAIN_LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            analysis = json.loads(response.choices[0].message.content)
            
            # Store learning
            performance_learning = PerformanceLearning(
                user_id=user_id,
                content_element="title_style",
                element_value=analysis.get("title_style", ""),
                total_attempts=1,
                successful_attempts=1 if performance_data["ctr"] > 5.0 else 0,
                avg_ctr=performance_data["ctr"],
                avg_retention=performance_data["retention"],
                avg_engagement=performance_data["engagement_rate"],
                effectiveness_score=analysis.get("effectiveness_score", 50)
            )
            
            db.session.add(performance_learning)
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Error learning title pattern: {str(e)}")
    
    async def _learn_thumbnail_pattern(self, user_id: str, video,
                                       performance_data: Dict):
        """Learn what thumbnail designs work best"""
        
        try:
            # Use vision to analyze thumbnail
            if video.thumbnail_path:
                prompt = f"""
                Analyze thumbnail effectiveness:
                
                Video Performance:
                - CTR: {performance_data['ctr']:.2f}%
                - Views: {performance_data['total_views']}
                
                What thumbnail design elements made this successful?
                Analyze style, colors, text, composition.
                
                Return JSON with:
                - design_style
                - emotional_appeal
                - effectiveness_score
                - elements_to_replicate
                """
                
                # This would use vision API to analyze the thumbnail image
                # Simplified for now
                
        except Exception as e:
            logger.error(f"Error learning thumbnail pattern: {str(e)}")
    
    async def _learn_script_pattern(self, user_id: str, script: str,
                                    performance_data: Dict):
        """Learn what script elements drive retention"""
        
        try:
            # Analyze script structure and retention
            script_preview = script[:500]
            
            prompt = f"""
            Analyze script effectiveness for retention:
            
            Script (first part): "{script_preview}"
            
            Performance:
            - Retention: {performance_data['retention']:.1f}%
            - Engagement: {performance_data['engagement_rate']:.1f}%
            - CTR: {performance_data['ctr']:.2f}%
            
            Identify:
            - Hook quality (0-100)
            - Pacing effectiveness
            - Retention strategies used
            - Emotional triggers
            - Story structure
            - CTA effectiveness
            
            Return JSON:
            {{
                "hook_score": 0-100,
                "pacing_style": "fast|slow|rhythmic",
                "retention_techniques": ["..."],
                "emotional_triggers": ["..."],
                "effectiveness_score": 0-100,
                "improvements": ["..."]
            }}
            """
            
            response = await self.openai_client.chat.completions.create(
                model=MAIN_LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            analysis = json.loads(response.choices[0].message.content)
            
            # Store learning
            pacing_style = analysis.get("pacing_style", "fast")
            performance_learning = PerformanceLearning(
                user_id=user_id,
                content_element="script_pacing",
                element_value=pacing_style,
                total_attempts=1,
                successful_attempts=1 if performance_data["retention"] > 50 else 0,
                avg_ctr=performance_data["ctr"],
                avg_retention=performance_data["retention"],
                avg_engagement=performance_data["engagement_rate"],
                effectiveness_score=analysis.get("effectiveness_score", 50)
            )
            
        except Exception as e:
            logger.error(f"Error learning script pattern: {str(e)}")
    
    async def _update_learning_state(self, user_id: str,
                                     performance_data: Dict):
        """Update overall learning state"""
        
        try:
            # Get or create learning state
            learning_state = db.get_learning_state(user_id)
            
            # Update performance averages
            total_videos = learning_state.total_videos_analyzed + 1
            
            # Update average performance
            new_avg = (
                (learning_state.average_performance_score * (total_videos - 1) +
                 performance_data["engagement_rate"]) / total_videos
            )
            
            updates = {
                "total_videos_analyzed": total_videos,
                "average_performance_score": new_avg,
                "last_updated_at": datetime.utcnow()
            }
            
            db.update_learning_state(user_id, **updates)
            
        except Exception as e:
            logger.error(f"Error updating learning state: {str(e)}")
    
    def _calculate_seo_score(self, video) -> float:
        """Calculate SEO optimization score"""
        
        score = 0
        max_score = 100
        
        # Title optimization (25 points)
        if 40 <= len(video.title) <= 60:
            score += 25
        elif len(video.title) > 30:
            score += 15
        
        # Description optimization (25 points)
        if video.description and len(video.description) > 200:
            score += 25
        elif video.description and len(video.description) > 100:
            score += 15
        
        # Tags (25 points)
        if video.tags and len(video.tags) >= 5:
            score += 25
        elif video.tags and len(video.tags) >= 3:
            score += 15
        
        # Hashtags (25 points)
        if video.hashtags and len(video.hashtags) >= 3:
            score += 25
        elif video.hashtags and len(video.hashtags) >= 1:
            score += 15
        
        return min(max_score, score)
    
    async def get_personalized_recommendations(self, user_id: str) -> Dict[str, List[str]]:
        """
        Get AI recommendations based on learning
        """
        
        try:
            # Get learning state
            learning_state = db.get_learning_state(user_id)
            
            # Get user's successful patterns
            prompt = f"""
            Based on this user's content performance history:
            - Average performance score: {learning_state.average_performance_score:.1f}
            - Videos analyzed: {learning_state.total_videos_analyzed}
            - High performing title patterns: {json.dumps(learning_state.high_performing_title_patterns[:3])}
            - Effective pacing styles: {json.dumps(learning_state.effective_pacing_styles)}
            - Niche preferences: {json.dumps(learning_state.niche_preferences)}
            
            Provide specific recommendations for:
            1. Next video topics
            2. Title optimization
            3. Script style
            4. Thumbnail approach
            5. Upload timing
            6. Video length
            7. Engagement strategies
            
            Return JSON with actionable recommendations.
            """
            
            response = await self.openai_client.chat.completions.create(
                model=MAIN_LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            recommendations = json.loads(response.choices[0].message.content)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting recommendations: {str(e)}")
            return {}
    
    async def optimize_for_next_video(self, user_id: str,
                                      topic: str) -> Dict:
        """
        AI-optimized configuration for next video based on learnings
        """
        
        try:
            learning_state = db.get_learning_state(user_id)
            
            prompt = f"""
            Create optimized video generation config based on learning:
            
            User's Best Performing Content:
            - Title patterns: {learning_state.high_performing_title_patterns}
            - Pacing styles: {learning_state.effective_pacing_styles}
            - Optimal duration: {learning_state.optimal_duration_by_niche}
            - Best upload time: {learning_state.optimal_upload_time}
            - Average performance: {learning_state.average_performance_score:.1f}
            
            New Topic: {topic}
            
            Recommend optimized config:
            {{
                "title_style": "...",
                "script_pacing": "...",
                "video_duration": 0,
                "thumbnail_style": "...",
                "upload_time": "...",
                "hook_type": "...",
                "retention_strategies": ["..."],
                "predicted_ctr": 0.0,
                "predicted_engagement": 0.0,
                "reasoning": "..."
            }}
            """
            
            response = await self.openai_client.chat.completions.create(
                model=MAIN_LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                response_format={"type": "json_object"}
            )
            
            config = json.loads(response.choices[0].message.content)
            
            return config
            
        except Exception as e:
            logger.error(f"Error optimizing for next video: {str(e)}")
            return {}


# Global instance
learning_loop = AILearningLoop()
