from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from src.models.base import Base

if TYPE_CHECKING:
    from src.models.account import Account


class Transaction(Base, table=True):
    value: float | None = None
    type: str = Field(default="transaction")
    account_id: int | None = Field(default=None, foreign_key="account.id")
    account: "Account" = Relationship(back_populates="transactions")
