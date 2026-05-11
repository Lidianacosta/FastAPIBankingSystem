import secrets

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.config import settings
from src.main import app
from src.models.user import User
from src.utils.database import (
    async_create_db_and_tables,
    async_engine,
    get_async_session,
)
from src.utils.password import get_password_hash


@pytest_asyncio.fixture(scope="function")
async def db():
    if "sqlite" in settings.database_url:
        settings.database_url = "sqlite+aiosqlite:///:memory:"

    settings.environment = "testing"

    await async_create_db_and_tables()

    yield

    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await async_engine.dispose()


@pytest_asyncio.fixture
async def client(db):

    async def override_get_session():
        async with AsyncSession(async_engine) as session:
            yield session

    app.dependency_overrides[get_async_session] = override_get_session

    transport = ASGITransport(app=app)
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    async with AsyncClient(
        base_url="https://test",
        transport=transport,
        headers=headers,
    ) as client:
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def access_token(client: AsyncClient):

    async with AsyncSession(async_engine) as session:
        test_password = secrets.token_urlsafe(16)
        test_user = User(
            username="test_user",
            hashed_password=get_password_hash(test_password),
        )
        session.add(test_user)
        await session.commit()
        await session.refresh(test_user)
        await session.close()

    response = await client.post(
        "/api/auth/token",
        data={
            "username": test_user.username,
            "password": test_password,
            "grant_type": "password",
        },
        headers={
            "Authorization": "Bearer token",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"Auth failed: {response.status_code} - {response.text}"
        )

    return response.json()["access_token"]


@pytest_asyncio.fixture
async def demo_access_token(client: AsyncClient):
    async with AsyncSession(async_engine) as session:
        test_password = secrets.token_urlsafe(16)
        test_user = User(
            username="demo_user",
            hashed_password=get_password_hash(test_password),
            is_demo=True,
        )
        session.add(test_user)
        await session.commit()
        await session.refresh(test_user)
        await session.close()

    response = await client.post(
        "/api/auth/token",
        data={
            "username": test_user.username,
            "password": test_password,
            "grant_type": "password",
        },
        headers={
            "Authorization": "Bearer token",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )

    return response.json()["access_token"]
