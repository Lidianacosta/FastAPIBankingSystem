"""Checking Account service layer.

Provides business logic for creating and managing checking accounts,
safely handling the relationship between `Account` and `CheckingAccount`.
"""

from typing import Annotated

from fastapi import Depends, HTTPException
from sqlmodel import col, select

from src.models.account import Account, CheckingAccount
from src.models.client import Client
from src.models.transaction import Transaction
from src.schemas.account import CheckingAccountIn, CheckingAccountUpdateIn
from src.utils.database import AsyncSessionDep
from src.views.account import CheckingAccountOut


class CheckingAccountService:
    """Service class for Checking Account management.

    Handles creation, updates, and interactions with base `Account`
    records. Validates ownership of accounts.

    Attributes:
        session: The asynchronous database session.

    """

    def __init__(self, session: AsyncSessionDep) -> None:
        """Initialize the service with a database session.

        Args:
            session: The asynchronous database session.

        """
        self.session = session

    async def create(
        self, account_in: CheckingAccountIn, client_id: int
    ) -> CheckingAccountOut:
        """Create a new checking account.

        Creates the generic `Account` record first to establish balance and routing,
        then associates it with the `CheckingAccount` specific limits.

        Args:
            account_in: Schema with account creation details.
            client_id: The ID of the client owner.

        Returns:
            The newly created checking account representation.

        """
        client = await self.__get_client_by_id(client_id)

        account = Account(
            balance=account_in.balance,
            number=account_in.number,
            branch=account_in.branch,
            client_id=client.id,
            type="checking",
        )
        self.session.add(account)
        await self.session.flush([account])

        checking_account = CheckingAccount(
            limit=account_in.limit,
            withdrawal_limit=account_in.withdrawal_limit,
            account_id=account.id,
        )
        self.session.add(checking_account)
        await self.session.commit()
        await self.session.refresh(checking_account)
        return await self.__to_out(checking_account)

    async def read_all(
        self,
        client_id: int,
        offset: int = 0,
        limit: int = 100,
    ) -> list[CheckingAccountOut]:
        """List all checking accounts owned by a specific client.

        Args:
            client_id: The ID of the client owner.
            offset: The number of records to skip.
            limit: The maximum number of records to return.

        Returns:
            A list of checking accounts.

        """
        statement = (
            select(CheckingAccount)
            .join(Account, col(CheckingAccount.account_id) == col(Account.id))
            .where(col(Account.client_id) == client_id)
            .offset(offset)
            .limit(limit)
        )
        accounts = await self.session.exec(statement)
        return [await self.__to_out(c) for c in accounts.all()]

    async def read(
        self, account_id: int, client_id: int
    ) -> CheckingAccountOut:
        """Retrieve a specific checking account by ID.

        Enforces that the specified client is the owner of the account.

        Args:
            account_id: The ID of the checking account.
            client_id: The ID of the requesting client owner.

        Returns:
            The requested checking account representation.

        Raises:
            HTTPException: 404 if not found, 403 if ownership validation fails.

        """
        checking = await self.__get_by_id(account_id)
        await self.__verify_ownership(checking, client_id)
        return await self.__to_out(checking)

    async def update(
        self,
        account_id: int,
        checking_account_in: CheckingAccountUpdateIn,
        client_id: int,
    ) -> CheckingAccountOut:
        """Update an existing checking account.

        Updates both base `Account` (e.g., balance, branch) and
        `CheckingAccount` (e.g., limits) fields. Validates ownership.

        Args:
            account_id: The ID of the checking account to update.
            checking_account_in: Schema with optional update fields.
            client_id: The ID of the requesting client owner.

        Returns:
            The updated checking account.

        Raises:
            HTTPException: 404 if not found, 403 if ownership validation fails.

        """
        checking = await self.__get_by_id(account_id)
        await self.__verify_ownership(checking, client_id)

        data = checking_account_in.model_dump(exclude_unset=True)

        checking_fields = CheckingAccount.model_fields.keys()
        account_fields = Account.model_fields.keys()

        for attr, value in data.items():
            if attr in checking_fields:
                setattr(checking, attr, value)

        if checking.account_id:
            account = await self.session.get(Account, checking.account_id)
            if account:
                for attr, value in data.items():
                    if attr in account_fields:
                        setattr(account, attr, value)
                self.session.add(account)

        self.session.add(checking)
        await self.session.commit()
        await self.session.refresh(checking)
        return await self.__to_out(checking)

    async def delete(self, account_id: int, client_id: int) -> None:
        """Delete a checking account, its parent account, and all associated transactions.

        Args:
            account_id: The ID of the checking account to delete.
            client_id: The ID of the requesting client owner.

        Raises:
            HTTPException: 404 if not found, 403 if ownership validation fails.

        """
        checking = await self.__get_by_id(account_id)
        await self.__verify_ownership(checking, client_id)

        # Delete Transactions linked to the base account
        stmt_transactions = select(Transaction).where(
            Transaction.account_id == checking.account_id
        )
        result_transactions = await self.session.exec(stmt_transactions)
        transactions = result_transactions.all()
        for transaction in transactions:
            await self.session.delete(transaction)

        parent_account = await self.session.get(Account, checking.account_id)
        await self.session.delete(checking)
        if parent_account:
            await self.session.delete(parent_account)
        await self.session.commit()

    async def __to_out(self, checking: CheckingAccount) -> CheckingAccountOut:
        """Convert a checking account model to an output schema.

        Fetches the associated parent account to include shared fields.

        Args:
            checking: The checking account model instance.

        Returns:
            A consolidated CheckingAccountOut schema.

        """
        account = await self.session.get(Account, checking.account_id)
        return CheckingAccountOut(
            **checking.model_dump(),
            balance=account.balance if account else None,
            number=account.number if account else None,
            branch=account.branch if account else None,
        )

    async def __verify_ownership(
        self, checking: CheckingAccount, client_id: int
    ) -> None:
        """Verify that a checking account belongs to a specific client.

        Args:
            checking: The checking account model to verify.
            client_id: The expected client owner ID.

        Raises:
            HTTPException: 403 if ownership validation fails.

        """
        account = await self.session.get(Account, checking.account_id)
        if not account or account.client_id != client_id:
            raise HTTPException(
                status_code=403,
                detail="This account does not belong to this client",
            )

    async def __get_by_id(self, account_id: int) -> CheckingAccount:
        """Retrieve a checking account by ID or raise 404.

        Args:
            account_id: The primary key of the checking account.

        Returns:
            The found CheckingAccount instance.

        Raises:
            HTTPException: 404 if not found.

        """
        account = await self.session.get(CheckingAccount, account_id)
        if not account:
            raise HTTPException(
                status_code=404, detail="Checking account not found"
            )
        return account

    async def __get_client_by_id(self, client_id: int) -> Client:
        """Retrieve a client by ID or raise 404.

        Args:
            client_id: The primary key of the client.

        Returns:
            The found Client instance.

        Raises:
            HTTPException: 404 if not found.

        """
        client = await self.session.get(Client, client_id)
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        return client


CheckingAccountServiceDep = Annotated[
    CheckingAccountService, Depends(CheckingAccountService)
]
