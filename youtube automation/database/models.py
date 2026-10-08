"""
Production-Grade SQLAlchemy ORM Models
Comprehensive data models for AI Media Operating System
"""

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text, 
    JSON, ForeignKey, Enum, Numeric, Table, UniqueConstraint,
    Index, create_engine, func
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session
from datetime import datetime
from enum import Enum as PyEnum
import uuid

Base = declarative_base()


class VideoStatusEnum(str, PyEnum):
    DRAFT = "draft"
    GENERATING = "generating"
    GENERATED = "generated"
    RENDERING = "rendering"
    RENDERED = "rendered"
    UPLOADING = "uploading"
    UPLOADED = "uploaded"
    PUBLISHED = "published"
    FAILED = "failed"


class TaskStatusEnum(str, PyEnum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRY = "retry"


class ContentTypeEnum(str, PyEnum):
    FULL_VIDEO = "full_video"
    SHORTS = "shorts"
    VIRAL_CLIP = "viral_clip"
    DOCUMENTARY = "documentary"
    MOTIVATIONAL = "motivational"
    EDUCATIONAL = "educational"
    FINANCE = "finance"
    TECH = "tech"


# ===========================
# MULTI-CHANNEL MODELS
# ===========================

class YouTubeChannel(Base):
    """Manage multiple YouTube channels"""
    __tablename__ = "youtube_channels"
    __table_args__ = (
        Index('idx_channel_user_workspace', 'user_id', 'workspace_id'),
    )
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(255), nullable=False)
    workspace_id = Column(String(255), nullable=False)
    channel_name = Column(String(255), nullable=False)
    channel_id = Column(String(255), unique=True)
    email = Column(String(255))
    subscriber_count = Column(Integer, default=0)
    total_views = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    is_primary = Column(Boolean, default=False)
    credentials_encrypted = Column(Text)  # Encrypted OAuth token
    last_sync = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    videos = relationship("Video", back_populates="channel")
    analytics = relationship("ChannelAnalytics", back_populates="channel")


# ===========================
# VIDEO & CONTENT MODELS
# ===========================

class Video(Base):
    """Core video model for all generated content"""
    __tablename__ = "videos"
    __table_args__ = (
        Index('idx_video_channel_status', 'channel_id', 'status'),
        Index('idx_video_created_at', 'created_at'),
        Index('idx_video_user', 'user_id'),
    )
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(255), nullable=False)
    channel_id = Column(String(36), ForeignKey('youtube_channels.id'))
    
    # Content Info
    content_type = Column(Enum(ContentTypeEnum), default=ContentTypeEnum.FULL_VIDEO)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    script = Column(Text, nullable=False)
    
    # Generation Status
    status = Column(Enum(VideoStatusEnum), default=VideoStatusEnum.DRAFT)
    progress_percent = Column(Integer, default=0)
    
    # File Paths
    video_path = Column(String(1024))
    thumbnail_path = Column(String(1024))
    audio_path = Column(String(1024))
    
    # YouTube Meta
    youtube_video_id = Column(String(255), unique=True)
    youtube_url = Column(String(512))
    privacy_status = Column(String(50), default="public")  # public, private, unlisted
    publish_at = Column(DateTime)
    
    # SEO Data
    seo_title = Column(String(255))
    seo_description = Column(Text)
    tags = Column(JSON, default=list)
    hashtags = Column(JSON, default=list)
    
    # Generation Config
    language = Column(String(50), default="english")
    voice_provider = Column(String(100))  # elevenlabs, openai, edge
    voice_gender = Column(String(20))  # male, female
    emotion_tone = Column(String(100))  # happy, serious, energetic, etc
    
    # AI Metrics
    viral_score = Column(Float, default=0.0)  # 0-100
    engagement_prediction = Column(Float, default=0.0)  # predicted engagement rate
    ctr_prediction = Column(Float, default=0.0)  # predicted click-through rate
    retention_prediction = Column(Float, default=0.0)  # predicted average view %
    
    # Duration & Performance
    duration_seconds = Column(Integer)
    actual_views = Column(Integer, default=0)
    actual_likes = Column(Integer, default=0)
    actual_comments = Column(Integer, default=0)
    actual_ctr = Column(Float)
    actual_retention = Column(Float)
    
    # Flags
    is_shorts = Column(Boolean, default=False)
    is_auto_generated = Column(Boolean, default=True)
    is_published = Column(Boolean, default=False)
    requires_manual_review = Column(Boolean, default=False)
    
    # Error Tracking
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    channel = relationship("YouTubeChannel", back_populates="videos")
    analytics = relationship("VideoAnalytics", back_populates="video")
    scenes = relationship("VideoScene", back_populates="video", cascade="all, delete-orphan")
    thumbnails = relationship("ThumbnailVariation", back_populates="video", cascade="all, delete-orphan")


class VideoScene(Base):
    """Individual scenes within a video for cinematic generation"""
    __tablename__ = "video_scenes"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    video_id = Column(String(36), ForeignKey('videos.id'), nullable=False)
    
    scene_number = Column(Integer, nullable=False)
    scene_type = Column(String(100))  # title, narrative, visual, transition, etc
    text = Column(Text)
    duration_seconds = Column(Float)
    
    # Visual Elements
    background_image_path = Column(String(1024))
    generated_image_path = Column(String(1024))
    visual_prompt = Column(Text)
    
    # Cinematography
    camera_movement = Column(String(100))  # pan, zoom, dolly, static, etc
    transition_type = Column(String(100))  # fade, cut, wipe, dissolve, etc
    transition_duration = Column(Float, default=0.5)
    
    # Audio
    narration_text = Column(Text)
    audio_path = Column(String(1024))
    audio_duration = Column(Float)
    
    # Visual Effects
    effects = Column(JSON, default=list)  # [{"type": "blur", "intensity": 0.5}, ...]
    overlay_text = Column(String(512))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    video = relationship("Video", back_populates="scenes")


# ===========================
# THUMBNAIL MODELS
# ===========================

class ThumbnailVariation(Base):
    """Multiple AI-generated thumbnail variations for A/B testing"""
    __tablename__ = "thumbnail_variations"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    video_id = Column(String(36), ForeignKey('videos.id'), nullable=False)
    
    variation_number = Column(Integer)
    image_path = Column(String(1024), nullable=False)
    prompt = Column(Text)
    
    # A/B Testing Results
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    ctr = Column(Float)
    
    # Design Elements
    design_style = Column(String(100))  # mrbeast_style, minimalist, dramatic, etc
    emotional_appeal = Column(String(100))  # curiosity, fear, joy, excitement
    color_scheme = Column(JSON)
    text_overlay = Column(String(255))
    face_detected = Column(Boolean)
    contrast_score = Column(Float)
    
    is_selected = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    video = relationship("Video", back_populates="thumbnails")


# ===========================
# TOPIC INTELLIGENCE MODELS
# ===========================

class Trend(Base):
    """Track trending topics and viral opportunities"""
    __tablename__ = "trends"
    __table_args__ = (
        Index('idx_trend_category_date', 'category', 'detected_at'),
    )
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    topic = Column(String(255), nullable=False)
    category = Column(String(100))
    keyword = Column(String(255), unique=True, nullable=False)
    
    # Viral Metrics
    search_volume = Column(Integer, default=0)
    growth_rate = Column(Float)  # percentage increase
    viral_score = Column(Float, default=0.0)  # 0-100
    
    # Market Analysis
    competition_level = Column(String(50))  # low, medium, high
    opportunity_score = Column(Float)  # scoring for content opportunity
    niche_rating = Column(Float)  # 0-100
    
    # Predictions
    predicted_retention = Column(Float)
    predicted_ctr = Column(Float)
    predicted_engagement = Column(Float)
    
    # Sources
    detected_on = Column(JSON, default=list)  # [twitter, tiktok, youtube, reddit, ...]
    source_data = Column(JSON)
    
    is_active = Column(Boolean, default=True)
    detected_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class CompetitorAnalysis(Base):
    """Track competitor channels and content strategies"""
    __tablename__ = "competitor_analysis"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(255), nullable=False)
    
    competitor_name = Column(String(255), nullable=False)
    competitor_channel_id = Column(String(255), unique=True)
    category = Column(String(100))
    
    # Performance Metrics
    subscriber_count = Column(Integer)
    total_views = Column(Integer)
    avg_ctr = Column(Float)
    avg_retention = Column(Float)
    upload_frequency = Column(String(100))  # daily, weekly, biweekly
    
    # Content Strategy
    dominant_topics = Column(JSON, default=list)
    avg_title_length = Column(Integer)
    avg_description_length = Column(Integer)
    common_tags = Column(JSON, default=list)
    thumbnail_style = Column(String(255))
    
    # Benchmarks
    performance_score = Column(Float)  # 0-100
    
    last_analyzed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ===========================
# ANALYTICS MODELS
# ===========================

class VideoAnalytics(Base):
    """Real-time and historical video performance data"""
    __tablename__ = "video_analytics"
    __table_args__ = (
        Index('idx_analytics_video_date', 'video_id', 'recorded_at'),
    )
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    video_id = Column(String(36), ForeignKey('videos.id'), nullable=False)
    
    # Viewership
    views = Column(Integer, default=0)
    unique_viewers = Column(Integer, default=0)
    
    # Engagement
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    
    # Performance Ratios
    ctr = Column(Float)
    like_rate = Column(Float)
    comment_rate = Column(Float)
    share_rate = Column(Float)
    
    # Retention
    avg_view_duration = Column(Integer)  # seconds
    avg_view_percentage = Column(Float)  # 0-100
    
    # Traffic Sources
    traffic_sources = Column(JSON, default={})  # {youtube_search: 45, suggested_videos: 30, ...}
    
    recorded_at = Column(DateTime, default=datetime.utcnow)
    video = relationship("Video", back_populates="analytics")


class ChannelAnalytics(Base):
    """Channel-level aggregate analytics"""
    __tablename__ = "channel_analytics"
    __table_args__ = (
        Index('idx_channel_analytics_date', 'channel_id', 'recorded_at'),
    )
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    channel_id = Column(String(36), ForeignKey('youtube_channels.id'), nullable=False)
    
    total_views = Column(Integer, default=0)
    total_subscribers = Column(Integer, default=0)
    avg_ctr = Column(Float)
    avg_retention = Column(Float)
    
    new_subscribers = Column(Integer, default=0)
    total_watch_time_hours = Column(Integer, default=0)
    
    top_performing_video_id = Column(String(36))
    
    recorded_at = Column(DateTime, default=datetime.utcnow)
    channel = relationship("YouTubeChannel", back_populates="analytics")


# ===========================
# LEARNING & OPTIMIZATION MODELS
# ===========================

class ContentLearningState(Base):
    """AI learning state for content optimization"""
    __tablename__ = "content_learning_state"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(255), nullable=False, unique=True)
    
    # Title Optimization Knowledge
    high_performing_title_patterns = Column(JSON, default=list)
    high_ctr_title_keywords = Column(JSON, default=list)
    title_length_optimal_range = Column(JSON)  # {"min": 40, "max": 60}
    
    # Thumbnail Optimization Knowledge
    high_performing_thumbnail_styles = Column(JSON, default=list)
    high_ctr_thumbnail_elements = Column(JSON, default=list)
    emotional_appeal_effectiveness = Column(JSON, default={})
    
    # Script & Narration
    high_retention_hook_patterns = Column(JSON, default=list)
    effective_pacing_styles = Column(JSON, default=list)
    optimal_script_structure = Column(JSON)
    
    # Niche Knowledge
    niche_preferences = Column(JSON, default={})  # {niche: {optimal_duration, themes, etc}}
    audience_preferences = Column(JSON, default={})
    
    # Video Performance Patterns
    optimal_duration_by_niche = Column(JSON, default={})
    optimal_upload_time = Column(String(100))
    optimal_upload_frequency = Column(String(100))
    
    # Overall Performance Index
    total_videos_analyzed = Column(Integer, default=0)
    average_performance_score = Column(Float, default=0.0)
    
    last_updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)


class PerformanceLearning(Base):
    """Track what works and what doesn't"""
    __tablename__ = "performance_learning"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(255), nullable=False)
    
    content_element = Column(String(100))  # title_style, thumbnail_style, hook_type, etc
    element_value = Column(String(512))
    
    total_attempts = Column(Integer, default=0)
    successful_attempts = Column(Integer, default=0)
    
    avg_ctr = Column(Float, default=0.0)
    avg_retention = Column(Float, default=0.0)
    avg_engagement = Column(Float, default=0.0)
    
    effectiveness_score = Column(Float, default=0.0)  # 0-100
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ===========================
# TASK MANAGEMENT MODELS
# ===========================

class Task(Base):
    """Background task tracking"""
    __tablename__ = "tasks"
    __table_args__ = (
        Index('idx_task_status_user', 'status', 'user_id'),
        Index('idx_task_created', 'created_at'),
    )
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    celery_task_id = Column(String(255), unique=True)
    user_id = Column(String(255), nullable=False)
    
    task_type = Column(String(100))  # video_generation, upload, thumbnail_gen, etc
    status = Column(Enum(TaskStatusEnum), default=TaskStatusEnum.QUEUED)
    progress_percent = Column(Integer, default=0)
    
    input_data = Column(JSON)
    result_data = Column(JSON)
    error_message = Column(Text)
    
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PublishingQueue(Base):
    """Schedule and queue videos for publishing"""
    __tablename__ = "publishing_queue"
    __table_args__ = (
        Index('idx_queue_channel_status', 'channel_id', 'status'),
        Index('idx_queue_scheduled', 'scheduled_publish_time'),
    )
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    video_id = Column(String(36), ForeignKey('videos.id'))
    channel_id = Column(String(36), ForeignKey('youtube_channels.id'))
    
    status = Column(String(50), default="pending")  # pending, scheduled, publishing, published, failed
    scheduled_publish_time = Column(DateTime)
    actual_publish_time = Column(DateTime)
    
    publish_order = Column(Integer)
    retry_count = Column(Integer, default=0)
    error_message = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ===========================
# USER & SETTINGS MODELS
# ===========================

class User(Base):
    """User accounts and API key management"""
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255))
    
    # API Keys (encrypted)
    openai_api_key_encrypted = Column(Text)
    elevenlabs_api_key_encrypted = Column(Text)
    
    # Preferences
    preferred_language = Column(String(50), default="english")
    timezone = Column(String(100), default="UTC")
    
    # Subscription
    plan_type = Column(String(50), default="free")  # free, pro, enterprise
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class UserPreferences(Base):
    """User AI generation preferences and toggles"""
    __tablename__ = "user_preferences"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey('users.id'), unique=True)
    
    # Feature Toggles
    autonomous_mode_enabled = Column(Boolean, default=True)
    shorts_generation_enabled = Column(Boolean, default=True)
    auto_thumbnail_generation = Column(Boolean, default=True)
    auto_upload_enabled = Column(Boolean, default=False)
    ai_script_generation = Column(Boolean, default=True)
    
    # Generation Preferences
    default_voice_provider = Column(String(100), default="elevenlabs")
    default_voice_gender = Column(String(20), default="male")
    default_emotion_tone = Column(String(100), default="energetic")
    
    # Safety & Compliance
    require_manual_review = Column(Boolean, default=False)
    avoid_controversial_topics = Column(Boolean, default=True)
    family_friendly_content = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ===========================
# SEARCH & CACHING MODELS
# ===========================

class SearchKeywordCache(Base):
    """Cache for YouTube search volume and trends"""
    __tablename__ = "search_keyword_cache"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    keyword = Column(String(255), unique=True, nullable=False)
    
    search_volume = Column(Integer)
    cpc = Column(Float)
    competition_level = Column(String(50))
    
    trend_velocity = Column(Float)  # How fast is it trending up/down
    
    last_updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = Column(DateTime)


# ===========================
# AUDIT & LOGGING MODELS
# ===========================

class AuditLog(Base):
    """Track all important system actions for compliance"""
    __tablename__ = "audit_logs"
    __table_args__ = (
        Index('idx_audit_user_action', 'user_id', 'action'),
        Index('idx_audit_timestamp', 'created_at'),
    )
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(255))
    action = Column(String(100))
    resource_type = Column(String(100))
    resource_id = Column(String(36))
    
    old_value = Column(JSON)
    new_value = Column(JSON)
    details = Column(Text)
    
    ip_address = Column(String(45))
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
