from datetime import date

from sqlmodel import Relationship, SQLModel

from src.models.account import Account
from src.models.base import Base


class Client(SQLModel):
    address: str
    accounts: list["Account"] = Relationship(back_populates="client")


class Individual(Base, Client, table=True):
    name: str
    cpf: str
    date_of_birth: date
