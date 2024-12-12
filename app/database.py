from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from typing import Optional, Iterator
from config import Settings

class DatabaseConfig:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_db_config()
        return cls._instance
    
    def _init_db_config(self):
        # Load settings
        self.app_settings = Settings()
        
        # Create engine with optimized connection pooling
        self.engine = create_engine(
            self.app_settings.get_full_db_url(),
            poolclass=QueuePool,
            pool_size=10,  # Adjust based on your needs
            max_overflow=20,  # Allow bursts of connections
            pool_timeout=30,  # Wait up to 30 seconds for a connection
            pool_recycle=1800,  # Recycle connections after 30 minutes
            pool_pre_ping=True,  # Test connection health before use
            echo=False  # Set to True for logging SQL statements (useful for debugging)
        )
        
        # Create session factory
        self.SessionLocal = sessionmaker(
            autocommit=False, 
            autoflush=False, 
            bind=self.engine
        )

# Create a single instance of database configuration
db_config = DatabaseConfig()

# Declarative base for ORM models
Base = declarative_base()

# Dependency to get database session
def get_db() -> Iterator[Session]:
    """
    Dependency function to provide a database session.
    Ensures proper session management and cleanup.
    """
    db = db_config.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Optional: Connection management functions
def get_engine():
    """
    Returns the SQLAlchemy engine with connection pooling.
    """
    return db_config.engine

def close_db_connections():
    """
    Dispose of all connections in the pool.
    Use cautiously, typically during application shutdown.
    """
    if hasattr(db_config, 'engine'):
        db_config.engine.dispose()