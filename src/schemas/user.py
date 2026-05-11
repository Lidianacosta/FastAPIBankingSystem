"""User Pydantic schemas.

Defines the data validation schemas for user input, output, and
database representation.
"""

from pydantic import BaseModel


class User(BaseModel):
    """Base User schema.

    Contains common public fields for user representation.

    Attributes:
        username: Unique login identifier.
        email: Optional contact email address.
        full_name: Optional real name of the user.
        disabled: Flag indicating if the user is suspended from logging in.
        is_demo: Flag indicating if the user is a demonstration account.

    """

    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None
    is_demo: bool = False


class UserDB(User):
    """Database representation of a User.

    Extends the base User schema by including the internal database ID
    and the confidential hashed password.

    Attributes:
        id: The database primary key constraint for the user.
        hashed_password: Argon2 generated hash for password verification.

    """

    id: int
    hashed_password: str


class UserIn(User):
    """User input schema for creation.

    Used when validating requests to create a new user. Extends the base
    User schema to require a plain text password.

    Attributes:
        plain_password: The raw password provided by the user, which will be hashed later.

    """

    plain_password: str


class UserUpdateIn(BaseModel):
    """User input schema for partial updates.

    All fields are optional, allowing PATCH requests to update only
    the provided attributes.

    Attributes:
        email: New optional contact email address.
        full_name: New optional real name of the user.
        disabled: New flag indicating if the user is suspended.
        plain_password: New optional raw password to replace the current one.

    """

    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None
    plain_password: str | None = None
