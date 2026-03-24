from datetime import datetime

from pydantic import BaseModel


class DepositOut(BaseModel):
    id: int
    value: float
    type: str
    created_at: datetime


class WithdrawalOut(BaseModel):
    id: int
    value: float
    type: str
    created_at: datetime
