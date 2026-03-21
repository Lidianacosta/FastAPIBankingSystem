from sqlmodel import Field

from src.models.base import Base


class Account(Base, table=True):
    balance: float | None = None
    number: int | None = None
    branch: str | None = None
    type: str = Field(default="account")
    client_id: int | None = Field(default=None, foreign_key="client.id")


class CheckingAccount(Base, table=True):
    limit: float | None = None
    withdrawal_limit: int | None = None
    account_id: int | None = Field(default=None, foreign_key="account.id")
