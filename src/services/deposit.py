"""Deposit transaction service layer.

Provides business logic for processing and reversing deposit operations
on checking accounts.
"""

from typing import Annotated

from fastapi import Depends, HTTPException
from sqlmodel import col, select

from src.models.account import Account, CheckingAccount
from src.models.transaction import Transaction
from src.schemas.transaction import DepositIn
from src.utils.database import AsyncSessionDep


class DepositService:
    """Service class for Deposit management.

    Handles creation, listing, retrieval, and deletion of deposit transactions,
    automatically adjusting the base account balance.

    Attributes:
        session: The asynchronous database session.
    """

    def __init__(self, session: AsyncSessionDep) -> None:
        """Initialize the deposit service.

        Args:
            session: The asynchronous database session.
        """
        self.session = session

    async def create(
        self, transaction_in: DepositIn, account_id: int
    ) -> Transaction:
        """Process a new deposit transaction for an account.

        Increments the parent `Account` balance by the transaction value
        and records the `Transaction`.

        Args:
            transaction_in: Deposit schema containing the value.
            account_id: ID of the checking account receiving the deposit.

        Returns:
            The recorded transaction instance.

        Raises:
            HTTPException: 404 if the account is not found.
        """
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
        """List all deposit transactions associated with an account.

        Args:
            account_id: The ID of the checking account.
            offset: The number of records to skip.
            limit: The maximum number of records to return.

        Returns:
            A list of deposit transaction model instances.
        """
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
        """Retrieve a specific deposit transaction by ID.

        Enforces that the transaction matches the requested account.

        Args:
            transaction_id: The ID of the deposit transaction.
            account_id: The ID of the checking account for ownership validation.

        Returns:
            The deposit transaction instance.

        Raises:
            HTTPException: 404 if not found, 403 if ownership validation fails.
        """
        transaction = await self.__get_by_id(transaction_id)
        await self.__verify_ownership(transaction, account_id)
        return transaction

    async def delete(self, transaction_id: int, account_id: int) -> None:
        """Delete a deposit transaction and revert its balance impact.

        Decreases the balance on the underlying parent account by the
        deposited value before safely removing the transaction record.

        Args:
            transaction_id: The ID of the deposit transaction to delete.
            account_id: The ID of the associated checking account.

        Raises:
            HTTPException: 404 if not found, 403 if ownership validation fails.
        """
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
        """Verify that a transaction belongs to a specific account.

        Args:
            transaction: The transaction model instance.
            account_id: The ID of the checking account to verify against.

        Raises:
            HTTPException: 403 if the transaction does not belong to the account.
        """
        checking = await self.__get_checking_by_id(account_id)
        if transaction.account_id != checking.account_id:
            raise HTTPException(
                status_code=403,
                detail="This transaction does not belong to this account",
            )

    async def __get_checking_by_id(self, account_id: int) -> CheckingAccount:
        """Internal helper to retrieve a checking account by ID.

        Args:
            account_id: The ID of the checking account to retrieve.

        Returns:
            The CheckingAccount model instance.

        Raises:
            HTTPException: 404 if the checking account is not found.
        """
        checking = await self.session.get(CheckingAccount, account_id)
        if not checking:
            raise HTTPException(
                status_code=404, detail="Checking account not found"
            )
        return checking

    async def __get_by_id(self, transaction_id: int) -> Transaction:
        """Internal helper to retrieve a deposit transaction by ID.

        Args:
            transaction_id: The ID of the transaction to retrieve.

        Returns:
            The Transaction model instance.

        Raises:
            HTTPException: 404 if the deposit is not found.
        """
        transaction = await self.session.get(Transaction, transaction_id)
        if not transaction or transaction.type != "deposit":
            raise HTTPException(status_code=404, detail="Deposit not found")
        return transaction


DepositServiceDep = Annotated[DepositService, Depends(DepositService)]
