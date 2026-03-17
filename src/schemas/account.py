from pydantic import BaseModel


class AccountIn(BaseModel):
    balance: float
    number: int
    branch: str
    client_id: int


class CheckingAccountIn(AccountIn):
    limit: float
    withdrawal_limit: int


class AccountUpdateIn(BaseModel):
    balance: float | None
    number: int | None
    branch: str | None


class CheckingAccountUpdateIn(AccountUpdateIn):
    limit: float | None
    withdrawal_limit: int | None
