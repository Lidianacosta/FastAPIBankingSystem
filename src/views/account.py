"""Account response models.

Defines the Pydantic schemas for account data returned by the API.
"""

from datetime import datetime

from pydantic import BaseModel


class CheckingAccountOut(BaseModel):
    """Checking Account output schema.

    Attributes:
        id: The unique identifier of the checking account.
        limit: The overdraft limit for the account.
        withdrawal_limit: The daily withdrawal count limit.
        account_id: The ID of the base account record.
        created_at: The timestamp when the account was created.
        balance: The current monetary balance.
        number: The account number.
        branch: The branch code.

    """

    id: int
    limit: float
    withdrawal_limit: int
    account_id: int
    created_at: datetime
    balance: float | None = None
    number: int | None = None
    branch: str | None = None
