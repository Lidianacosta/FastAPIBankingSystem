from datetime import datetime

from sqlmodel import Field, SQLModel


class Base(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default=datetime.today)
