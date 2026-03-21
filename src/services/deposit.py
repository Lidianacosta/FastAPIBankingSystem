from typing import Annotated

from fastapi import Depends, HTTPException
from sqlmodel import select

from src.models.transaction import Transaction
from src.schemas.transaction import DepositIn
from src.utils.database import AsyncSessionDep


class DepositService:
    def __init__(self, session: AsyncSessionDep) -> None:
        self.session = session

    async def create(self, transaction_in: DepositIn) -> Transaction:
        transaction = Transaction(
            **transaction_in.model_dump(), type="deposit"
        )
        self.session.add(transaction)
        await self.session.commit()
        await self.session.refresh(transaction)

        return transaction

    async def read_all(
        self,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Transaction]:
        statement = (
            select(Transaction)
            .where(Transaction.type == "deposit")
            .offset(offset)
            .limit(limit)
        )
        transactions = await self.session.exec(statement)
        return list(transactions.all())

    async def read(self, transaction_id: int) -> Transaction:
        return await self.__get_by_id(transaction_id)

    async def delete(self, transaction_id: int) -> None:
        transaction = await self.__get_by_id(transaction_id)
        await self.session.delete(transaction)
        await self.session.commit()

    async def __get_by_id(self, transaction_id) -> Transaction:
        transaction = await self.session.get(Transaction, transaction_id)
        if not transaction:
            raise HTTPException(status_code=404, detail="Deposit not found")
        return transaction


DepositServiceDep = Annotated[DepositService, Depends(DepositService)]
