"""
Celery Configuration for Background Task Processing
Handles video generation, uploads, and analytics processing
"""

from celery import Celery, Task
from celery.schedules import crontab
from config.settings import CELERY_BROKER_URL, CELERY_RESULT_BACKEND
import os
from datetime import timedelta

# Initialize Celery app
app = Celery(
    'youtube_automation',
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND
)

# Configure Celery
app.conf.update(
    # Task settings
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Timeouts
    task_time_limit=3600,  # Hard limit 1 hour
    task_soft_time_limit=3300,  # Soft limit 55 minutes
    
    # Routing
    task_default_queue='default',
    task_default_exchange='default',
    task_default_routing_key='default',
    
    # Result backend
    result_expires=3600,  # Results expire after 1 hour
    
    # Worker settings
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    
    # Periodic tasks
    beat_schedule={
        'detect-trends-hourly': {
            'task': 'tasks.detect_trends_task',
            'schedule': timedelta(hours=1),
        },
        'publish-scheduled-videos': {
            'task': 'tasks.publish_scheduled_videos_task',
            'schedule': timedelta(minutes=5),
        },
        'sync-analytics-hourly': {
            'task': 'tasks.sync_analytics_task',
            'schedule': timedelta(hours=1),
        },
        'optimize-learning-daily': {
            'task': 'tasks.optimize_learning_task',
            'schedule': crontab(hour=0, minute=0),
        },
    }
)


# Define task class
class CallbackTask(Task):
    """Task with callback support"""
    
    def on_success(self, retval, task_id, args, kwargs):
        """Success callback"""
        from utils.logger import logger
        logger.info(f"Task {task_id} succeeded with result: {retval}")
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Failure callback"""
        from utils.logger import logger
        logger.error(f"Task {task_id} failed with exception: {exc}")


app.Task = CallbackTask


# Task definitions

@app.task(bind=True, max_retries=3)
def generate_content_task(self, task_data: dict):
    """
    Celery task for autonomous content generation
    """
    from services.ai_media_orchestrator import ai_orchestrator, WorkflowConfig
    from database.manager import db
    import asyncio
    
    try:
        # Update task status
        db.update_task_status(
            task_data.get('task_id'),
            'PROCESSING',
            progress=10
        )
        
        # Create workflow config
        config = WorkflowConfig(
            user_id=task_data['user_id'],
            channel_id=task_data['channel_id'],
            topic=task_data['topic'],
            content_type=task_data.get('content_type', 'full_video'),
            autonomous_mode=task_data.get('autonomous_mode', True),
            auto_upload=task_data.get('auto_upload', False),
            generate_shorts=task_data.get('generate_shorts', True),
            auto_thumbnail=task_data.get('auto_thumbnail', True),
            target_retention=task_data.get('target_retention', 75.0)
        )
        
        # Run workflow
        result = asyncio.run(ai_orchestrator.start_autonomous_workflow(config))
        
        # Update task status
        db.update_task_status(
            task_data.get('task_id'),
            'COMPLETED',
            progress=100,
            result=result
        )
        
        return {
            "status": "success",
            "workflow_id": result.get("user_id"),
            "stages": list(result.get("stages", {}).keys())
        }
        
    except Exception as exc:
        from utils.logger import logger
        logger.error(f"Task failed: {str(exc)}")
        
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@app.task
def detect_trends_task():
    """
    Hourly task to detect new viral trends
    """
    from services.topic_intelligence import topic_engine
    from database.manager import db
    from utils.logger import logger
    import asyncio
    
    try:
        logger.info("Running trend detection task")
        
        # Get all active users
        # TODO: Implement user enumeration from database
        
        # For each user, detect trends
        # opportunities = asyncio.run(
        #     topic_engine.detect_viral_topics(user_id, num_topics=5)
        # )
        
        logger.info("Trend detection completed")
        
    except Exception as e:
        logger.error(f"Trend detection failed: {str(e)}")


@app.task
def publish_scheduled_videos_task():
    """
    Every 5 minutes: Check for videos ready to publish
    """
    from database.manager import db
    from utils.logger import logger
    
    try:
        logger.info("Checking for videos ready to publish")
        
        # Get pending publishes
        pending = db.get_pending_publishes()
        
        for queue_item in pending:
            try:
                logger.info(f"Publishing video: {queue_item.video_id}")
                
                # TODO: Implement YouTube upload
                # youtube_service.upload_video(queue_item.video_id)
                
            except Exception as e:
                logger.error(f"Failed to publish video: {str(e)}")
        
        logger.info(f"Publishing check completed. Found {len(pending)} videos.")
        
    except Exception as e:
        logger.error(f"Publishing task failed: {str(e)}")


@app.task
def sync_analytics_task():
    """
    Hourly: Sync analytics from YouTube
    """
    from database.manager import db
    from utils.logger import logger
    import asyncio
    
    try:
        logger.info("Syncing analytics from YouTube")
        
        # Get all videos published in last 30 days
        # For each, fetch analytics from YouTube API
        # Store in database
        
        logger.info("Analytics sync completed")
        
    except Exception as e:
        logger.error(f"Analytics sync failed: {str(e)}")


@app.task
def optimize_learning_task():
    """
    Daily: Optimize AI learning models
    """
    from services.learning_loop import learning_loop
    from database.manager import db
    from utils.logger import logger
    import asyncio
    
    try:
        logger.info("Running daily learning optimization")
        
        # TODO: Get all users and update their learning states
        # For each user:
        #   - Analyze last 10 videos
        #   - Update learning patterns
        #   - Generate new recommendations
        
        logger.info("Learning optimization completed")
        
    except Exception as e:
        logger.error(f"Learning optimization failed: {str(e)}")


@app.task
def cleanup_old_tasks_task():
    """
    Daily cleanup of old task records
    """
    from database.manager import db
    from utils.logger import logger
    from datetime import datetime, timedelta
    
    try:
        logger.info("Cleaning up old task records")
        
        # Delete tasks older than 30 days
        cutoff = datetime.utcnow() - timedelta(days=30)
        
        # TODO: Implement cleanup
        
        logger.info("Cleanup completed")
        
    except Exception as e:
        logger.error(f"Cleanup failed: {str(e)}")


# Export for use in other modules
__all__ = [
    'app',
    'generate_content_task',
    'detect_trends_task',
    'publish_scheduled_videos_task',
    'sync_analytics_task',
    'optimize_learning_task',
    'cleanup_old_tasks_task'
]
