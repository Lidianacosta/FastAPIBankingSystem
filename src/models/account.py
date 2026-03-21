from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from src.models.base import Base

if TYPE_CHECKING:
    from src.models.client import Client
    from src.models.transaction import Transaction


class Account(Base, table=True):
    balance: float | None = None
    number: int | None = None
    branch: str | None = None
    type: str = Field(default="account")
    client_id: int | None = Field(default=None, foreign_key="client.id")
    client: "Client" = Relationship(back_populates="accounts")
    transactions: list["Transaction"] = Relationship(back_populates="account")


class CheckingAccount(Base, table=True):
    limit: float | None = None
    withdrawal_limit: int | None = None
    account_id: int | None = Field(default=None, foreign_key="account.id")
    account: Account = Relationship()
