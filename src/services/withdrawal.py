"""Withdrawal transaction service layer.

Provides business logic for processing and reversing withdrawal operations,
validating account limits, bounds, and sufficient balances.
"""

from datetime import datetime, timedelta
from typing import Annotated

from fastapi import Depends, HTTPException
from sqlmodel import col, select

from src.models.account import Account, CheckingAccount
from src.models.transaction import Transaction
from src.schemas.transaction import WithdrawalIn
from src.utils.database import AsyncSessionDep


class WithdrawalService:
    """Service class for Withdrawal management.

    Handles creation, listing, retrieval, and deletion of withdrawal
    transactions. Validates business rules, such as overdraft limits
    and daily withdrawal count limits, adjusting balances upon success.

    Attributes:
        session: The asynchronous database session.
    """

    def __init__(self, session: AsyncSessionDep) -> None:
        self.session = session

    async def create(
        self, transaction_in: WithdrawalIn, account_id: int
    ) -> Transaction:
        """Process a new withdrawal transaction for an account.

        Ensures the withdrawal does not exceed available balance (plus limits)
        and respects the daily transaction limit for withdrawals. Decreases
        the parent `Account` balance upon successful validation.

        Args:
            transaction_in: Withdrawal schema containing the value.
            account_id: ID of the checking account from which to withdraw.

        Returns:
            The recorded transaction instance.

        Raises:
            HTTPException: 404 if account not found.
            HTTPException: 400 if insufficient funds or limits reached.
        """
        checking = await self.__get_checking_by_id(account_id)

        account = await self.session.get(Account, checking.account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")

        balance = account.balance or 0
        limit = checking.limit or 0
        available = balance + limit

        if transaction_in.value > available:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient funds. Available: {available}",
            )

        today_start = datetime.today().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        today_end = today_start + timedelta(days=1)

        statement = (
            select(Transaction)
            .where(col(Transaction.account_id) == checking.account_id)
            .where(col(Transaction.type) == "withdrawal")
            .where(Transaction.created_at >= today_start)
            .where(Transaction.created_at < today_end)
        )
        result = await self.session.exec(statement)
        withdrawal_count = len(result.all())

        if (
            checking.withdrawal_limit
            and withdrawal_count >= checking.withdrawal_limit
        ):
            raise HTTPException(
                status_code=400,
                detail=f"Daily withdrawal limit of {checking.withdrawal_limit} reached",
            )

        account.balance = balance - transaction_in.value
        self.session.add(account)

        transaction = Transaction(
            value=transaction_in.value,
            account_id=checking.account_id,
            type="withdrawal",
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
        """List all withdrawal transactions associated with an account.

        Args:
            account_id: The ID of the checking account.
            offset: The number of records to skip.
            limit: The maximum number of records to return.

        Returns:
            A list of withdrawal transaction model instances.
        """
        checking = await self.__get_checking_by_id(account_id)
        statement = (
            select(Transaction)
            .where(col(Transaction.type) == "withdrawal")
            .where(col(Transaction.account_id) == checking.account_id)
            .offset(offset)
            .limit(limit)
        )
        transactions = await self.session.exec(statement)
        return list(transactions.all())

    async def read(self, transaction_id: int, account_id: int) -> Transaction:
        """Retrieve a specific withdrawal transaction by ID.

        Enforces that the transaction matches the requested account.

        Args:
            transaction_id: The ID of the withdrawal transaction.
            account_id: The ID of the checking account for ownership validation.

        Returns:
            The withdrawal transaction instance.

        Raises:
            HTTPException: 404 if not found, 403 if ownership validation fails.
        """
        transaction = await self.__get_by_id(transaction_id)
        await self.__verify_ownership(transaction, account_id)
        return transaction

    async def delete(self, transaction_id: int, account_id: int) -> None:
        """Delete a withdrawal transaction and revert its balance impact.

        Restores the deducted balance to the underlying parent account
        before safely removing the transaction record.

        Args:
            transaction_id: The ID of the withdrawal transaction to delete.
            account_id: The ID of the associated checking account.

        Raises:
            HTTPException: 404 if not found, 403 if ownership validation fails.
        """
        transaction = await self.__get_by_id(transaction_id)
        await self.__verify_ownership(transaction, account_id)
        checking = await self.__get_checking_by_id(account_id)
        account = await self.session.get(Account, checking.account_id)
        if account:
            account.balance = (account.balance or 0.0) + (
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
        if not transaction or transaction.type != "withdrawal":
            raise HTTPException(status_code=404, detail="Withdrawal not found")
        return transaction


WithdrawalServiceDep = Annotated[WithdrawalService, Depends(WithdrawalService)]
