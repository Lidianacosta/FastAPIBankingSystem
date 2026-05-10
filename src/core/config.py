"""Application configuration module.

Defines Pydantic settings used to configure the FastAPI application,
including database URLs, environment contexts, and security keys.
"""

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings schema.

    Loads values from the `.env` file first, falling back to defaults.

    Attributes:
        database_url: Connection string for the database.
        environment: Current deployment context (e.g., 'production', 'development').
        secret_key: Secret key used to sign JWT tokens.
        algorithm: Algorithm used for JWT encoding/decoding.
        access_token_expire_minutes: Expiration time for access tokens.

    """

    database_url: str = Field(default="sqlite+aiosqlite:///db.sqlite")

    @field_validator("database_url", mode="before")
    @classmethod
    def assemble_db_url(cls, v: str) -> str:
        """Fix postgres scheme for SQLAlchemy compatibility."""
        if v:
            if v.startswith("postgres://"):
                return v.replace("postgres://", "postgresql+asyncpg://", 1)
            if v.startswith("postgresql://") and "+asyncpg" not in v:
                return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v

    environment: str = Field(default="production")

    secret_key: str = Field(
        default=(
            "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
        )
    )
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30)

    first_superuser_username: str | None = Field(default=None)
    first_superuser_password: str | None = Field(default=None)

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
