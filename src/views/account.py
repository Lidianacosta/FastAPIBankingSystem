from datetime import datetime

from pydantic import BaseModel


class CheckingAccountOut(BaseModel):
    id: int
    limit: float
    withdrawal_limit: int
    account_id: int
    created_at: datetime
    balance: float | None = None
    number: int | None = None
    branch: str | None = None
