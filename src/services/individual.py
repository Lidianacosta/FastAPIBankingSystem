from typing import Annotated, Sequence

from fastapi import Depends, HTTPException
from sqlmodel import select

from src.models.client import Individual
from src.schemas.client import IndividualIn
from src.utils.database import AsyncSessionDep


class IndividualService:
    def __init__(self, session: AsyncSessionDep) -> None:
        self.session = session

    async def create(self, client: Individual) -> Individual:
        self.session.add(client)
        await self.session.commit()
        await self.session.refresh(client)
        return client

    async def read_all(
        self,
        offset: int = 0,
        limit: int = 100,
    ) -> Sequence[Individual]:
        statement = select(Individual).offset(offset).limit(limit)
        accounts = await self.session.exec(statement)
        return accounts.all()

    async def read(self, id: int) -> Individual:
        client = await self.__get_by_id(id)
        return client

    async def update(self, id: int, client: IndividualIn) -> Individual:
        db_account = await self.__get_by_id(id)
        data = client.model_dump(exclude_unset=True)

        for attr, value in data.items():
            setattr(db_account, attr, value)

        self.session.add(db_account)
        await self.session.commit()
        await self.session.refresh(db_account)
        return db_account

    async def delete(self, id: int) -> None:
        client = await self.__get_by_id(id)
        await self.session.delete(client)
        await self.session.commit()

    async def __get_by_id(self, id):
        client = await self.session.get(Individual, id)
        if not client:
            raise HTTPException(status_code=404, detail="Individual not found")
        return client


CheckingAccountServiceDep = Annotated[
    IndividualService, Depends(IndividualService)
]
