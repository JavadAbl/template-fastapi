
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlmodel import SQLModel
from app.contracts.config import get_settings

config = get_settings()

engine = create_async_engine(
    url=config.database_url,
    echo=True,
    future=True,
)

# Async session factory
async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db():
    """Create all tables (call once on startup)."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def close_db():
    """Dispose of the engine and close all connections."""
    await engine.dispose()
