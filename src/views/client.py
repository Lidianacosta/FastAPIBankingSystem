from datetime import date

from pydantic import BaseModel


class IndividualClientOut(BaseModel):
    id: int
    name: str
    cpf: str
    date_of_birth: date
    address: str
