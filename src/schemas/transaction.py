"""Transaction Pydantic schemas.

Defines the data validation schemas for financial transactions.
"""

from pydantic import BaseModel


class DepositIn(BaseModel):
    """Deposit input schema for creation.

    Attributes:
        value: Monetary value to be deposited. Must be positive.

    """

    value: float


class WithdrawalIn(BaseModel):
    """Withdrawal input schema for creation.

    Attributes:
        value: Monetary value to be withdrawn. Must be positive and
            not exceed the account balance or limits.

    """

    value: float
