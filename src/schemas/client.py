from datetime import date

from pydantic import BaseModel


class ClientIn(BaseModel):
    address: str


class IndividualClientIn(ClientIn):
    name: str
    cpf: str
    date_of_birth: date


class ClientUpdateIn(BaseModel):
    address: str | None = None


class IndividualClientUpdateIn(ClientUpdateIn):
    name: str | None = None
    cpf: str | None = None
    date_of_birth: date | None = None
