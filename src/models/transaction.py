from sqlmodel import Relationship, SQLModel

from src.models.account import Account
from src.models.base import Base


class Transaction(SQLModel):
    value: float
    account: Account = Relationship(back_populates="transactions")


class Deposit(Base, Transaction, table=True):
    pass


class Withdrawal(Base, Transaction, table=True):
    pass
