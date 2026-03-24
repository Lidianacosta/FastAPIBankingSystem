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
    return current_user


@router.patch("/me/", response_model=User)
async def update_user_me(
    user_update_in: UserUpdateIn,
    current_user: Annotated[UserDB, Depends(get_current_active_user)],
    user_service: UserServiceDep,
):
    return await user_service.update_by_user(current_user, user_update_in)
