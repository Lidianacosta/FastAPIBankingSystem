"""Account Pydantic schemas.

Defines the data validation schemas for account creation and updates.
"""

from pydantic import BaseModel


class CheckingAccountIn(BaseModel):
    """Checking Account input schema for creation.

    Used when validating requests to open a new checking account.

    Attributes:
        balance: Initial monetary balance of the account.
        number: Unique account number.
        branch: Branch code.
        limit: Overdraft limit allowed for the checking account.
        withdrawal_limit: Maximum number of withdrawals permitted.
    """

    balance: float
    number: int
    branch: str
    limit: float
    withdrawal_limit: int


class CheckingAccountUpdateIn(BaseModel):
    """Checking Account input schema for partial updates.

    All fields are optional, allowing PATCH requests to update only
    the provided attributes.

    Attributes:
        balance: New monetary balance of the account.
        number: New unique account number.
        branch: New branch code.
        limit: New overdraft limit allowed.
        withdrawal_limit: New maximum number of withdrawals permitted.
    """

    balance: float | None = None
    number: int | None = None
    branch: str | None = None
    limit: float | None = None
    withdrawal_limit: int | None = None
