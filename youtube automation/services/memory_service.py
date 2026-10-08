"""
Long-term Memory Service for AI Learning and Optimization
Enables the system to remember previous videos, detect repeated topics,
learn audience interests, and optimize future content.
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from config.settings import MEMORY_DB_PATH, BASE_DIR
import os


class MemoryService:
    """Handles long-term memory for content learning and optimization"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or os.path.join(BASE_DIR, MEMORY_DB_PATH)
        self._ensure_db()
    
    def _ensure_db(self):
        """Initialize database with required tables"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Content history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS content_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id TEXT UNIQUE,
                title TEXT,
                topic TEXT,
                script TEXT,
                thumbnail_path TEXT,
                published_at TIMESTAMP,
                ctr REAL,
                watch_time_minutes REAL,
                retention_percentage REAL,
                likes INTEGER,
                comments INTEGER,
                shares INTEGER,
                audience_demographics TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Topic memory table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS topic_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT UNIQUE,
                occurrences INTEGER DEFAULT 1,
                avg_ctr REAL,
                avg_watch_time REAL,
                last_used TIMESTAMP,
                next_recommended TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Audience interest table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audience_interests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT,
                category TEXT,
                interest_score REAL,
                engagement_metric REAL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Channel tone memory
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS channel_tone (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tone_attribute TEXT UNIQUE,
                intensity REAL,
                examples TEXT,
                effectiveness REAL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Script patterns table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS script_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_name TEXT,
                pattern_content TEXT,
                effectiveness_score REAL,
                usage_count INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    # ========== CONTENT HISTORY ==========
    
    def save_video_record(self, video_data: Dict[str, Any]) -> bool:
        """Save published video information for future reference"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO content_history 
                (video_id, title, topic, script, thumbnail_path, published_at, 
                 ctr, watch_time_minutes, retention_percentage, likes, comments, shares, audience_demographics)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                video_data.get("video_id"),
                video_data.get("title"),
                video_data.get("topic"),
                video_data.get("script"),
                video_data.get("thumbnail_path"),
                video_data.get("published_at", datetime.now()),
                video_data.get("ctr", 0),
                video_data.get("watch_time_minutes", 0),
                video_data.get("retention_percentage", 0),
                video_data.get("likes", 0),
                video_data.get("comments", 0),
                video_data.get("shares", 0),
                json.dumps(video_data.get("audience_demographics", {}))
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving video record: {e}")
            return False
    
    def get_content_history(self, limit: int = 50) -> List[Dict]:
        """Retrieve recent content history"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM content_history 
                ORDER BY published_at DESC 
                LIMIT ?
            """, (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"Error retrieving content history: {e}")
            return []
    
    # ========== TOPIC MEMORY ==========
    
    def remember_topic(self, topic: str, performance_metrics: Dict[str, float]) -> bool:
        """Remember topic performance for future recommendations"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM topic_memory WHERE topic = ?", (topic,))
            existing = cursor.fetchone()
            
            if existing:
                # Update existing
                new_occurrences = existing["occurrences"] + 1
                new_avg_ctr = (existing["avg_ctr"] * existing["occurrences"] + 
                             performance_metrics.get("ctr", 0)) / new_occurrences
                new_avg_watch_time = (existing["avg_watch_time"] * existing["occurrences"] + 
                                     performance_metrics.get("watch_time", 0)) / new_occurrences
                
                cursor.execute("""
                    UPDATE topic_memory 
                    SET occurrences = ?, avg_ctr = ?, avg_watch_time = ?, last_used = ?
                    WHERE topic = ?
                """, (new_occurrences, new_avg_ctr, new_avg_watch_time, datetime.now(), topic))
            else:
                # Insert new
                cursor.execute("""
                    INSERT INTO topic_memory 
                    (topic, avg_ctr, avg_watch_time, last_used)
                    VALUES (?, ?, ?, ?)
                """, (topic, performance_metrics.get("ctr", 0), 
                      performance_metrics.get("watch_time", 0), datetime.now()))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error remembering topic: {e}")
            return False
    
    def detect_repeated_topics(self, days: int = 90) -> List[Dict]:
        """Detect topics that have been covered multiple times"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cutoff_date = datetime.now() - timedelta(days=days)
            
            cursor.execute("""
                SELECT topic, COUNT(*) as count, AVG(ctr) as avg_ctr
                FROM content_history 
                WHERE published_at > ?
                GROUP BY topic
                HAVING count > 1
                ORDER BY count DESC
            """, (cutoff_date,))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"Error detecting repeated topics: {e}")
            return []
    
    def get_best_performing_topics(self, limit: int = 10) -> List[Dict]:
        """Get highest performing topics"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT topic, avg_ctr, avg_watch_time, occurrences
                FROM topic_memory 
                ORDER BY avg_ctr DESC 
                LIMIT ?
            """, (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"Error getting best topics: {e}")
            return []
    
    # ========== AUDIENCE INTERESTS ==========
    
    def update_audience_interests(self, interests: Dict[str, float]) -> bool:
        """Update learned audience interests"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            for topic, score in interests.items():
                cursor.execute("SELECT * FROM audience_interests WHERE topic = ?", (topic,))
                existing = cursor.fetchone()
                
                if existing:
                    cursor.execute("""
                        UPDATE audience_interests 
                        SET interest_score = (interest_score + ?) / 2,
                            last_updated = ?
                        WHERE topic = ?
                    """, (score, datetime.now(), topic))
                else:
                    cursor.execute("""
                        INSERT INTO audience_interests 
                        (topic, interest_score, last_updated)
                        VALUES (?, ?, ?)
                    """, (topic, score, datetime.now()))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating audience interests: {e}")
            return False
    
    def get_audience_interests(self, limit: int = 20) -> List[Dict]:
        """Get current audience interests"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT topic, interest_score
                FROM audience_interests
                ORDER BY interest_score DESC
                LIMIT ?
            """, (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"Error getting audience interests: {e}")
            return []
    
    # ========== CHANNEL TONE ==========
    
    def remember_channel_tone(self, tone_attributes: Dict[str, float]) -> bool:
        """Remember and learn channel tone for consistency"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            for attribute, intensity in tone_attributes.items():
                cursor.execute("SELECT * FROM channel_tone WHERE tone_attribute = ?", (attribute,))
                existing = cursor.fetchone()
                
                if existing:
                    cursor.execute("""
                        UPDATE channel_tone 
                        SET intensity = (intensity + ?) / 2,
                            updated_at = ?
                        WHERE tone_attribute = ?
                    """, (intensity, datetime.now(), attribute))
                else:
                    cursor.execute("""
                        INSERT INTO channel_tone (tone_attribute, intensity)
                        VALUES (?, ?)
                    """, (attribute, intensity))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error remembering channel tone: {e}")
            return False
    
    def get_channel_tone(self) -> Dict[str, float]:
        """Get learned channel tone"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT tone_attribute, intensity FROM channel_tone")
            rows = cursor.fetchall()
            conn.close()
            
            return {row["tone_attribute"]: row["intensity"] for row in rows}
        except Exception as e:
            print(f"Error getting channel tone: {e}")
            return {}
    
    # ========== SCRIPT PATTERNS ==========
    
    def save_script_pattern(self, pattern_name: str, pattern_content: str, effectiveness: float) -> bool:
        """Save successful script patterns for reuse"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM script_patterns WHERE pattern_name = ?", (pattern_name,))
            existing = cursor.fetchone()
            
            if existing:
                cursor.execute("""
                    UPDATE script_patterns 
                    SET effectiveness_score = (effectiveness_score + ?) / 2,
                        usage_count = usage_count + 1
                    WHERE pattern_name = ?
                """, (effectiveness, pattern_name))
            else:
                cursor.execute("""
                    INSERT INTO script_patterns 
                    (pattern_name, pattern_content, effectiveness_score)
                    VALUES (?, ?, ?)
                """, (pattern_name, pattern_content, effectiveness))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving script pattern: {e}")
            return False
    
    def get_best_script_patterns(self, limit: int = 5) -> List[Dict]:
        """Get most effective script patterns"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT pattern_name, pattern_content, effectiveness_score, usage_count
                FROM script_patterns
                ORDER BY effectiveness_score DESC
                LIMIT ?
            """, (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"Error getting script patterns: {e}")
            return []
    
    # ========== ANALYTICS SUMMARY ==========
    
    def get_learning_summary(self) -> Dict[str, Any]:
        """Get comprehensive learning summary for system optimization"""
        return {
            "best_topics": self.get_best_performing_topics(5),
            "audience_interests": self.get_audience_interests(10),
            "channel_tone": self.get_channel_tone(),
            "repeated_topics": self.detect_repeated_topics(),
            "effective_scripts": self.get_best_script_patterns(),
            "total_videos": self._count_videos()
        }
    
    def _count_videos(self) -> int:
        """Count total videos in history"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM content_history")
            result = cursor.fetchone()
            conn.close()
            return result["count"] if result else 0
        except:
            return 0


# Global instance
_memory_service = None


def get_memory_service() -> MemoryService:
    """Get or create memory service instance"""
    global _memory_service
    if _memory_service is None:
        _memory_service = MemoryService()
    return _memory_service
