from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from app.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

Base = declarative_base()


async def get_db():
    """Dependency for providing an async database session per request."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Create all relational tables automatically on startup if they don't exist."""
    import app.models  # noqa: F401 - ensure all ORM models are registered on Base.metadata

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def verify_db_connection() -> bool:
    """Verify async PostgreSQL connectivity by executing SELECT 1."""
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))
    return True


async def close_db():
    """Cleanly dispose of database connection pool on shutdown."""
    await engine.dispose()
