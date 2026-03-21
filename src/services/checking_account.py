from typing import Annotated

from fastapi import Depends, HTTPException
from sqlmodel import select

from src.models.account import CheckingAccount
from src.schemas.account import CheckingAccountIn
from src.utils.database import AsyncSessionDep


class CheckingAccountService:
    def __init__(self, session: AsyncSessionDep) -> None:
        self.session = session

    async def create(self, account_in: CheckingAccountIn) -> CheckingAccount:
        account = CheckingAccount(**account_in.model_dump())
        self.session.add(account)
        await self.session.commit()
        await self.session.refresh(account)
        return account

    async def read_all(
        self,
        offset: int = 0,
        limit: int = 100,
    ) -> list[CheckingAccount]:
        statement = select(CheckingAccount).offset(offset).limit(limit)
        accounts = await self.session.exec(statement)
        return list(accounts.all())

    async def read(self, account_id: int) -> CheckingAccount:
        return await self.__get_by_id(account_id)

    async def update(
        self, account_id: int, checking_account_in: CheckingAccountIn
    ) -> CheckingAccount:
        account = await self.__get_by_id(account_id)
        data = checking_account_in.model_dump(exclude_unset=True)

        for attr, value in data.items():
            setattr(account, attr, value)

        self.session.add(account)
        await self.session.commit()
        await self.session.refresh(account)
        return account

    async def delete(self, account_id: int) -> None:
        account = await self.__get_by_id(account_id)
        await self.session.delete(account)
        await self.session.commit()

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
