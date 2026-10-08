# ================================================
# DATABASE MODELS - SQLALCHEMY DEFINITIONS
# ================================================

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, 
    Boolean, Float, JSON, ForeignKey, Table, 
    Enum, UniqueConstraint, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

# ================================================
# ENUMS
# ================================================

class VideoStatus(str, enum.Enum):
    DRAFT = "draft"
    GENERATED = "generated"
    UPLOADING = "uploading"
    PUBLISHED = "published"
    SCHEDULED = "scheduled"
    FAILED = "failed"

class ContentType(str, enum.Enum):
    LONG_FORM = "long_form"
    SHORTS = "shorts"
    HYBRID = "hybrid"

class PrivacyStatus(str, enum.Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    UNLISTED = "unlisted"

class Language(str, enum.Enum):
    ENGLISH = "en"
    URDU = "ur"
    HINDI = "hi"
    SPANISH = "es"
    FRENCH = "fr"

class VoiceGender(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"

# ================================================
# USERS & ACCOUNTS
# ================================================

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True)
    email = Column(String(255), unique=True, index=True)
    full_name = Column(String(255))
    password_hash = Column(String(500))
    is_active = Column(Boolean, default=True)
    is_premium = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    api_keys = relationship("APIKey", back_populates="user")
    youtube_channels = relationship("YouTubeChannel", back_populates="user")
    videos = relationship("Video", back_populates="user")
    scripts = relationship("Script", back_populates="user")
    thumbnails = relationship("Thumbnail", back_populates="user")
    analytics = relationship("Analytics", back_populates="user")
    settings = relationship("UserSettings", uselist=False, back_populates="user")


class APIKey(Base):
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    key_type = Column(String(50))  # openai, huggingface, elevenlabs, etc
    encrypted_key = Column(String(1000))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="api_keys")


class UserSettings(Base):
    __tablename__ = "user_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    theme = Column(String(50), default="dark")
    language = Column(Enum(Language), default=Language.ENGLISH)
    voice_gender = Column(Enum(VoiceGender), default=VoiceGender.MALE)
    default_privacy = Column(Enum(PrivacyStatus), default=PrivacyStatus.PUBLIC)
    auto_seo = Column(Boolean, default=True)
    auto_captions = Column(Boolean, default=True)
    auto_music = Column(Boolean, default=True)
    notification_email = Column(Boolean, default=True)
    settings_json = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="settings")


# ================================================
# YOUTUBE INTEGRATION
# ================================================

class YouTubeChannel(Base):
    __tablename__ = "youtube_channels"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    channel_id = Column(String(255), unique=True, index=True)
    channel_name = Column(String(255))
    channel_description = Column(Text)
    subscriber_count = Column(Integer, default=0)
    view_count = Column(Integer, default=0)
    profile_image_url = Column(String(500))
    access_token = Column(String(1000))
    refresh_token = Column(String(1000))
    is_primary = Column(Boolean, default=False)
    is_connected = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="youtube_channels")
    videos = relationship("Video", back_populates="youtube_channel")


# ================================================
# CONTENT & SCRIPTS
# ================================================

class Script(Base):
    __tablename__ = "scripts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String(255))
    topic = Column(String(255))
    content_type = Column(Enum(ContentType), default=ContentType.LONG_FORM)
    niche = Column(String(100))
    target_audience = Column(String(255))
    language = Column(Enum(Language), default=Language.ENGLISH)
    tone = Column(String(100))
    full_script = Column(Text)
    hook = Column(Text)
    body = Column(Text)
    cta = Column(Text)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="scripts")
    videos = relationship("Video", back_populates="script")


class Video(Base):
    __tablename__ = "videos"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    script_id = Column(Integer, ForeignKey("scripts.id"))
    youtube_channel_id = Column(Integer, ForeignKey("youtube_channels.id"))
    title = Column(String(255))
    description = Column(Text)
    tags = Column(JSON)  # List of tags
    content_type = Column(Enum(ContentType), default=ContentType.LONG_FORM)
    status = Column(Enum(VideoStatus), default=VideoStatus.DRAFT)
    privacy_status = Column(Enum(PrivacyStatus), default=PrivacyStatus.PUBLIC)
    video_file_path = Column(String(500))
    thumbnail_path = Column(String(500))
    duration_seconds = Column(Integer)
    youtube_video_id = Column(String(255), index=True)
    upload_date = Column(DateTime)
    scheduled_date = Column(DateTime)
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    seo_score = Column(Float)
    viral_score = Column(Float)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="videos")
    script = relationship("Script", back_populates="videos")
    youtube_channel = relationship("YouTubeChannel", back_populates="videos")
    voiceover = relationship("Voiceover", uselist=False, back_populates="video")
    captions = relationship("Caption", back_populates="video")


class Thumbnail(Base):
    __tablename__ = "thumbnails"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String(255))
    description = Column(Text)
    file_path = Column(String(500))
    thumbnail_url = Column(String(500))
    width = Column(Integer)
    height = Column(Integer)
    template_used = Column(String(100))
    text_content = Column(String(255))
    background_color = Column(String(50))
    text_color = Column(String(50))
    has_shadow_effect = Column(Boolean, default=False)
    has_text_stroke = Column(Boolean, default=False)
    viral_score = Column(Float)
    a_b_test_group = Column(String(50))
    performance_metrics = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="thumbnails")


class Voiceover(Base):
    __tablename__ = "voiceovers"
    
    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id"), unique=True)
    language = Column(Enum(Language), default=Language.ENGLISH)
    voice_gender = Column(Enum(VoiceGender), default=VoiceGender.MALE)
    voice_provider = Column(String(50))  # gtts, elevenlabs, azure, etc
    voice_id = Column(String(100))
    audio_file_path = Column(String(500))
    duration_seconds = Column(Float)
    emotion = Column(String(50))
    speed = Column(Float, default=1.0)
    pitch = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    video = relationship("Video", back_populates="voiceover")


class Caption(Base):
    __tablename__ = "captions"
    
    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id"))
    language = Column(Enum(Language), default=Language.ENGLISH)
    srt_file_path = Column(String(500))
    vtt_file_path = Column(String(500))
    txt_file_path = Column(String(500))
    caption_text = Column(Text)
    accuracy_score = Column(Float)
    auto_generated = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    video = relationship("Video", back_populates="captions")


# ================================================
# SEO & OPTIMIZATION
# ================================================

class SEOMetadata(Base):
    __tablename__ = "seo_metadata"
    
    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id"), unique=True)
    seo_title = Column(String(255))
    seo_description = Column(Text)
    keywords = Column(JSON)  # List of keywords
    hashtags = Column(JSON)  # List of hashtags
    seo_score = Column(Float)
    title_optimization = Column(Float)
    description_optimization = Column(Float)
    keyword_density = Column(Float)
    competitor_analysis = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TrendingTopic(Base):
    __tablename__ = "trending_topics"
    
    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String(255), unique=True, index=True)
    category = Column(String(100))
    trend_score = Column(Float)
    search_volume = Column(Integer)
    competition_level = Column(String(50))
    keyword_difficulty = Column(Float)
    viral_potential = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ================================================
# ANALYTICS
# ================================================

class Analytics(Base):
    __tablename__ = "analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    metric_type = Column(String(100))  # views, likes, comments, watch_time, etc
    metric_value = Column(Float)
    date = Column(DateTime)
    video_id = Column(Integer, ForeignKey("videos.id"), nullable=True)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="analytics")


class VideoAnalytics(Base):
    __tablename__ = "video_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id"), unique=True)
    youtube_video_id = Column(String(255))
    total_views = Column(Integer, default=0)
    total_likes = Column(Integer, default=0)
    total_comments = Column(Integer, default=0)
    total_shares = Column(Integer, default=0)
    watch_time_hours = Column(Float, default=0)
    average_view_duration = Column(Float, default=0)
    click_through_rate = Column(Float, default=0)
    retention_rate = Column(Float, default=0)
    last_synced = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ================================================
# CONTENT CALENDAR
# ================================================

class ContentSchedule(Base):
    __tablename__ = "content_schedule"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    video_id = Column(Integer, ForeignKey("videos.id"), nullable=True)
    scheduled_date = Column(DateTime)
    content_title = Column(String(255))
    content_description = Column(Text)
    status = Column(String(50), default="scheduled")  # scheduled, published, cancelled
    publish_time = Column(String(10))  # HH:MM format
    youtube_channel_id = Column(Integer, ForeignKey("youtube_channels.id"), nullable=True)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ================================================
# GENERATED FILES & CACHE
# ================================================

class GeneratedAsset(Base):
    __tablename__ = "generated_assets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    asset_type = Column(String(100))  # video, audio, image, script, thumbnail
    file_path = Column(String(500))
    file_size = Column(Integer)
    duration_seconds = Column(Float, nullable=True)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


# ================================================
# INDEXES
# ================================================

Index('idx_user_id', User.id)
Index('idx_video_user_id', Video.user_id)
Index('idx_video_status', Video.status)
Index('idx_video_youtube_id', Video.youtube_video_id)
Index('idx_script_user_id', Script.user_id)
Index('idx_thumbnail_user_id', Thumbnail.user_id)
Index('idx_channel_user_id', YouTubeChannel.user_id)
Index('idx_schedule_date', ContentSchedule.scheduled_date)
Index('idx_trending_topic', TrendingTopic.trend_score)
