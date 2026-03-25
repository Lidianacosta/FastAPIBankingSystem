"""Client database models.

Includes the base `Client` model and the specialized `IndividualClient` model.
"""

from datetime import date

from sqlmodel import Field

from src.models.base import Base


class Client(Base, table=True):
    """Base Client database model.

    Represents a generic bank client entity.

    Attributes:
        address: Physical or mailing address of the client.
        type: The specific type of client (e.g., 'individual', 'corporate').
    """

    address: str | None = None
    type: str = Field(default="individual")


class IndividualClient(Base, table=True):
    """Individual Client database model.

    Represents a natural person client. It maps to a base `Client`
    record via `client_id`.

    Attributes:
        name: Full name of the individual.
        cpf: Brazilian natural person registry number (Cadastro de Pessoas Físicas).
        date_of_birth: Birthdate of the individual.
        client_id: Foreign key linking to the base Client record.
    """

    name: str | None = None
    cpf: str | None = None
    date_of_birth: date | None = None
    client_id: int | None = Field(default=None, foreign_key="client.id")
