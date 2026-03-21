from pydantic import BaseModel


class DepositIn(BaseModel):
    value: float


class WithdrawalIn(BaseModel):
    value: float
