"""Withdrawal transaction controller.

Provides RESTful endpoints for managing withdrawal transactions
for a specific account. All endpoints require authentication.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from src.schemas.transaction import WithdrawalIn
from src.services.withdrawal import WithdrawalServiceDep
from src.utils.security import get_current_active_user
from src.views.transaction import WithdrawalOut

router = APIRouter(
    prefix="/withdrawals", dependencies=[Depends(get_current_active_user)]
)


@router.get("/", response_model=list[WithdrawalOut])
async def read_withdrawals(
    account_id: int,
    withdrawal_service: WithdrawalServiceDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    """List all withdrawal transactions for a specific account.

    Args:
        account_id: The ID of the account.
        withdrawal_service: Dependency injected service.
        offset: Pagination offset.
        limit: Maximum number of records to return.

    Returns:
        A list of withdrawal transactions.

    """
    return await withdrawal_service.read_all(
        account_id=account_id, offset=offset, limit=limit
    )


@router.post("/", response_model=WithdrawalOut)
async def create_withdrawal(
    account_id: int,
    withdrawal: WithdrawalIn,
    withdrawal_service: WithdrawalServiceDep,
):
    """Create a new withdrawal transaction for an account.

    Decreases the account balance by the specified withdrawal value.
    Enforces business rules such as balance limits and withdrawal count.

    Args:
        account_id: The ID of the account making the withdrawal.
        withdrawal: Payload containing the withdrawal value.
        withdrawal_service: Dependency injected service.

    Returns:
        The registered withdrawal transaction.

    Raises:
        HTTPException: 404 if account not found, or 400 for business rule failures.

    """
    return await withdrawal_service.create(withdrawal, account_id)


@router.get("/{withdrawal_id}", response_model=WithdrawalOut)
async def read_withdrawal(
    account_id: int,
    withdrawal_id: int,
    withdrawal_service: WithdrawalServiceDep,
):
    """Retrieve details of a specific withdrawal transaction.

    Enforces that the transaction belongs to the specified account.

    Args:
        account_id: The ID of the account.
        withdrawal_id: The ID of the withdrawal transaction.
        withdrawal_service: Dependency injected service.

    Returns:
        The requested withdrawal transaction.

    Raises:
        HTTPException: 404 if not found or does not belong to the account.

    """
    return await withdrawal_service.read(withdrawal_id, account_id)


@router.delete("/{withdrawal_id}", response_model=None)
async def delete_withdrawal(
    account_id: int,
    withdrawal_id: int,
    withdrawal_service: WithdrawalServiceDep,
):
    """Delete a specific withdrawal transaction.

    Increases the account balance, reverting the original withdrawal.

    Args:
        account_id: The ID of the account.
        withdrawal_id: The ID of the withdrawal transaction to delete.
        withdrawal_service: Dependency injected service.

    Returns:
        None (200 OK) if successful.

    Raises:
        HTTPException: 404 if not found or does not belong to the account.

    """
    return await withdrawal_service.delete(withdrawal_id, account_id)
