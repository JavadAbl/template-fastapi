

from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from fastapi import Depends
from .database import async_session


# 1. Inject DB Session
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for FastAPI or general use."""
    async with async_session() as session:
        yield session

SessionDep = Annotated[AsyncSession, Depends(get_session)]
