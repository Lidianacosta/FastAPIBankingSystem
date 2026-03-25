"""Client Pydantic schemas.

Defines the data validation schemas for client creation and updates.
"""

from datetime import date

from pydantic import BaseModel


class ClientIn(BaseModel):
    """Base Client input schema for creation.

    Attributes:
        address: Physical or mailing address of the client.
    """

    address: str


class IndividualClientIn(ClientIn):
    """Individual Client input schema for creation.

    Extends the base Client schema to include personal information.

    Attributes:
        name: Full name of the individual.
        cpf: Brazilian natural person registry number (Cadastro de Pessoas Físicas).
        date_of_birth: Birthdate of the individual.
    """

    name: str
    cpf: str
    date_of_birth: date


class ClientUpdateIn(BaseModel):
    """Base Client input schema for partial updates.

    Attributes:
        address: New physical or mailing address of the client.
    """

    address: str | None = None


class IndividualClientUpdateIn(ClientUpdateIn):
    """Individual Client input schema for partial updates.

    All fields are optional, allowing PATCH requests to update only
    the provided attributes.

    Attributes:
        name: New full name of the individual.
        cpf: New Brazilian natural person registry number.
        date_of_birth: New birthdate of the individual.
    """

    name: str | None = None
    cpf: str | None = None
    date_of_birth: date | None = None
