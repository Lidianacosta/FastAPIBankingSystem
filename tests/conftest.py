import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.config import settings
from src.main import app
from src.models.user import User
from src.utils.password import get_password_hash

settings.database_url = "sqlite+aiosqlite:///:memory:"
settings.environment = "testing"

from src.utils.database import (
    AsyncSessionDep,
    async_create_db_and_tables,
    async_engine,
)


@pytest_asyncio.fixture(scope="function")
async def db():
    """Create all tables and drop all after usage."""
    await async_create_db_and_tables()

    yield

    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest_asyncio.fixture
async def client(db):

    async def override_get_session():
        async with AsyncSession(async_engine) as session:
            yield session

    app.dependency_overrides[AsyncSessionDep] = override_get_session

    transport = ASGITransport(app=app)
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    async with AsyncClient(
        base_url="http://test",
        transport=transport,
        headers=headers,
    ) as client:
        yield client


@pytest_asyncio.fixture
async def access_token(client: AsyncClient):

    async with AsyncSession(async_engine) as session:
        plain_password = "test_user"
        test_user = User(
            username="test_user",
            hashed_password=get_password_hash(plain_password),
        )
        session.add(test_user)
        await session.commit()
        await session.refresh(test_user)

    response = await client.post(
        "/api/auth/token",
        data={
            "username": test_user.username,
            "password": plain_password,
            "grant_type": "password",
        },
        headers={
            "Authorization": f"Bearer token",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )

    if response.status_code != 200:
        raise Exception(f"Auth failed: {response.status_code} - {response.text}")

    return response.json()["access_token"]
