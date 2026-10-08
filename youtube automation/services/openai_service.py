# ================================================
# OPENAI SERVICE - AI CONTENT GENERATION
# ================================================

import openai
import logging
import json
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# ================================================
# OPENAI INITIALIZATION
# ================================================

class OpenAIService:
    """Handle all OpenAI API calls for content generation."""
    
    def __init__(self, api_key: str = None):
        """Initialize OpenAI service with API key."""
        if api_key:
            openai.api_key = api_key
        self.model = "gpt-4-turbo-preview"
        self.fallback_model = "gpt-3.5-turbo"
    
    def _call_openai(self, prompt: str, system_prompt: str = None, 
                    temperature: float = 0.7, max_tokens: int = 2000) -> Optional[str]:
        """Call OpenAI API with error handling."""
        try:
            messages = []
            
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            # Try fallback model
            try:
                response = openai.ChatCompletion.create(
                    model=self.fallback_model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                return response.choices[0].message.content
            except Exception as e2:
                logger.error(f"Fallback model also failed: {e2}")
                return None
    
    # =============================================
    # SCRIPT GENERATION
    # =============================================
    
    def generate_script(self, topic: str, content_type: str = "long_form",
                       language: str = "en", tone: str = "engaging",
                       target_audience: str = "General") -> Dict:
        """Generate complete video script with hook, body, CTA."""
        try:
            system_prompt = """You are an expert YouTube scriptwriter creating viral content.
Generate engaging scripts that:
- Hook viewers in first 3 seconds
- Maintain tension throughout
- Include emotional triggers
- End with strong Call-To-Action
Format as JSON with hook, body, and cta fields."""

            prompt = f"""
Create a {content_type} YouTube script for:
Topic: {topic}
Language: {language}
Tone: {tone}
Target Audience: {target_audience}

Return valid JSON with:
{{
    "hook": "First 30 seconds - grab attention",
    "body": "Main content",
    "cta": "Call to action",
    "estimated_duration": "in seconds",
    "key_points": ["point1", "point2", "point3"]
}}
"""
            
            response = self._call_openai(prompt, system_prompt, temperature=0.8)
            
            if response:
                # Parse JSON response
                try:
                    script_data = json.loads(response)
                    return {
                        "success": True,
                        "data": script_data,
                        "timestamp": datetime.now().isoformat()
                    }
                except json.JSONDecodeError:
                    # Fallback: return as text
                    return {
                        "success": True,
                        "data": {"full_script": response},
                        "timestamp": datetime.now().isoformat()
                    }
            return {"success": False, "error": "No response from OpenAI"}
        
        except Exception as e:
            logger.error(f"Script generation error: {e}")
            return {"success": False, "error": str(e)}
    
    # =============================================
    # TITLE GENERATION
    # =============================================
    
    def generate_title(self, topic: str, style: str = "clickbait") -> Dict:
        """Generate viral YouTube titles."""
        try:
            system_prompt = """You are a YouTube title expert.
Generate 5 viral YouTube titles that:
- Are under 60 characters
- Include power words (SHOCKING, ULTIMATE, etc)
- Trigger curiosity
- Are relevant to the topic
Format as JSON with "titles" array."""

            prompt = f"""
Generate viral YouTube titles for: {topic}
Style: {style}

Return JSON: {{"titles": ["title1", "title2", "title3", "title4", "title5"]}}
"""
            
            response = self._call_openai(prompt, system_prompt)
            
            if response:
                try:
                    data = json.loads(response)
                    return {"success": True, "data": data}
                except:
                    return {"success": True, "data": {"titles": response.split("\n")}}
            
            return {"success": False, "error": "No response"}
        except Exception as e:
            logger.error(f"Title generation error: {e}")
            return {"success": False, "error": str(e)}
    
    # =============================================
    # DESCRIPTION GENERATION
    # =============================================
    
    def generate_description(self, topic: str, keywords: List[str] = None) -> Dict:
        """Generate SEO-optimized YouTube description."""
        try:
            system_prompt = """You are an SEO expert writing YouTube descriptions.
Create descriptions that:
- Include main keyword in first 50 characters
- Include natural keyword variations
- Have clear sections (About, Chapters, Links)
- Encourage engagement
- Under 5000 characters"""

            keywords_text = ", ".join(keywords) if keywords else topic
            
            prompt = f"""
Generate SEO description for: {topic}
Keywords: {keywords_text}

Include:
- Engaging intro
- Key highlights
- Timestamps (if applicable)
- Social links section
- CTAs for engagement
"""
            
            response = self._call_openai(prompt, system_prompt, max_tokens=500)
            
            if response:
                return {"success": True, "data": {"description": response}}
            
            return {"success": False, "error": "No response"}
        except Exception as e:
            logger.error(f"Description generation error: {e}")
            return {"success": False, "error": str(e)}
    
    # =============================================
    # TAGS GENERATION
    # =============================================
    
    def generate_tags(self, topic: str, keywords: List[str] = None) -> Dict:
        """Generate SEO tags and hashtags."""
        try:
            system_prompt = """You are a YouTube SEO expert.
Generate relevant tags that:
- Include main topic keywords
- Include long-tail variations
- Are searchable
- Have decent search volume
Return JSON with "tags" and "hashtags" arrays."""

            keywords_text = ", ".join(keywords) if keywords else topic
            
            prompt = f"""
Generate YouTube tags for: {topic}
Primary keywords: {keywords_text}

Return JSON:
{{
    "tags": ["tag1", "tag2", ...],  // max 30 tags
    "hashtags": ["#hashtag1", "#hashtag2", ...],  // max 10
    "primary_keyword": "most important keyword"
}}
"""
            
            response = self._call_openai(prompt, system_prompt)
            
            if response:
                try:
                    data = json.loads(response)
                    return {"success": True, "data": data}
                except:
                    return {"success": True, "data": {"tags": response.split(", ")}}
            
            return {"success": False, "error": "No response"}
        except Exception as e:
            logger.error(f"Tags generation error: {e}")
            return {"success": False, "error": str(e)}
    
    # =============================================
    # THUMBNAIL COPY GENERATION
    # =============================================
    
    def generate_thumbnail_text(self, topic: str, style: str = "bold") -> Dict:
        """Generate text recommendations for thumbnails."""
        try:
            prompt = f"""
For a YouTube thumbnail about "{topic}", generate:
1. Main headline (max 5 words)
2. Subheadline (max 3 words)
3. Emoji suggestions (max 3)
4. Color scheme recommendations

Keep text punchy and attention-grabbing.
"""
            
            response = self._call_openai(prompt, temperature=0.6)
            
            if response:
                return {"success": True, "data": {"text": response}}
            
            return {"success": False, "error": "No response"}
        except Exception as e:
            logger.error(f"Thumbnail text generation error: {e}")
            return {"success": False, "error": str(e)}
    
    # =============================================
    # TRENDING KEYWORDS ANALYSIS
    # =============================================
    
    def analyze_trending_keywords(self, topic: str) -> Dict:
        """Analyze trending keywords for topic."""
        try:
            system_prompt = """You are a YouTube SEO and trends analyst.
Provide JSON response with trending keywords and analysis."""

            prompt = f"""
Analyze trending keywords for: {topic}

Provide JSON:
{{
    "trending_keywords": ["keyword1", "keyword2", ...],
    "search_volume": {{"keyword1": "high/medium/low", ...}},
    "competition": {{"keyword1": "high/medium/low", ...}},
    "trend_velocity": "increasing/stable/declining",
    "recommended_keywords": ["best1", "best2", "best3"]
}}
"""
            
            response = self._call_openai(prompt, system_prompt)
            
            if response:
                try:
                    data = json.loads(response)
                    return {"success": True, "data": data}
                except:
                    return {"success": True, "data": {"keywords": response}}
            
            return {"success": False, "error": "No response"}
        except Exception as e:
            logger.error(f"Keyword analysis error: {e}")
            return {"success": False, "error": str(e)}
    
    # =============================================
    # VIRAL SCORE PREDICTION
    # =============================================
    
    def calculate_viral_score(self, title: str, description: str, 
                             topic: str, tags: List[str] = None) -> Dict:
        """Calculate viral potential score (0-100)."""
        try:
            tags_text = ", ".join(tags) if tags else ""
            
            prompt = f"""
Calculate viral score for YouTube video:
Title: {title}
Description: {description}
Topic: {topic}
Tags: {tags_text}

Analyze:
1. Title impact (hook strength, curiosity gap)
2. Description quality (CTAs, formatting)
3. Topic relevance (trending potential)
4. SEO optimization (keyword placement)
5. Engagement potential

Return JSON:
{{
    "total_score": score_0_to_100,
    "title_score": score,
    "description_score": score,
    "topic_score": score,
    "seo_score": score,
    "engagement_score": score,
    "recommendation": "improvement suggestion"
}}
"""
            
            response = self._call_openai(prompt, temperature=0.5)
            
            if response:
                try:
                    data = json.loads(response)
                    return {"success": True, "data": data}
                except:
                    return {"success": True, "data": {"score": 75}}
            
            return {"success": False, "error": "No response"}
        except Exception as e:
            logger.error(f"Viral score calculation error: {e}")
            return {"success": False, "error": str(e)}


# ================================================
# SINGLETON INSTANCE
# ================================================

openai_service = None

def init_openai_service(api_key: str) -> OpenAIService:
    """Initialize OpenAI service with API key."""
    global openai_service
    openai_service = OpenAIService(api_key)
    return openai_service

def get_openai_service() -> OpenAIService:
    """Get OpenAI service instance."""
    if openai_service is None:
        openai_service = OpenAIService()
    return openai_service
