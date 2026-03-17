from typing import Annotated, Sequence

from fastapi import Depends, HTTPException
from sqlmodel import select

from src.models.transaction import Deposit
from src.utils.database import AsyncSessionDep


class DepositService:
    def __init__(self, session: AsyncSessionDep) -> None:
        self.session = session

    async def create(self, transaction: Deposit) -> Deposit:
        self.session.add(transaction)
        await self.session.commit()
        await self.session.refresh(transaction)
        return transaction

    async def read_all(
        self,
        offset: int = 0,
        limit: int = 100,
    ) -> Sequence[Deposit]:
        statement = select(Deposit).offset(offset).limit(limit)
        accounts = await self.session.exec(statement)
        return accounts.all()

    async def read(self, id: int) -> Deposit:
        transaction = await self.__get_by_id(id)
        return transaction

    async def delete(self, id: int) -> None:
        transaction = await self.__get_by_id(id)
        await self.session.delete(transaction)
        await self.session.commit()

    async def __get_by_id(self, id):
        transaction = await self.session.get(Deposit, id)
        if not transaction:
            raise HTTPException(status_code=404, detail="Deposit not found")
        return transaction


DepositServiceDep = Annotated[DepositService, Depends(DepositService)]
