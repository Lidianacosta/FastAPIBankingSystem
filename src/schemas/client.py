from pydantic import AwareDatetime, BaseModel


class ClientIn(BaseModel):
    address: str


class IndividualClientIn(ClientIn):
    name: str
    cpf: str
    date_of_birth: AwareDatetime


class ClientUpdateIn(BaseModel):
    address: str | None


class IndividualClientUpdateIn(ClientUpdateIn):
    name: str | None
    cpf: str | None
    date_of_birth: AwareDatetime | None
