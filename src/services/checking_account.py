from typing import Annotated

from fastapi import Depends, HTTPException
from sqlmodel import col, select

from src.models.account import Account, CheckingAccount
from src.schemas.account import CheckingAccountIn, CheckingAccountUpdateIn
from src.utils.database import AsyncSessionDep
from src.views.account import CheckingAccountOut


class CheckingAccountService:
    def __init__(self, session: AsyncSessionDep) -> None:
        self.session = session

    async def create(
        self, account_in: CheckingAccountIn, client_id: int
    ) -> CheckingAccountOut:
        account = Account(
            balance=account_in.balance,
            number=account_in.number,
            branch=account_in.branch,
            client_id=client_id,
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
        statement = (
            select(CheckingAccount)
            .join(Account, col(CheckingAccount.account_id) == col(Account.id))
            .where(col(Account.client_id) == client_id)
            .offset(offset)
            .limit(limit)
        )
        accounts = await self.session.exec(statement)
        return [await self.__to_out(c) for c in accounts.all()]

    async def read(self, account_id: int, client_id: int) -> CheckingAccountOut:
        checking = await self.__get_by_id(account_id)
        await self.__verify_ownership(checking, client_id)
        return await self.__to_out(checking)

    async def update(
        self,
        account_id: int,
        checking_account_in: CheckingAccountUpdateIn,
        client_id: int,
    ) -> CheckingAccountOut:
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
        checking = await self.__get_by_id(account_id)
        await self.__verify_ownership(checking, client_id)
        parent_account = await self.session.get(Account, checking.account_id)
        await self.session.delete(checking)
        if parent_account:
            await self.session.delete(parent_account)
        await self.session.commit()

    async def __to_out(self, checking: CheckingAccount) -> CheckingAccountOut:
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
        account = await self.session.get(Account, checking.account_id)
        if not account or account.client_id != client_id:
            raise HTTPException(
                status_code=403,
                detail="This account does not belong to this client",
            )

    async def __get_by_id(self, account_id: int) -> CheckingAccount:
        account = await self.session.get(CheckingAccount, account_id)
        if not account:
            raise HTTPException(
                status_code=404, detail="Checking account not found"
            )
        return account


CheckingAccountServiceDep = Annotated[
    CheckingAccountService, Depends(CheckingAccountService)
]
