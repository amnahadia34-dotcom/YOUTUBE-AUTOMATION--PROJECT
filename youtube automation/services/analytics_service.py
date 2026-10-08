from typing import Dict, Any
from config.settings import BASE_DIR
from database.database import DatabaseManager
from services.memory_service import MemoryService
from utils.logger import logger


class AnalyticsService:
    def __init__(self):
        DatabaseManager.init_db()
        self.memory_service = MemoryService()

    def record_video_metrics(
        self,
        video_id: str,
        title: str,
        topic: str,
        script: str,
        thumbnail_path: str,
        views: int = 0,
        likes: int = 0,
        watch_time_seconds: float = 0.0,
        retention_rate: float = 0.0,
        comments: int = 0,
        shares: int = 0,
        ctr: float = 0.0
    ) -> bool:
        try:
            DatabaseManager.save_analytics_record(
                video_id=video_id,
                views=views,
                likes=likes,
                watch_time_seconds=watch_time_seconds,
                retention_rate=retention_rate
            )
            self.memory_service.save_video_record({
                "video_id": video_id,
                "title": title,
                "topic": topic,
                "script": script,
                "thumbnail_path": thumbnail_path,
                "published_at": None,
                "ctr": ctr,
                "watch_time_minutes": watch_time_seconds / 60.0,
                "retention_percentage": retention_rate,
                "likes": likes,
                "comments": comments,
                "shares": shares,
                "audience_demographics": {}
            })
            logger.info(f"Analytics recorded for video {video_id}")
            return True
        except Exception as exc:
            logger.error(f"Analytics recording failed: {exc}")
            return False

    def get_video_analytics(self, video_id: str) -> Dict[str, Any]:
        data = DatabaseManager.get_video_analytics(video_id)
        return {
            "views": data.get("views", 0),
            "likes": data.get("likes", 0),
            "watch_time_seconds": data.get("watch_time_seconds", 0.0),
            "average_retention": round(data.get("average_retention", 0.0), 2)
        }

    def get_channel_overview(self) -> Dict[str, Any]:
        data = DatabaseManager.get_channel_overview()
        return {
            "views": data.get("views", 0),
            "likes": data.get("likes", 0),
            "watch_time_seconds": data.get("watch_time_seconds", 0.0),
            "average_retention": round(data.get("average_retention", 0.0), 2)
        }

    def summarize_performance(self, limit: int = 10) -> Dict[str, Any]:
        history = self.memory_service.get_content_history(limit)
        total = len(history)
        avg_ctr = sum(v.get("ctr", 0) for v in history) / max(total, 1)
        avg_watch_time = sum(v.get("watch_time_minutes", 0) for v in history) / max(total, 1)
        return {
            "total_videos": total,
            "average_ctr": round(avg_ctr, 4),
            "average_watch_time_minutes": round(avg_watch_time, 2),
            "top_topics": self.memory_service.get_best_performing_topics(5)
        }


AnalyticsTracker = AnalyticsService
