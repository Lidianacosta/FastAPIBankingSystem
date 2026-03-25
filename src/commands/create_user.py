import asyncio

import typer
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.config import settings
from src.models.user import User
from src.schemas.user import UserIn
from src.utils.password import get_password_hash

app = typer.Typer()


async def _create_user(
    username: str, password: str, email: str | None, full_name: str | None
) -> None:
    engine = create_async_engine(settings.database_url)

    async with AsyncSession(engine) as session:
        existing = await session.exec(
            select(User).where(User.username == username)
        )
        if existing.first():
            typer.secho(f"Error: user '{username}' already exists.", fg=typer.colors.RED, bold=True, err=True)
            raise typer.Exit(code=1)

        user_in = UserIn(
            username=username,
            plain_password=password,
            email=email,
            full_name=full_name,
        )
        user = User(**user_in.model_dump(exclude={"plain_password"}))

        if len(password) < 8:
            typer.secho(
                "Warning: password is shorter than 8 characters.",
                fg=typer.colors.YELLOW,
                bold=True,
            )

        user.hashed_password = get_password_hash(user_in.plain_password)

        session.add(user)
        await session.commit()
        await session.refresh(user)

    await engine.dispose()
    typer.secho(f"User '{user.username}' created successfully.", fg=typer.colors.GREEN, bold=True)


@app.command()
def create_user(
    username: str = typer.Option(..., prompt=True, help="Username for login"),
    password: str = typer.Option(
        ...,
        prompt=True,
        hide_input=True,
        confirmation_prompt=True,
        help="User password",
    ),
    email: str | None = typer.Option(None, help="User email address"),
    full_name: str | None = typer.Option(None, help="User full name"),
) -> None:
    """Create a new user account in the database."""
    asyncio.run(_create_user(username, password, email, full_name))


if __name__ == "__main__":
    app()
