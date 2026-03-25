"""User authentication and database models.

Includes the `User` model used for the application's authentication system.
"""

from src.models.base import Base


class User(Base, table=True):
    """User database model for authentication.

    Represents a system user capable of logging in via OAuth2 credentials.

    Attributes:
        username: Unique login identifier.
        email: Optional contact email address.
        full_name: Optional real name of the user.
        disabled: Flag indicating if the user is suspended from logging in.
        hashed_password: Argon2 generated hash for password verification.
    """

    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None
    hashed_password: str
