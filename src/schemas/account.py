"""Account Pydantic schemas.

Defines the data validation schemas for account creation and updates.
"""

from pydantic import BaseModel


class CheckingAccountIn(BaseModel):
    """Checking Account input schema for creation.

    Used when validating requests to open a new checking account.

    Attributes:
        balance: Initial monetary balance of the account.
        limit: Overdraft limit allowed for the checking account.
        withdrawal_limit: Maximum number of withdrawals permitted.
        daily_withdrawal_limit: Maximum total value of withdrawals permitted per day.

    """

    balance: float
    limit: float
    withdrawal_limit: int
    daily_withdrawal_limit: float


class CheckingAccountUpdateIn(BaseModel):
    """Checking Account input schema for partial updates.

    All fields are optional, allowing PATCH requests to update only
    the provided attributes.

    Attributes:
        balance: New monetary balance of the account.
        limit: New overdraft limit allowed.
        withdrawal_limit: New maximum number of withdrawals permitted.
        daily_withdrawal_limit: New maximum total value of withdrawals permitted per day.

    """

    balance: float | None = None
    limit: float | None = None
    withdrawal_limit: int | None = None
    daily_withdrawal_limit: float | None = None
