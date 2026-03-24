from typing import Annotated

from fastapi import Depends, HTTPException
from sqlmodel import col, select

from src.models.user import User
from src.schemas.user import UserDB, UserIn, UserUpdateIn
from src.utils.database import AsyncSessionDep
from src.utils.password import get_password_hash


class UserService:
    def __init__(self, session: AsyncSessionDep) -> None:
        self.session = session

    async def create(self, user_in: UserIn) -> User:
        user = User(**user_in.model_dump(exclude_unset=True))
        user.hashed_password = get_password_hash(user_in.plain_password)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def read(self, user_id: int) -> User:
        return await self.__get_by_id(user_id)

    async def read_all(self, offset: int = 0, limit: int = 100) -> list[User]:
        statement = select(User).offset(offset).limit(limit)
        result = await self.session.exec(statement)
        return list(result.all())

    async def update(self, user_id: int, user_in: UserUpdateIn) -> User:
        user = await self.__get_by_id(user_id)
        data = user_in.model_dump(exclude_unset=True)

        if data.get("plain_password") is not None:
            user.hashed_password = get_password_hash(
                data.pop("plain_password")
            )

        for attr, value in data.items():
            setattr(user, attr, value)

        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update_by_user(
        self, user_db: UserDB, user_in: UserUpdateIn
    ) -> User:
        user = await self.get_user_by_username(user_db.username)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        data = user_in.model_dump(exclude_unset=True)

        if data.get("plain_password") is not None:
            user.hashed_password = get_password_hash(
                data.pop("plain_password")
            )

        for attr, value in data.items():
            setattr(user, attr, value)

        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def delete(self, user_id: int) -> None:
        client = await self.__get_by_id(user_id)
        await self.session.delete(client)
        await self.session.commit()

    async def get_user_by_username(self, username: str) -> User | None:
        statement = select(User).where(col(User.username) == username)
        result = await self.session.exec(statement)
        return result.first()

    async def __get_by_id(self, user_id) -> User:
        client = await self.session.get(User, user_id)
        if not client:
            raise HTTPException(status_code=404, detail="User not found")
        return client


UserServiceDep = Annotated[UserService, Depends(UserService)]
