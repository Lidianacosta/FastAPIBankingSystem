from typing import Annotated

from fastapi import Depends, HTTPException
from sqlmodel import col, select

from src.models.account import Account, CheckingAccount
from src.models.transaction import Transaction
from src.schemas.transaction import DepositIn
from src.utils.database import AsyncSessionDep


class DepositService:
    def __init__(self, session: AsyncSessionDep) -> None:
        self.session = session

    async def create(
        self, transaction_in: DepositIn, account_id: int
    ) -> Transaction:
        checking = await self.__get_checking_by_id(account_id)

        account = await self.session.get(Account, checking.account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")

        account.balance = (account.balance or 0) + transaction_in.value
        self.session.add(account)

        transaction = Transaction(
            value=transaction_in.value,
            account_id=checking.account_id,
            type="deposit",
        )
        self.session.add(transaction)
        await self.session.commit()
        await self.session.refresh(transaction)
        return transaction

    async def read_all(
        self,
        account_id: int,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Transaction]:
        checking = await self.__get_checking_by_id(account_id)
        statement = (
            select(Transaction)
            .where(col(Transaction.type) == "deposit")
            .where(col(Transaction.account_id) == checking.account_id)
            .offset(offset)
            .limit(limit)
        )
        transactions = await self.session.exec(statement)
        return list(transactions.all())

    async def read(self, transaction_id: int, account_id: int) -> Transaction:
        transaction = await self.__get_by_id(transaction_id)
        await self.__verify_ownership(transaction, account_id)
        return transaction

    async def delete(self, transaction_id: int, account_id: int) -> None:
        transaction = await self.__get_by_id(transaction_id)
        await self.__verify_ownership(transaction, account_id)
        checking = await self.__get_checking_by_id(account_id)
        account = await self.session.get(Account, checking.account_id)
        if account:
            account.balance = (account.balance or 0.0) - (
                transaction.value or 0.0
            )
            self.session.add(account)
        await self.session.delete(transaction)
        await self.session.commit()

    async def __verify_ownership(
        self, transaction: Transaction, account_id: int
    ) -> None:
        checking = await self.__get_checking_by_id(account_id)
        if transaction.account_id != checking.account_id:
            raise HTTPException(
                status_code=403,
                detail="This transaction does not belong to this account",
            )

    async def __get_checking_by_id(self, account_id: int) -> CheckingAccount:
        checking = await self.session.get(CheckingAccount, account_id)
        if not checking:
            raise HTTPException(
                status_code=404, detail="Checking account not found"
            )
        return checking

    async def __get_by_id(self, transaction_id: int) -> Transaction:
        transaction = await self.session.get(Transaction, transaction_id)
        if not transaction or transaction.type != "deposit":
            raise HTTPException(status_code=404, detail="Deposit not found")
        return transaction


DepositServiceDep = Annotated[DepositService, Depends(DepositService)]
