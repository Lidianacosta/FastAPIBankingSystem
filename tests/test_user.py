from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.models.user import User
from src.utils.database import async_engine


async def test_get_curruent_user(client, access_token):
    response = await client.get(
        "/api/users/me/",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "test_user"


async def test_database_isolation(db):
    async with AsyncSession(async_engine) as session:
        result = await session.exec(select(User))
        users = result.all()
        assert len(users) == 0
