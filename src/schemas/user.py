from pydantic import BaseModel


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class UserDB(User):
    id: int
    hashed_password: str


class UserIn(User):
    plain_password: str


class UserUpdateIn(BaseModel):
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None
    plain_password: str | None
