# ================================================
# DATABASE CONNECTION & SESSION MANAGEMENT
# ================================================

import os
import sqlite3
from contextlib import contextmanager
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import logging
from datetime import datetime

from database.saas_models import Base

logger = logging.getLogger(__name__)

# ================================================
# DATABASE CONFIGURATION
# ================================================

DATABASE_URL = "sqlite:///./youtube_saas.db"

# SQLite engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# ================================================
# DATABASE INITIALIZATION
# ================================================

def init_db():
    """Initialize database with all tables."""
    try:
        logger.info("Initializing database...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database initialized successfully")
        
        # Enable foreign keys for SQLite
        with engine.connect() as conn:
            conn.execute("PRAGMA foreign_keys=ON")
        
        return True
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        return False


def get_db() -> Session:
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context():
    """Context manager for database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ================================================
# DATABASE OPERATIONS
# ================================================

class DatabaseManager:
    """Database manager for CRUD operations."""
    
    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal
    
    def create_session(self) -> Session:
        """Create a new database session."""
        return self.SessionLocal()
    
    def close_session(self, session: Session):
        """Close database session."""
        if session:
            session.close()
    
    def execute_query(self, query_str: str):
        """Execute raw SQL query."""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query_str)
                return result.fetchall()
        except Exception as e:
            logger.error(f"Query execution error: {e}")
            return None
    
    def check_connection(self) -> bool:
        """Check if database connection is working."""
        try:
            with self.engine.connect() as conn:
                conn.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            return False
    
    def get_db_size(self) -> str:
        """Get database file size."""
        try:
            db_path = "youtube_saas.db"
            if os.path.exists(db_path):
                size_bytes = os.path.getsize(db_path)
                size_mb = size_bytes / (1024 * 1024)
                return f"{size_mb:.2f} MB"
            return "0 MB"
        except Exception as e:
            logger.error(f"Error getting DB size: {e}")
            return "Unknown"
    
    def backup_database(self, backup_path: str = None) -> bool:
        """Backup database file."""
        try:
            if backup_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = f"youtube_saas_backup_{timestamp}.db"
            
            source = "youtube_saas.db"
            if os.path.exists(source):
                with open(source, 'rb') as f_src:
                    with open(backup_path, 'wb') as f_dst:
                        f_dst.write(f_src.read())
                logger.info(f"✅ Database backed up to {backup_path}")
                return True
            else:
                logger.warning("Database file not found for backup")
                return False
        except Exception as e:
            logger.error(f"❌ Backup failed: {e}")
            return False
    
    def clear_old_data(self, days: int = 90) -> int:
        """Delete data older than specified days."""
        try:
            from datetime import timedelta
            from database.saas_models import GeneratedAsset, Analytics
            
            session = self.create_session()
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Delete old generated assets
            deleted_assets = session.query(GeneratedAsset).filter(
                GeneratedAsset.created_at < cutoff_date
            ).delete()
            
            # Delete old analytics entries (keep summary)
            deleted_analytics = session.query(Analytics).filter(
                Analytics.created_at < cutoff_date
            ).delete()
            
            session.commit()
            total_deleted = deleted_assets + deleted_analytics
            logger.info(f"Cleared {total_deleted} old records")
            
            return total_deleted
        except Exception as e:
            logger.error(f"❌ Error clearing old data: {e}")
            return 0
        finally:
            self.close_session(session)


# ================================================
# GLOBAL DATABASE MANAGER
# ================================================

db_manager = DatabaseManager()


# ================================================
# DATABASE INITIALIZATION ON IMPORT
# ================================================

if not os.path.exists("youtube_saas.db"):
    init_db()
