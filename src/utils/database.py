from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio.engine import create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.config import settings

if settings.environment != "production":
    connect_args = {"check_same_thread": False}
    echo = False
else:
    echo = True
    connect_args = {}


async_engine = create_async_engine(
    settings.database_url, echo=echo, connect_args=connect_args
)


async def async_create_db_and_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_async_session():
    async with AsyncSession(async_engine) as session:
        yield session


AsyncSessionDep = Annotated[AsyncSession, Depends(get_async_session)]
