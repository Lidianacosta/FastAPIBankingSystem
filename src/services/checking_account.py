from typing import Annotated, Sequence

from fastapi import Depends, HTTPException
from sqlmodel import select

from src.models.account import CheckingAccount
from src.schemas.account import CheckingAccountIn
from src.utils.database import AsyncSessionDep


class CheckingAccountService:
    def __init__(self, session: AsyncSessionDep) -> None:
        self.session = session

    async def create(self, account: CheckingAccount) -> CheckingAccount:
        self.session.add(account)
        await self.session.commit()
        await self.session.refresh(account)
        return account

    async def read_all(
        self,
        offset: int = 0,
        limit: int = 100,
    ) -> Sequence[CheckingAccount]:
        statement = select(CheckingAccount).offset(offset).limit(limit)
        accounts = await self.session.exec(statement)
        return accounts.all()

    async def read(self, id: int) -> CheckingAccount:
        account = await self.__get_by_id(id)
        return account

    async def update(
        self, id: int, account: CheckingAccountIn
    ) -> CheckingAccount:
        db_account = await self.__get_by_id(id)
        data = account.model_dump(exclude_unset=True)

        for attr, value in data.items():
            setattr(db_account, attr, value)

        self.session.add(db_account)
        await self.session.commit()
        await self.session.refresh(db_account)
        return db_account

    async def delete(self, id: int) -> None:
        account = await self.__get_by_id(id)
        await self.session.delete(account)
        await self.session.commit()

    async def __get_by_id(self, id: int):
        account = await self.session.get(CheckingAccount, id)
        if not account:
            raise HTTPException(
                status_code=404, detail="CheckingAccount not found"
            )
        return account


CheckingAccountServiceDep = Annotated[
    CheckingAccountService, Depends(CheckingAccountService)
]
