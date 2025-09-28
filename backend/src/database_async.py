"""
Async database configuration with connection pooling for high performance
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import QueuePool
from sqlalchemy import text
from typing import AsyncGenerator
import os
import logging

logger = logging.getLogger(__name__)

# Get database URL and convert to async version
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://spend_admin:admin123@localhost/spendplatform")
DATABASE_URL_ASYNC = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Create async engine with optimized connection pooling
async_engine = create_async_engine(
    DATABASE_URL_ASYNC,
    # High-performance connection pool settings (no poolclass for async)
    pool_size=20,          # Base connection pool size
    max_overflow=30,       # Additional connections during peak load
    pool_pre_ping=True,    # Validate connections before use
    pool_recycle=3600,     # Recycle connections every hour
    pool_timeout=30,       # Timeout for getting connection from pool
    # Performance optimizations
    echo=False,            # Disable SQL logging in production
    future=True,           # Use SQLAlchemy 2.0 features
)

# Async session factory with optimized settings
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Keep objects accessible after commit
    autoflush=False,         # Manual control over flushing
    autocommit=False,
)

# Async database dependency
async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Async database session dependency with proper error handling
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {str(e)}")
            await session.rollback()
            raise
        finally:
            await session.close()

# Health check function
async def check_async_database_health() -> bool:
    """Check if async database connection is healthy"""
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
            return True
    except Exception as e:
        logger.error(f"Async database health check failed: {str(e)}")
        return False