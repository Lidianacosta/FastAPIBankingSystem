from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = Field(default="sqlite+aiosqlite:///db.sqlite")

    environment: str = Field(default="production")

    model_config = SettingsConfigDict(env_prefix=".env")


settings = Settings()
