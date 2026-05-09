"""Base model and database metadata configuration.

This module defines the SQLAlchemy MetaData with naming conventions
and the base SQLModel class from which all other models inherit.
"""

from datetime import UTC, datetime

from sqlmodel import Field, MetaData, SQLModel

naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

SQLModel.metadata = MetaData(naming_convention=naming_convention)


class Base(SQLModel):
    """Base SQLModel class for all database models.

    Provides common underlying fields for all tables, such as primary
    key and creation timestamp.

    Attributes:
        id: Primary key, auto-incremented integer. None before saving.
        created_at: Timestamp of when the record was created. Defaults to current UTC time.

    """

    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC).replace(tzinfo=None)
    )
