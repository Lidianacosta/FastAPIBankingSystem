"""User controller.

Provides endpoints for the currently authenticated user to read
and update their own profile.
"""

from typing import Annotated

from fastapi import APIRouter, Depends

from src.schemas.user import User, UserDB, UserUpdateIn
from src.services.user import UserServiceDep
from src.utils.security import (
    get_current_active_user,
)

router = APIRouter(prefix="/users")


@router.get("/me/")
async def read_user_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    """Get the profile of the currently authenticated user.

    Args:
        current_user: The user decoded from the JWT token.

    Returns:
        The current user's profile information.
    """
    return current_user


@router.patch("/me/", response_model=User)
async def update_user_me(
    user_update_in: UserUpdateIn,
    current_user: Annotated[UserDB, Depends(get_current_active_user)],
    user_service: UserServiceDep,
):
    """Update the profile of the currently authenticated user.

    Allows updating email, full name, active status, or password.
    Fields left as null or omitted will not be modified.

    Args:
        user_update_in: Payload containing the fields to update.
        current_user: The user decoded from the JWT token (with DB ID).
        user_service: Dependency injected user service.

    Returns:
        The updated user profile.
    """
    return await user_service.update_by_user(current_user, user_update_in)
