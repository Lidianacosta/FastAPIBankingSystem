"""Deposit transaction controller.

Provides RESTful endpoints for managing deposit transactions
for a specific account. All endpoints require authentication.
"""

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
    """List all deposit transactions for a specific account.

    Args:
        account_id: The ID of the account.
        deposit_service: Dependency injected service.
        offset: Pagination offset.
        limit: Maximum number of records to return.

    Returns:
        A list of deposit transactions.
    """
    return await deposit_service.read_all(
        account_id=account_id, offset=offset, limit=limit
    )


@router.post("/", response_model=DepositOut)
async def create_deposit(
    account_id: int,
    deposit: DepositIn,
    deposit_service: DepositServiceDep,
):
    """Create a new deposit transaction for an account.

    Increases the account balance by the specified deposit value.

    Args:
        account_id: The ID of the account receiving the deposit.
        deposit: Payload containing the deposit value.
        deposit_service: Dependency injected service.

    Returns:
        The registered deposit transaction.

    Raises:
        HTTPException: 404 if the account is not found.
    """
    return await deposit_service.create(deposit, account_id)


@router.get("/{deposit_id}", response_model=DepositOut)
async def read_deposit(
    account_id: int,
    deposit_id: int,
    deposit_service: DepositServiceDep,
):
    """Retrieve details of a specific deposit transaction.

    Enforces that the transaction belongs to the specified account.

    Args:
        account_id: The ID of the account.
        deposit_id: The ID of the deposit transaction.
        deposit_service: Dependency injected service.

    Returns:
        The requested deposit transaction.

    Raises:
        HTTPException: 404 if not found or does not belong to the account.
    """
    return await deposit_service.read(deposit_id, account_id)


@router.delete("/{deposit_id}", response_model=None)
async def delete_deposit(
    account_id: int,
    deposit_id: int,
    deposit_service: DepositServiceDep,
):
    """Delete a specific deposit transaction.

    Decreases the account balance, reverting the original deposit.

    Args:
        account_id: The ID of the account.
        deposit_id: The ID of the deposit transaction to delete.
        deposit_service: Dependency injected service.

    Returns:
        None (200 OK) if successful.

    Raises:
        HTTPException: 404 if not found or does not belong to the account.
    """
    return await deposit_service.delete(deposit_id, account_id)
