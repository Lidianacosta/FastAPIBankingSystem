"""Client response models.

Defines the Pydantic schemas for client data returned by the API.
"""

from datetime import date

from pydantic import BaseModel


class IndividualClientOut(BaseModel):
    """Individual Client output schema.

    Attributes:
        id: The unique identifier of the individual client.
        name: The full name of the client.
        cpf: The Brazilian CPF registry number.
        date_of_birth: The client's birth date.
        address: The client's physical address.

    """

    id: int
    name: str
    cpf: str
    date_of_birth: date
    address: str
