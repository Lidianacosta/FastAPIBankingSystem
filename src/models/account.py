from sqlmodel import Relationship, SQLModel

from src.models.base import Base
from src.models.client import Client
from src.models.transaction import Transaction


class Account(SQLModel):
    balance: float
    number: int
    branch: str
    client: Client = Relationship(back_populates="accounts")
    transactions: list["Transaction"] = Relationship(back_populates="account")


class CheckingAccount(Base, Account, table=True):
    limit: float
    withdrawal_limit: int
