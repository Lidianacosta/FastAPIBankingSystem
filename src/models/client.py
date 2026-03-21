from datetime import date
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from src.models.base import Base

if TYPE_CHECKING:
    from src.models.account import Account


class Client(Base, table=True):
    address: str | None = None
    type: str = Field(default="individual")
    accounts: list["Account"] = Relationship(back_populates="client")


class IndividualClient(Base, table=True):
    name: str | None = None
    cpf: str | None = None
    date_of_birth: date | None = None
    client_id: int | None = Field(default=None, foreign_key="client.id")
    client: Client = Relationship()
