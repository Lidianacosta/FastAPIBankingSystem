from typing import Annotated

from fastapi import APIRouter, Depends, Query

from src.schemas.transaction import DepositIn
from src.services.deposit import DepositServiceDep
from src.utils.security import get_current_active_user
from src.views.transaction import DepositOut

router = APIRouter(
    prefix="/deposits", dependencies=[Depends(get_current_active_user)]
)


@router.get("/", response_model=list[DepositOut])
async def read_deposits(
    account_id: int,
    deposit_service: DepositServiceDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    return await deposit_service.read_all(
        account_id=account_id, offset=offset, limit=limit
    )


@router.post("/", response_model=DepositOut)
async def create_deposit(
    account_id: int,
    deposit: DepositIn,
    deposit_service: DepositServiceDep,
):
    return await deposit_service.create(deposit, account_id)


@router.get("/{transaction_id}", response_model=DepositOut)
async def read_deposit(
    account_id: int,
    transaction_id: int,
    deposit_service: DepositServiceDep,
):
    return await deposit_service.read(transaction_id, account_id)


@router.delete("/{transaction_id}", response_model=None)
async def delete_deposit(
    account_id: int,
    transaction_id: int,
    deposit_service: DepositServiceDep,
):
    return await deposit_service.delete(transaction_id, account_id)
