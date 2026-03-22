from typing import Annotated

from fastapi import APIRouter, Query

from src.schemas.account import CheckingAccountIn, CheckingAccountUpdateIn
from src.services.checking_account import CheckingAccountServiceDep
from src.views.account import CheckingAccountOut

router = APIRouter(prefix="/checking-accounts")


@router.get("/", response_model=list[CheckingAccountOut])
async def read_checking_accounts(
    client_id: int,
    checking_account_service: CheckingAccountServiceDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    return await checking_account_service.read_all(
        client_id=client_id, offset=offset, limit=limit
    )


@router.post("/", response_model=CheckingAccountOut)
async def create_checking_account(
    client_id: int,
    account_in: CheckingAccountIn,
    checking_account_service: CheckingAccountServiceDep,
):
    return await checking_account_service.create(account_in, client_id)


@router.get("/{account_id}", response_model=CheckingAccountOut)
async def read_checking_account(
    client_id: int,
    account_id: int,
    checking_account_service: CheckingAccountServiceDep,
):
    return await checking_account_service.read(account_id, client_id)


@router.patch("/{account_id}", response_model=CheckingAccountOut)
async def update_checking_account(
    client_id: int,
    account_id: int,
    account_in: CheckingAccountUpdateIn,
    checking_account_service: CheckingAccountServiceDep,
):
    return await checking_account_service.update(
        account_id, account_in, client_id
    )


@router.delete("/{account_id}", response_model=None)
async def delete_checking_account(
    client_id: int,
    account_id: int,
    checking_account_service: CheckingAccountServiceDep,
):
    return await checking_account_service.delete(account_id, client_id)
