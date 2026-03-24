from src.models.base import Base


class User(Base, table=True):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None
    hashed_password: str
