"""
Database Connection & Session Management
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os
from pathlib import Path

from .models import Base

# Database URL - SQLite für Entwicklung
DATABASE_DIR = Path(__file__).parent.parent.parent / "data"
DATABASE_DIR.mkdir(exist_ok=True)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{DATABASE_DIR}/trading.db"
)

# Create Engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    poolclass=StaticPool if "sqlite" in DATABASE_URL else None,
    echo=False  # Set to True for SQL debugging
)

# Session Factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize Database - Create all tables"""
    Base.metadata.create_all(bind=engine)
    print(f"✅ Database initialized at: {DATABASE_URL}")


def get_db():
    """Dependency for FastAPI to get DB session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def reset_db():
    """⚠️ WARNING: Drops all tables and recreates them"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("⚠️ Database reset complete")
