"""Bank account database models.

Includes the base `Account` model and the specialized `CheckingAccount` model.
"""

from sqlmodel import Field

from src.models.base import Base


class Account(Base, table=True):
    """Base Account database model.

    Represents a generic bank account assigned to a client.

    Attributes:
        balance: Current monetary balance of the account.
        number: Unique account number identifier.
        branch: Branch code where the account is registered.
        type: The specific type of account (e.g., 'account', 'checking').
        client_id: Foreign key linking to the Client who owns this account.

    """

    balance: float | None = None
    number: int | None = None
    branch: str | None = None
    type: str = Field(default="account")
    client_id: int | None = Field(default=None, foreign_key="client.id")


class CheckingAccount(Base, table=True):
    """Checking Account database model.

    A specific type of account with specialized limits for transactions.
    It maps to a base `Account` record via `account_id`.

    Attributes:
        limit: Overdraft limit allowed for the checking account.
        withdrawal_limit: Maximum number of withdrawals permitted per day/period.
        daily_withdrawal_limit: Maximum total value of withdrawals permitted per day.
        account_id: Foreign key linking to the base Account record.

    """

    limit: float | None = None
    withdrawal_limit: int | None = None
    daily_withdrawal_limit: float | None = None
    account_id: int | None = Field(default=None, foreign_key="account.id")
