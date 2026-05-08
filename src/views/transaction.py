"""Transaction response models.

Defines the Pydantic schemas for transaction data returned by the API.
"""

from datetime import datetime

from pydantic import BaseModel


class TransactionOut(BaseModel):
    """Base transaction output schema.

    Attributes:
        id: The unique identifier of the transaction.
        value: The monetary value of the transaction.
        type: The type of transaction (e.g., 'deposit', 'withdrawal').
        account_id: The ID of the associated account.
        created_at: The timestamp when the transaction occurred.

    """

    id: int
    value: float
    type: str
    account_id: int
    created_at: datetime


class DepositOut(TransactionOut):
    """Deposit transaction output schema."""

    pass


class WithdrawalOut(TransactionOut):
    """Withdrawal transaction output schema."""

    pass
