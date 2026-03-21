from pydantic import BaseModel


class CheckingAccountIn(BaseModel):
    balance: float
    number: int
    branch: str
    limit: float
    withdrawal_limit: int


class CheckingAccountUpdateIn(BaseModel):
    balance: float | None = None
    number: int | None = None
    branch: str | None = None
    limit: float | None = None
    withdrawal_limit: int | None = None
