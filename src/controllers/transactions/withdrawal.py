from typing import Annotated

from fastapi import APIRouter, Query

from src.schemas.transaction import WithdrawalIn
from src.services.withdrawal import WithdrawalServiceDep
from src.views.transaction import WithdrawalOut

router = APIRouter(prefix="/withdrawals")


@router.get("/", response_model=list[WithdrawalOut])
async def read_withdrawals(
    account_id: int,
    withdrawal_service: WithdrawalServiceDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    return await withdrawal_service.read_all(
        account_id=account_id, offset=offset, limit=limit
    )


@router.post("/", response_model=WithdrawalOut)
async def create_withdrawal(
    account_id: int,
    withdrawal: WithdrawalIn,
    withdrawal_service: WithdrawalServiceDep,
):
    return await withdrawal_service.create(withdrawal, account_id)


@router.get("/{transaction_id}", response_model=WithdrawalOut)
async def read_withdrawal(
    account_id: int,
    transaction_id: int,
    withdrawal_service: WithdrawalServiceDep,
):
    return await withdrawal_service.read(transaction_id, account_id)


@router.delete("/{transaction_id}", response_model=None)
async def delete_withdrawal(
    account_id: int,
    transaction_id: int,
    withdrawal_service: WithdrawalServiceDep,
):
    return await withdrawal_service.delete(transaction_id, account_id)
