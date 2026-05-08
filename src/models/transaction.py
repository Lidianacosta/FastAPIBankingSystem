"""Transaction database models.

Includes the `Transaction` model used for deposits, withdrawals, and other operations.
"""

from sqlmodel import Field

from src.models.base import Base


class Transaction(Base, table=True):
    """Financial Transaction database model.

    Records monetary movements such as deposits and withdrawals.

    Attributes:
        value: Monetary value of the transaction.
        type: String identifier of the transaction type ('deposit', 'withdrawal', etc).
        account_id: Foreign key linking to the Account that owns the transaction.

    """

    value: float | None = None
    type: str = Field(default="transaction")
    account_id: int | None = Field(default=None, foreign_key="account.id")
