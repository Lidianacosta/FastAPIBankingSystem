"""Database initialization script.

Checks if an initial superuser and a demo user should be created.
"""

import asyncio
import logging

from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.config import settings
from src.models.user import User
from src.schemas.user import UserIn
from src.utils.password import get_password_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_user_if_not_exists(
    session: AsyncSession,
    username: str,
    password: str,
    is_demo: bool = False,
    description: str = "user",
) -> None:
    """Create a user if they don't already exist in the database."""
    statement = select(User).where(User.username == username)
    result = await session.exec(statement)
    user = result.first()

    if user:
        logger.info("%s '%s' already exists. Skipping.", description, username)
    else:
        logger.info("Creating %s '%s'.", description, username)
        user_in = UserIn(
            username=username,
            plain_password=password,
            is_demo=is_demo,
        )
        new_user = User(**user_in.model_dump(exclude={"plain_password"}))
        new_user.hashed_password = get_password_hash(user_in.plain_password)
        session.add(new_user)
        await session.commit()
        logger.info("%s '%s' created successfully.", description, username)


async def init_db() -> None:
    """Initialize the database with default users."""
    engine = create_async_engine(settings.database_url)

    async with AsyncSession(engine) as session:
        if (
            settings.first_superuser_username
            and settings.first_superuser_password
        ):
            await create_user_if_not_exists(
                session,
                settings.first_superuser_username,
                settings.first_superuser_password,
                is_demo=False,
                description="Superuser",
            )

        if settings.demo_user_username and settings.demo_user_password:
            await create_user_if_not_exists(
                session,
                settings.demo_user_username,
                settings.demo_user_password,
                is_demo=True,
                description="Demo user",
            )

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_db())
