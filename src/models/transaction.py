from sqlmodel import Field

from src.models.base import Base


class Transaction(Base, table=True):
    value: float | None = None
    type: str = Field(default="transaction")
    account_id: int | None = Field(default=None, foreign_key="account.id")
