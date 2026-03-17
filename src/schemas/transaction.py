from pydantic import BaseModel


class TransactionIn(BaseModel):
    value: float
    account_id: int


class DepositIn(TransactionIn):
    pass


class WithdrawalIn(TransactionIn):
    pass
