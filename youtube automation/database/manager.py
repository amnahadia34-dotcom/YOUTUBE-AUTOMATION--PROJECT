"""
Production-Grade Database Manager with SQLAlchemy
Handles all database operations with proper session management, error handling, and migrations
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
import os
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from utils.logger import logger
from config.settings import DATABASE_URL, DEBUG
from database.models import (
    Base, Video, VideoStatusEnum, YouTubeChannel, Task, TaskStatusEnum,
    Trend, CompetitorAnalysis, VideoAnalytics, ChannelAnalytics,
    ContentLearningState, PerformanceLearning, PublishingQueue, User,
    UserPreferences, AuditLog, ThumbnailVariation, VideoScene,
    SearchKeywordCache
)


class DatabaseManager:
    """Centralized database management with connection pooling"""
    
    _instance = None
    _engine = None
    _SessionLocal = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize database engine and session factory"""
        try:
            # Use PostgreSQL in production, SQLite for development
            if DATABASE_URL.startswith("postgresql"):
                self._engine = create_engine(
                    DATABASE_URL,
                    poolclass=QueuePool,
                    pool_size=20,
                    max_overflow=40,
                    pool_pre_ping=True,
                    echo=DEBUG,
                    connect_args={
                        "connect_timeout": 10,
                        "options": "-c statement_timeout=30000"
                    }
                )
            else:
                # SQLite for development
                self._engine = create_engine(
                    DATABASE_URL,
                    connect_args={"check_same_thread": False},
                    echo=DEBUG
                )
            
            self._SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self._engine
            )
            
            logger.info(f"Database manager initialized with: {DATABASE_URL}")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise
    
    @contextmanager
    def get_session(self) -> Session:
        """Get database session with automatic cleanup"""
        session = self._SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database error: {str(e)}")
            raise
        finally:
            session.close()
    
    def init_db(self):
        """Create all database tables"""
        try:
            Base.metadata.create_all(bind=self._engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create database tables: {str(e)}")
            raise
    
    # ===========================
    # VIDEO OPERATIONS
    # ===========================
    
    def create_video(self, user_id: str, channel_id: str, 
                     title: str, description: str, script: str,
                     content_type: str = "full_video", **kwargs) -> Video:
        """Create new video record"""
        with self.get_session() as session:
            video = Video(
                user_id=user_id,
                channel_id=channel_id,
                title=title,
                description=description,
                script=script,
                content_type=content_type,
                **kwargs
            )
            session.add(video)
            session.commit()
            session.refresh(video)
            return video
    
    def get_video(self, video_id: str) -> Optional[Video]:
        """Retrieve video by ID"""
        with self.get_session() as session:
            return session.query(Video).filter(Video.id == video_id).first()
    
    def update_video_status(self, video_id: str, status: VideoStatusEnum,
                           progress: int = None, error: str = None):
        """Update video status and progress"""
        with self.get_session() as session:
            video = session.query(Video).filter(Video.id == video_id).first()
            if video:
                video.status = status
                if progress is not None:
                    video.progress_percent = progress
                if error:
                    video.error_message = error
                video.updated_at = datetime.utcnow()
                session.commit()
    
    def get_user_videos(self, user_id: str, limit: int = 50,
                       status: VideoStatusEnum = None) -> List[Video]:
        """Get user's videos with optional filtering"""
        with self.get_session() as session:
            query = session.query(Video).filter(Video.user_id == user_id)
            if status:
                query = query.filter(Video.status == status)
            return query.order_by(Video.created_at.desc()).limit(limit).all()
    
    def get_channel_videos(self, channel_id: str, limit: int = 50) -> List[Video]:
        """Get all videos for a channel"""
        with self.get_session() as session:
            return session.query(Video)\
                .filter(Video.channel_id == channel_id)\
                .order_by(Video.created_at.desc())\
                .limit(limit).all()
    
    # ===========================
    # CHANNEL OPERATIONS
    # ===========================
    
    def create_channel(self, user_id: str, workspace_id: str,
                      channel_name: str, channel_id: str = None,
                      credentials_encrypted: str = None, **kwargs) -> YouTubeChannel:
        """Create new YouTube channel record"""
        with self.get_session() as session:
            channel = YouTubeChannel(
                user_id=user_id,
                workspace_id=workspace_id,
                channel_name=channel_name,
                channel_id=channel_id,
                credentials_encrypted=credentials_encrypted,
                **kwargs
            )
            session.add(channel)
            session.commit()
            session.refresh(channel)
            return channel
    
    def get_user_channels(self, user_id: str) -> List[YouTubeChannel]:
        """Get all channels for a user"""
        with self.get_session() as session:
            return session.query(YouTubeChannel)\
                .filter(YouTubeChannel.user_id == user_id)\
                .order_by(YouTubeChannel.is_primary.desc())\
                .all()
    
    def get_primary_channel(self, user_id: str) -> Optional[YouTubeChannel]:
        """Get user's primary YouTube channel"""
        with self.get_session() as session:
            return session.query(YouTubeChannel)\
                .filter(YouTubeChannel.user_id == user_id,
                       YouTubeChannel.is_primary == True).first()
    
    # ===========================
    # TASK OPERATIONS
    # ===========================
    
    def create_task(self, user_id: str, task_type: str,
                   celery_task_id: str = None, input_data: Dict = None) -> Task:
        """Create new background task"""
        with self.get_session() as session:
            task = Task(
                user_id=user_id,
                task_type=task_type,
                celery_task_id=celery_task_id,
                input_data=input_data or {},
                status=TaskStatusEnum.QUEUED
            )
            session.add(task)
            session.commit()
            session.refresh(task)
            return task
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID"""
        with self.get_session() as session:
            return session.query(Task).filter(Task.id == task_id).first()
    
    def update_task_status(self, task_id: str, status: TaskStatusEnum,
                          progress: int = None, result: Dict = None,
                          error: str = None):
        """Update task status and result"""
        with self.get_session() as session:
            task = session.query(Task).filter(Task.id == task_id).first()
            if task:
                task.status = status
                if progress is not None:
                    task.progress_percent = progress
                if result:
                    task.result_data = result
                if error:
                    task.error_message = error
                if status in [TaskStatusEnum.COMPLETED, TaskStatusEnum.FAILED]:
                    task.completed_at = datetime.utcnow()
                task.updated_at = datetime.utcnow()
                session.commit()
    
    def get_user_tasks(self, user_id: str, limit: int = 50,
                       status: TaskStatusEnum = None) -> List[Task]:
        """Get user's tasks"""
        with self.get_session() as session:
            query = session.query(Task).filter(Task.user_id == user_id)
            if status:
                query = query.filter(Task.status == status)
            return query.order_by(Task.created_at.desc()).limit(limit).all()
    
    # ===========================
    # ANALYTICS OPERATIONS
    # ===========================
    
    def record_video_analytics(self, video_id: str, views: int,
                              likes: int, comments: int, shares: int,
                              ctr: float = None, retention: float = None) -> VideoAnalytics:
        """Record video performance metrics"""
        with self.get_session() as session:
            analytics = VideoAnalytics(
                video_id=video_id,
                views=views,
                likes=likes,
                comments=comments,
                shares=shares,
                ctr=ctr,
                comment_rate=comments / views if views > 0 else 0,
                like_rate=likes / views if views > 0 else 0,
                share_rate=shares / views if views > 0 else 0,
                avg_view_percentage=retention or 0
            )
            session.add(analytics)
            session.commit()
            session.refresh(analytics)
            return analytics
    
    def get_video_analytics_history(self, video_id: str, days: int = 30) -> List[VideoAnalytics]:
        """Get video analytics over time"""
        with self.get_session() as session:
            cutoff = datetime.utcnow() - timedelta(days=days)
            return session.query(VideoAnalytics)\
                .filter(VideoAnalytics.video_id == video_id,
                       VideoAnalytics.recorded_at >= cutoff)\
                .order_by(VideoAnalytics.recorded_at.asc()).all()
    
    # ===========================
    # TREND & COMPETITOR OPERATIONS
    # ===========================
    
    def get_active_trends(self, category: str = None, limit: int = 50) -> List[Trend]:
        """Get current active trends"""
        with self.get_session() as session:
            query = session.query(Trend)\
                .filter(Trend.is_active == True,
                       Trend.expires_at > datetime.utcnow())
            if category:
                query = query.filter(Trend.category == category)
            return query.order_by(Trend.viral_score.desc()).limit(limit).all()
    
    def add_trend(self, topic: str, keyword: str, viral_score: float,
                  category: str = None, **kwargs) -> Trend:
        """Add new trend"""
        with self.get_session() as session:
            trend = Trend(
                topic=topic,
                keyword=keyword,
                viral_score=viral_score,
                category=category,
                expires_at=datetime.utcnow() + timedelta(days=30),
                **kwargs
            )
            session.add(trend)
            session.commit()
            session.refresh(trend)
            return trend
    
    # ===========================
    # LEARNING OPERATIONS
    # ===========================
    
    def get_learning_state(self, user_id: str) -> Optional[ContentLearningState]:
        """Get user's AI learning state"""
        with self.get_session() as session:
            state = session.query(ContentLearningState)\
                .filter(ContentLearningState.user_id == user_id).first()
            if not state:
                state = ContentLearningState(user_id=user_id)
                session.add(state)
                session.commit()
                session.refresh(state)
            return state
    
    def update_learning_state(self, user_id: str, **updates):
        """Update user's learning state with new patterns"""
        with self.get_session() as session:
            state = session.query(ContentLearningState)\
                .filter(ContentLearningState.user_id == user_id).first()
            if state:
                for key, value in updates.items():
                    if hasattr(state, key):
                        setattr(state, key, value)
                state.last_updated_at = datetime.utcnow()
                session.commit()
    
    # ===========================
    # PUBLISHING QUEUE OPERATIONS
    # ===========================
    
    def add_to_publishing_queue(self, video_id: str, channel_id: str,
                                scheduled_time: datetime) -> PublishingQueue:
        """Add video to publishing queue"""
        with self.get_session() as session:
            queue_item = PublishingQueue(
                video_id=video_id,
                channel_id=channel_id,
                scheduled_publish_time=scheduled_time,
                status="pending"
            )
            session.add(queue_item)
            session.commit()
            session.refresh(queue_item)
            return queue_item
    
    def get_pending_publishes(self) -> List[PublishingQueue]:
        """Get videos ready to publish"""
        with self.get_session() as session:
            return session.query(PublishingQueue)\
                .filter(PublishingQueue.status.in_(["pending", "scheduled"]),
                       PublishingQueue.scheduled_publish_time <= datetime.utcnow())\
                .order_by(PublishingQueue.scheduled_publish_time.asc()).all()
    
    # ===========================
    # AUDIT LOGGING
    # ===========================
    
    def log_action(self, user_id: str, action: str, resource_type: str,
                   resource_id: str = None, old_value: Dict = None,
                   new_value: Dict = None, ip_address: str = None):
        """Log user action for audit trail"""
        with self.get_session() as session:
            log = AuditLog(
                user_id=user_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                old_value=old_value,
                new_value=new_value,
                ip_address=ip_address
            )
            session.add(log)
            session.commit()


# Singleton instance for global access
db = DatabaseManager()
