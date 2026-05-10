"""Database initialization script.

Checks if an initial superuser should be created and creates it if needed.
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


async def init_db() -> None:
    """Create the initial superuser if configured."""
    if (
        not settings.first_superuser_username
        or not settings.first_superuser_password
    ):
        logger.info(
            "First superuser credentials not configured. Skipping initialization."
        )
        return

    engine = create_async_engine(settings.database_url)

    async with AsyncSession(engine) as session:
        statement = select(User).where(
            User.username == settings.first_superuser_username
        )
        result = await session.exec(statement)
        user = result.first()

        if user:
            logger.info("Superuser already exists. Skipping creation.")
        else:
            logger.info("Creating initial superuser.")
            user_in = UserIn(
                username=settings.first_superuser_username,
                plain_password=settings.first_superuser_password,
            )
            new_user = User(**user_in.model_dump(exclude={"plain_password"}))
            new_user.hashed_password = get_password_hash(
                user_in.plain_password
            )
            session.add(new_user)
            await session.commit()
            logger.info("Initial superuser created successfully.")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_db())
