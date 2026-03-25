"""User service layer.

Provides business logic and database interactions for managing users.
"""

from typing import Annotated

from fastapi import Depends, HTTPException
from sqlmodel import col, select

from src.models.user import User
from src.schemas.user import UserDB, UserIn, UserUpdateIn
from src.utils.database import AsyncSessionDep
from src.utils.password import get_password_hash


class UserService:
    """Service class for User management.

    Handles creation, retrieval, updates, and deletion of users,
    including password hashing and verification.

    Attributes:
        session: The asynchronous database session.
    """

    def __init__(self, session: AsyncSessionDep) -> None:
        self.session = session

    async def create(self, user_in: UserIn) -> User:
        """Create a new user.

        Hashes the provided plain text password before saving it to
        the database.

        Args:
            user_in: The user creation schema containing details and plain password.

        Returns:
            The newly created User model instance.
        """
        user = User(**user_in.model_dump(exclude_unset=True))
        user.hashed_password = get_password_hash(user_in.plain_password)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def read(self, user_id: int) -> User:
        """Retrieve a user by their ID.

        Args:
            user_id: The ID of the user to retrieve.

        Returns:
            The requested User model instance.

        Raises:
            HTTPException: 404 if the user is not found.
        """
        return await self.__get_by_id(user_id)

    async def read_all(self, offset: int = 0, limit: int = 100) -> list[User]:
        """List all users with pagination.

        Args:
            offset: The number of records to skip.
            limit: The maximum number of records to return.

        Returns:
            A list of User model instances.
        """
        statement = select(User).offset(offset).limit(limit)
        result = await self.session.exec(statement)
        return list(result.all())

    async def update(self, user_id: int, user_in: UserUpdateIn) -> User:
        """Update an existing user by ID.

        If a new plain password is provided, it will be hashed and updated.

        Args:
            user_id: The ID of the user to update.
            user_in: The schema containing fields to update.

        Returns:
            The updated User model instance.

        Raises:
            HTTPException: 404 if the user is not found.
        """
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
        """Update a user based on an authenticated user instance.

        Similar to `update`, but relies on the username of the current user.

        Args:
            user_db: The database representation of the current user.
            user_in: The schema containing fields to update.

        Returns:
            The updated User model instance.

        Raises:
            HTTPException: 404 if the user is not found in the database.
        """
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
        """Delete a user.

        Args:
            user_id: The ID of the user to delete.

        Raises:
            HTTPException: 404 if the user is not found.
        """
        client = await self.__get_by_id(user_id)
        await self.session.delete(client)
        await self.session.commit()

    async def get_user_by_username(self, username: str) -> User | None:
        """Retrieve a user by their username.

        Useful for authentication flows.

        Args:
            username: The unique username to search for.

        Returns:
            The User model instance if found, None otherwise.
        """
        statement = select(User).where(col(User.username) == username)
        result = await self.session.exec(statement)
        return result.first()

    async def __get_by_id(self, user_id) -> User:
        client = await self.session.get(User, user_id)
        if not client:
            raise HTTPException(status_code=404, detail="User not found")
        return client


UserServiceDep = Annotated[UserService, Depends(UserService)]
