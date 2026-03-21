from datetime import date

from sqlmodel import Field

from src.models.base import Base


class Client(Base, table=True):
    address: str | None = None
    type: str = Field(default="individual")


class IndividualClient(Base, table=True):
    name: str | None = None
    cpf: str | None = None
    date_of_birth: date | None = None
    client_id: int | None = Field(default=None, foreign_key="client.id")
