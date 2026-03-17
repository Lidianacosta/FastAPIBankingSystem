from typing import Annotated, Sequence

from fastapi import Depends, HTTPException
from sqlmodel import select

from src.models.transaction import Withdrawal
from src.utils.database import AsyncSessionDep


class WithdrawalService:
    def __init__(self, session: AsyncSessionDep) -> None:
        self.session = session

    async def create(self, transaction: Withdrawal) -> Withdrawal:
        self.session.add(transaction)
        await self.session.commit()
        await self.session.refresh(transaction)
        return transaction

    async def read_all(
        self,
        offset: int = 0,
        limit: int = 100,
    ) -> Sequence[Withdrawal]:
        statement = select(Withdrawal).offset(offset).limit(limit)
        accounts = await self.session.exec(statement)
        return accounts.all()

    async def read(self, id: int) -> Withdrawal:
        transaction = await self.__get_by_id(id)
        return transaction

    async def delete(self, id: int) -> None:
        transaction = await self.__get_by_id(id)
        await self.session.delete(transaction)
        await self.session.commit()

    async def __get_by_id(self, id):
        transaction = await self.session.get(Withdrawal, id)
        if not transaction:
            raise HTTPException(status_code=404, detail="Withdrawal not found")
        return transaction


WithdrawalServiceDep = Annotated[WithdrawalService, Depends(WithdrawalService)]
