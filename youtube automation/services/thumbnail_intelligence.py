"""
Advanced Thumbnail Intelligence System
Generates MrBeast-style viral thumbnails with psychological optimization
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import openai
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import os
from config.settings import OPENAI_API_KEY, THUMBNAILS_DIR, MAIN_LLM_MODEL, VISION_MODEL
from utils.logger import logger


class ThumbnailStyle(str, Enum):
    MRBEAST = "mrbeast"  # High contrast, bold text, faces
    MINIMALIST = "minimalist"  # Clean, simple, elegant
    DRAMATIC = "dramatic"  # Dark, intense, mysterious
    BRIGHT = "bright"  # Colorful, vibrant, energetic
    EMOTIONAL = "emotional"  # Facial expressions, emotional appeal
    INTRIGUING = "intriguing"  # Question marks, arrows, intrigue


class EmotionalAppeal(str, Enum):
    CURIOSITY = "curiosity"
    FEAR = "fear"
    JOY = "joy"
    ANGER = "anger"
    SHOCK = "shock"
    EXCITEMENT = "excitement"
    SKEPTICISM = "skepticism"


@dataclass
class ThumbnailDesign:
    """Thumbnail design specification"""
    style: ThumbnailStyle
    background_color: Tuple[int, int, int]
    text: str
    text_color: Tuple[int, int, int]
    emotional_appeal: EmotionalAppeal
    face_position: Optional[str] = "center-right"
    text_position: str = "top"
    arrows_or_elements: List[str] = None
    contrast_level: float = 0.8  # 0-1


@dataclass
class ThumbnailAnalysis:
    """Analysis of thumbnail effectiveness"""
    design: ThumbnailDesign
    predicted_ctr: float
    predicted_engagement: float
    contrast_score: float  # 0-100
    clarity_score: float  # 0-100
    emotional_impact: float  # 0-100
    psychological_triggers: List[str]
    recommendations: List[str]


class ThumbnailIntelligence:
    """
    Production-grade thumbnail generation and optimization
    
    Features:
    - MrBeast-style composition
    - Emotional psychology optimization
    - Contrast and clarity optimization
    - Face detection and highlighting
    - Text optimization for readability
    - A/B testing variations
    - CTR prediction
    - AI-powered design suggestions
    """
    
    def __init__(self):
        self.openai_client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)
        os.makedirs(THUMBNAILS_DIR, exist_ok=True)
        
        # Design palettes
        self.color_palettes = {
            ThumbnailStyle.MRBEAST: {
                "primary": (255, 0, 0),
                "secondary": (255, 255, 255),
                "accent": (0, 0, 0)
            },
            ThumbnailStyle.BRIGHT: {
                "primary": (255, 150, 0),
                "secondary": (0, 200, 255),
                "accent": (0, 0, 0)
            },
            ThumbnailStyle.DRAMATIC: {
                "primary": (50, 50, 50),
                "secondary": (200, 200, 200),
                "accent": (255, 0, 0)
            }
        }
    
    async def generate_viral_thumbnail(
        self,
        video_title: str,
        video_topic: str,
        style: ThumbnailStyle = ThumbnailStyle.MRBEAST,
        emotion: EmotionalAppeal = EmotionalAppeal.CURIOSITY,
        face_image: Optional[str] = None,
        background_image: Optional[str] = None,
        output_path: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Generate viral-optimized thumbnail
        """
        
        try:
            logger.info(f"Generating {style.value} thumbnail for: {video_title}")
            
            # Step 1: Generate design spec
            design = await self._generate_design_spec(
                video_title, video_topic, style, emotion
            )
            
            # Step 2: Create thumbnail image
            if not output_path:
                output_path = os.path.join(
                    THUMBNAILS_DIR,
                    f"thumbnail_{int(__import__('time').time())}.png"
                )
            
            thumbnail_path = self._create_thumbnail_image(
                design=design,
                face_image=face_image,
                background_image=background_image,
                output_path=output_path
            )
            
            # Step 3: Analyze and predict CTR
            analysis = await self._analyze_thumbnail(thumbnail_path, video_title)
            
            return {
                "thumbnail_path": thumbnail_path,
                "predicted_ctr": str(analysis.predicted_ctr),
                "predicted_engagement": str(analysis.predicted_engagement),
                "design_style": design.style.value,
                "emotional_appeal": design.emotional_appeal.value,
                "recommendations": analysis.recommendations
            }
            
        except Exception as e:
            logger.error(f"Error generating thumbnail: {str(e)}")
            raise
    
    async def _generate_design_spec(self, title: str, topic: str,
                                    style: ThumbnailStyle,
                                    emotion: EmotionalAppeal) -> ThumbnailDesign:
        """Use AI to generate optimal thumbnail design"""
        
        prompt = f"""
        Design optimal YouTube thumbnail for viral CTR.
        
        Video Title: {title}
        Topic: {topic}
        Style: {style.value}
        Emotional Appeal: {emotion.value}
        
        Requirements:
        - Mobile-optimized (readable on small screens)
        - High contrast
        - Emotional psychology
        - Psychology-based text
        - Face positioning for attention
        
        Provide design as JSON:
        {{
            "background_color": [R, G, B],
            "text": "main text (max 3 words)",
            "text_color": [R, G, B],
            "text_size": "large",
            "text_position": "top|center|bottom",
            "face_position": "center-right|left|top-left",
            "emotional_appeal": "{emotion.value}",
            "elements": ["arrow", "circle", "burst"],
            "contrast_approach": "high|medium",
            "why_works": "explanation of why this works"
        }}
        """
        
        response = await self.openai_client.chat.completions.create(
            model=MAIN_LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            response_format={"type": "json_object"}
        )
        
        design_data = json.loads(response.choices[0].message.content)
        
        return ThumbnailDesign(
            style=style,
            background_color=tuple(design_data["background_color"]),
            text=design_data["text"],
            text_color=tuple(design_data["text_color"]),
            emotional_appeal=emotion,
            face_position=design_data.get("face_position"),
            text_position=design_data.get("text_position", "top"),
            arrows_or_elements=design_data.get("elements", []),
            contrast_level=0.9 if design_data.get("contrast_approach") == "high" else 0.7
        )
    
    def _create_thumbnail_image(
        self,
        design: ThumbnailDesign,
        face_image: Optional[str],
        background_image: Optional[str],
        output_path: str
    ) -> str:
        """
        Create actual thumbnail image with PIL
        Dimensions: 1280x720
        """
        
        # Create base image
        img = Image.new('RGB', (1280, 720), design.background_color)
        
        # Add background image if provided
        if background_image and os.path.exists(background_image):
            try:
                bg = Image.open(background_image).resize((1280, 720))
                img.paste(bg, (0, 0))
            except Exception as e:
                logger.warning(f"Could not add background: {str(e)}")
        
        # Add face image if provided
        if face_image and os.path.exists(face_image):
            try:
                face = Image.open(face_image).convert('RGB')
                face_size = int(720 * 0.6)
                face = face.resize((face_size, face_size))
                
                # Position based on design
                if design.face_position == "center-right":
                    x = 1280 - face_size - 20
                    y = (720 - face_size) // 2
                elif design.face_position == "left":
                    x, y = 20, (720 - face_size) // 2
                else:  # top-left
                    x, y = 20, 20
                
                img.paste(face, (x, y))
            except Exception as e:
                logger.warning(f"Could not add face image: {str(e)}")
        
        # Add high contrast border/shadow
        self._add_contrast_enhancement(img, design.contrast_level)
        
        # Add text
        self._add_text_overlay(img, design)
        
        # Add elements (arrows, circles, etc)
        if design.arrows_or_elements:
            self._add_elements(img, design.arrows_or_elements)
        
        # Save
        img.save(output_path, quality=95)
        logger.info(f"Thumbnail saved: {output_path}")
        
        return output_path
    
    def _add_contrast_enhancement(self, img: Image.Image, contrast_level: float):
        """Enhance contrast for viral thumbnails"""
        
        enhancer = ImageEnhance.Contrast(img)
        enhanced = enhancer.enhance(1.0 + (contrast_level * 0.5))
        
        # Apply sharpening
        sharpener = ImageEnhance.Sharpness(enhanced)
        final = sharpener.enhance(1.5)
        
        # Copy back to original
        img.paste(final)
    
    def _add_text_overlay(self, img: Image.Image, design: ThumbnailDesign):
        """Add optimized text to thumbnail"""
        
        draw = ImageDraw.Draw(img)
        
        try:
            # Use system font or default
            font_size = 140
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        # Break text into lines if needed
        text = design.text
        if len(text) > 20:
            words = text.split()
            lines = []
            current_line = ""
            for word in words:
                if len(current_line + word) <= 20:
                    current_line += word + " "
                else:
                    if current_line:
                        lines.append(current_line.strip())
                    current_line = word + " "
            if current_line:
                lines.append(current_line.strip())
            text = "\n".join(lines[:3])  # Max 3 lines
        
        # Position text
        if design.text_position == "top":
            y = 20
        elif design.text_position == "center":
            y = 250
        else:  # bottom
            y = 550
        
        # Add text with outline for readability
        outline_width = 5
        for adj_x in range(-outline_width, outline_width + 1):
            for adj_y in range(-outline_width, outline_width + 1):
                if adj_x != 0 or adj_y != 0:
                    draw.text(
                        (640 + adj_x, y + adj_y),
                        text,
                        font=font,
                        fill=(0, 0, 0),
                        anchor="mm",
                        align="center"
                    )
        
        # Draw main text
        draw.text(
            (640, y),
            text,
            font=font,
            fill=design.text_color,
            anchor="mm",
            align="center"
        )
    
    def _add_elements(self, img: Image.Image, elements: List[str]):
        """Add visual elements like arrows, circles, etc"""
        
        draw = ImageDraw.Draw(img)
        
        for element in elements[:3]:  # Max 3 elements
            if element == "arrow":
                # Draw arrow pointing to face/text
                draw.polygon(
                    [(1100, 200), (1150, 250), (1050, 250)],
                    fill=(255, 0, 0)
                )
            elif element == "circle":
                draw.ellipse(
                    [(950, 150), (1100, 300)],
                    outline=(255, 0, 0),
                    width=8
                )
            elif element == "burst":
                # Draw star burst
                for i in range(12):
                    angle = (360 / 12) * i
                    import math
                    x = 1000 + 80 * math.cos(math.radians(angle))
                    y = 200 + 80 * math.sin(math.radians(angle))
                    draw.line([(1000, 200), (x, y)], fill=(255, 255, 0), width=3)
    
    async def _analyze_thumbnail(self, thumbnail_path: str,
                                video_title: str) -> ThumbnailAnalysis:
        """Analyze thumbnail for CTR prediction"""
        
        try:
            # Load image and encode for vision API
            with open(thumbnail_path, 'rb') as f:
                image_data = f.read()
            
            import base64
            base64_image = base64.standard_b64encode(image_data).decode('utf-8')
            
            prompt = f"""
            Analyze this YouTube thumbnail for viral CTR potential.
            Video title: {video_title}
            
            Evaluate:
            1. Visual clarity and contrast (0-100)
            2. Text readability (0-100)
            3. Emotional impact (0-100)
            4. Face prominence and emotion
            5. Psychological triggers present
            6. Predicted CTR (0-20%)
            7. Predicted engagement rate (0-10%)
            8. Improvements needed
            
            Return JSON:
            {{
                "clarity_score": 85,
                "contrast_score": 90,
                "emotional_impact": 75,
                "predicted_ctr": 8.5,
                "predicted_engagement": 5.2,
                "psychological_triggers": ["curiosity", "facial_expression", "contrast"],
                "recommendations": ["...", "..."]
            }}
            """
            
            response = await self.openai_client.chat.completions.create(
                model=VISION_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            analysis_data = json.loads(response.choices[0].message.content)
            
            return ThumbnailAnalysis(
                design=None,
                predicted_ctr=analysis_data.get("predicted_ctr", 5.0),
                predicted_engagement=analysis_data.get("predicted_engagement", 3.0),
                contrast_score=analysis_data.get("contrast_score", 80),
                clarity_score=analysis_data.get("clarity_score", 80),
                emotional_impact=analysis_data.get("emotional_impact", 70),
                psychological_triggers=analysis_data.get("psychological_triggers", []),
                recommendations=analysis_data.get("recommendations", [])
            )
            
        except Exception as e:
            logger.error(f"Error analyzing thumbnail: {str(e)}")
            return ThumbnailAnalysis(
                design=None,
                predicted_ctr=5.0,
                predicted_engagement=3.0,
                contrast_score=75,
                clarity_score=75,
                emotional_impact=70,
                psychological_triggers=[],
                recommendations=["Ensure high contrast", "Use bold text", "Add emotional element"]
            )
    
    async def generate_multiple_variations(
        self,
        video_title: str,
        video_topic: str,
        num_variations: int = 3
    ) -> List[Dict[str, str]]:
        """
        Generate multiple thumbnail variations for A/B testing
        """
        
        variations = []
        styles = [
            ThumbnailStyle.MRBEAST,
            ThumbnailStyle.DRAMATIC,
            ThumbnailStyle.BRIGHT
        ]
        emotions = [
            EmotionalAppeal.CURIOSITY,
            EmotionalAppeal.SHOCK,
            EmotionalAppeal.EXCITEMENT
        ]
        
        for i in range(min(num_variations, len(styles))):
            try:
                variation = await self.generate_viral_thumbnail(
                    video_title=video_title,
                    video_topic=video_topic,
                    style=styles[i],
                    emotion=emotions[i]
                )
                variation["variation_number"] = i + 1
                variations.append(variation)
            except Exception as e:
                logger.error(f"Error generating variation {i+1}: {str(e)}")
                continue
        
        return variations


# Global instance
thumbnail_intelligence = ThumbnailIntelligence()
