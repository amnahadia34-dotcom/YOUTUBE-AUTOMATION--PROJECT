import json
import os
import sqlite3
from datetime import datetime
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))
load_dotenv(os.path.join(ROOT_DIR, ".env"))

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{os.path.join(ROOT_DIR, 'database', 'content_history.db')}"
)


def _ensure_database_path(path: str):
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)


def _get_connection():
    if DATABASE_URL.startswith("sqlite:///"):
        path = DATABASE_URL.replace("sqlite:///", "", 1)
        _ensure_database_path(path)
        conn = sqlite3.connect(path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    raise RuntimeError(
        "Unsupported database URL. Use a sqlite:/// path in DATABASE_URL or extend the database layer for PostgreSQL."
    )


def _execute(query: str, params=(), fetch=False):
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    result = cursor.fetchall() if fetch else None
    conn.commit()
    conn.close()
    return result


def init_db():
    conn = _get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS generated_videos (
            id TEXT PRIMARY KEY,
            created_at TEXT,
            topic TEXT,
            title TEXT,
            description TEXT,
            script TEXT,
            caption TEXT,
            hashtags TEXT,
            tags TEXT,
            file_path TEXT,
            youtube_url TEXT,
            seo_title TEXT,
            seo_description TEXT,
            status TEXT
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS schedule_queue (
            job_id TEXT PRIMARY KEY,
            video_path TEXT,
            title TEXT,
            description TEXT,
            publish_at TEXT,
            privacy_status TEXT,
            status TEXT,
            created_at TEXT,
            youtube_url TEXT
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS analytics_records (
            id TEXT PRIMARY KEY,
            video_id TEXT,
            views INTEGER,
            likes INTEGER,
            watch_time_seconds REAL,
            retention_rate REAL,
            recorded_at TEXT
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS generation_tasks (
            task_id TEXT PRIMARY KEY,
            created_at TEXT,
            updated_at TEXT,
            user_id TEXT,
            topic TEXT,
            mode TEXT,
            payload TEXT,
            status TEXT,
            progress INTEGER,
            result TEXT,
            error TEXT
        )
        """
    )

    conn.commit()
    conn.close()


def save_task(
    task_id: str,
    user_id: str,
    topic: str,
    mode: str,
    payload: dict,
    status: str = "QUEUED",
    progress: int = 0,
    result: dict | None = None,
    error: str | None = None
):
    init_db()
    _execute(
        """
        INSERT OR REPLACE INTO generation_tasks (
            task_id, created_at, updated_at, user_id,
            topic, mode, payload, status, progress, result, error
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            task_id,
            datetime.utcnow().isoformat(),
            datetime.utcnow().isoformat(),
            user_id,
            topic,
            mode,
            json.dumps(payload),
            status,
            progress,
            json.dumps(result or {}),
            error
        )
    )


def update_task(
    task_id: str,
    status: str,
    progress: int,
    result: dict | None = None,
    error: str | None = None
):
    init_db()
    existing = get_task(task_id)
    if not existing:
        raise ValueError(f"Task not found: {task_id}")

    payload = json.loads(existing.get("payload", "{}"))
    merged_result = {**json.loads(existing.get("result", "{}")), **(result or {})}

    _execute(
        """
        UPDATE generation_tasks
        SET status = ?, progress = ?, result = ?, error = ?, updated_at = ?
        WHERE task_id = ?
        """,
        (
            status,
            progress,
            json.dumps(merged_result),
            error,
            datetime.utcnow().isoformat(),
            task_id
        )
    )


def get_task(task_id: str):
    init_db()
    rows = _execute("SELECT * FROM generation_tasks WHERE task_id = ?", (task_id,), fetch=True)
    return dict(rows[0]) if rows else None


def list_tasks(user_id: str = None):
    init_db()
    if user_id:
        rows = _execute("SELECT * FROM generation_tasks WHERE user_id = ? ORDER BY created_at DESC", (user_id,), fetch=True)
    else:
        rows = _execute("SELECT * FROM generation_tasks ORDER BY created_at DESC", fetch=True)
    return [dict(row) for row in rows] if rows else []


def save_generated_video(
    video_id: str,
    topic: str,
    title: str,
    description: str,
    script: str,
    caption: str,
    hashtags: list,
    tags: list,
    file_path: str,
    youtube_url: str,
    seo_title: str,
    seo_description: str,
    status: str = "created"
):
    init_db()
    _execute(
        """
        INSERT OR REPLACE INTO generated_videos (
            id, created_at, topic, title, description, script,
            caption, hashtags, tags, file_path, youtube_url,
            seo_title, seo_description, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            video_id,
            datetime.utcnow().isoformat(),
            topic,
            title,
            description,
            script,
            caption,
            json.dumps(hashtags),
            json.dumps(tags),
            file_path,
            youtube_url,
            seo_title,
            seo_description,
            status
        )
    )


def save_schedule_job(job: dict):
    init_db()
    _execute(
        """
        INSERT OR REPLACE INTO schedule_queue (
            job_id, video_path, title, description,
            publish_at, privacy_status, status, created_at, youtube_url
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            job["job_id"],
            job["video_path"],
            job["title"],
            job["description"],
            job["publish_at"],
            job["privacy_status"],
            job["status"],
            job["created_at"],
            job.get("youtube_url")
        )
    )


def get_schedule_queue():
    init_db()
    rows = _execute("SELECT * FROM schedule_queue ORDER BY publish_at ASC", fetch=True)
    return [dict(row) for row in rows] if rows else []


def get_schedule_job(job_id: str):
    init_db()
    rows = _execute("SELECT * FROM schedule_queue WHERE job_id = ?", (job_id,), fetch=True)
    return dict(rows[0]) if rows else None


def update_schedule_status(job_id: str, status: str, youtube_url: str = None):
    init_db()
    _execute(
        "UPDATE schedule_queue SET status = ?, youtube_url = ? WHERE job_id = ?",
        (status, youtube_url, job_id)
    )


def save_analytics_record(
    video_id: str,
    views: int = 0,
    likes: int = 0,
    watch_time_seconds: float = 0.0,
    retention_rate: float = 0.0
):
    init_db()
    record_id = f"analytics_{datetime.utcnow().timestamp()}_{video_id}"
    _execute(
        """
        INSERT INTO analytics_records (
            id, video_id, views, likes, watch_time_seconds, retention_rate, recorded_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            record_id,
            video_id,
            views,
            likes,
            watch_time_seconds,
            retention_rate,
            datetime.utcnow().isoformat()
        )
    )


def get_video_analytics(video_id: str):
    init_db()
    rows = _execute(
        """
        SELECT SUM(views) as views, SUM(likes) as likes,
               SUM(watch_time_seconds) as watch_time_seconds,
               AVG(retention_rate) as average_retention
        FROM analytics_records
        WHERE video_id = ?
        """,
        (video_id,),
        fetch=True
    )
    return dict(rows[0]) if rows else {}


def get_channel_overview():
    init_db()
    rows = _execute(
        """
        SELECT SUM(views) as views, SUM(likes) as likes,
               SUM(watch_time_seconds) as watch_time_seconds,
               AVG(retention_rate) as average_retention
        FROM analytics_records
        """,
        fetch=True
    )
    return dict(rows[0]) if rows else {}


class DatabaseManager:
    @staticmethod
    def init_db():
        return init_db()

    @staticmethod
    def save_generated_video(
        video_id: str,
        topic: str,
        title: str,
        description: str,
        script: str,
        caption: str,
        hashtags: list,
        tags: list,
        file_path: str,
        youtube_url: str,
        seo_title: str,
        seo_description: str,
        status: str = "created"
    ):
        return save_generated_video(
            video_id,
            topic,
            title,
            description,
            script,
            caption,
            hashtags,
            tags,
            file_path,
            youtube_url,
            seo_title,
            seo_description,
            status
        )

    @staticmethod
    def save_schedule_job(job: dict):
        return save_schedule_job(job)

    @staticmethod
    def get_schedule_queue():
        return get_schedule_queue()

    @staticmethod
    def get_schedule_job(job_id: str):
        return get_schedule_job(job_id)

    @staticmethod
    def update_schedule_status(job_id: str, status: str, youtube_url: str = None):
        return update_schedule_status(job_id, status, youtube_url=youtube_url)

    @staticmethod
    def save_analytics_record(video_id: str, views: int = 0, likes: int = 0, watch_time_seconds: float = 0.0, retention_rate: float = 0.0):
        return save_analytics_record(video_id, views, likes, watch_time_seconds, retention_rate)

    @staticmethod
    def get_video_analytics(video_id: str):
        return get_video_analytics(video_id)

    @staticmethod
    def get_channel_overview():
        return get_channel_overview()

    @staticmethod
    def save_task(
        task_id: str,
        user_id: str,
        topic: str,
        mode: str,
        payload: dict,
        status: str = "QUEUED",
        progress: int = 0,
        result: dict | None = None,
        error: str | None = None
    ):
        return save_task(task_id, user_id, topic, mode, payload, status, progress, result, error)

    @staticmethod
    def update_task(
        task_id: str,
        status: str,
        progress: int,
        result: dict | None = None,
        error: str | None = None
    ):
        return update_task(task_id, status, progress, result, error)

    @staticmethod
    def get_task(task_id: str):
        return get_task(task_id)

    @staticmethod
    def list_tasks(user_id: str = None):
        return list_tasks(user_id)
