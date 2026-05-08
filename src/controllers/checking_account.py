"""Checking Account controller.

Provides RESTful endpoints for managing checking accounts linked
to a specific client. All endpoints require authentication.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from src.schemas.account import CheckingAccountIn, CheckingAccountUpdateIn
from src.services.checking_account import CheckingAccountServiceDep
from src.utils.security import get_current_active_user
from src.views.account import CheckingAccountOut

router = APIRouter(
    prefix="/checking-accounts",
    dependencies=[Depends(get_current_active_user)],
)


@router.get("/", response_model=list[CheckingAccountOut])
async def read_checking_accounts(
    client_id: int,
    checking_account_service: CheckingAccountServiceDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    """List all checking accounts for a specific client.

    Args:
        client_id: The ID of the client whose accounts to retrieve.
        checking_account_service: Dependency injected service.
        offset: Pagination offset.
        limit: Maximum number of records to return (max 100).

    Returns:
        A list of checking accounts.
    """
    return await checking_account_service.read_all(
        client_id=client_id, offset=offset, limit=limit
    )


@router.post(
    "/", response_model=CheckingAccountOut, status_code=status.HTTP_201_CREATED
)
async def create_checking_account(
    client_id: int,
    account_in: CheckingAccountIn,
    checking_account_service: CheckingAccountServiceDep,
):
    """Create a new checking account for a specific client.

    Args:
        client_id: The ID of the client opening the account.
        account_in: Payload containing checking account details.
        checking_account_service: Dependency injected service.

    Returns:
        The newly created checking account.

    Raises:
        HTTPException: 404 if the client does not exist.
    """
    return await checking_account_service.create(account_in, client_id)


@router.get("/{account_id}", response_model=CheckingAccountOut)
async def read_checking_account(
    client_id: int,
    account_id: int,
    checking_account_service: CheckingAccountServiceDep,
):
    """Retrieve details of a specific checking account.

    Ensures the account belongs to the specified client.

    Args:
        client_id: The ID of the client.
        account_id: The ID of the checking account to retrieve.
        checking_account_service: Dependency injected service.

    Returns:
        The requested checking account.

    Raises:
        HTTPException: 404 if the account is not found or does not belong to the client.
    """
    return await checking_account_service.read(account_id, client_id)


@router.patch("/{account_id}", response_model=CheckingAccountOut)
async def update_checking_account(
    client_id: int,
    account_id: int,
    account_in: CheckingAccountUpdateIn,
    checking_account_service: CheckingAccountServiceDep,
):
    """Update a specific checking account partially.

    Args:
        client_id: The ID of the client.
        account_id: The ID of the checking account to update.
        account_in: Payload with the fields to update.
        checking_account_service: Dependency injected service.

    Returns:
        The updated checking account.

    Raises:
        HTTPException: 404 if the account is not found or does not belong to the client.
    """
    return await checking_account_service.update(
        account_id, account_in, client_id
    )


@router.delete("/{account_id}", response_model=None)
async def delete_checking_account(
    client_id: int,
    account_id: int,
    checking_account_service: CheckingAccountServiceDep,
):
    """Delete a specific checking account.

    This operation also deletes the underlying base account representation.

    Args:
        client_id: The ID of the client.
        account_id: The ID of the checking account to delete.
        checking_account_service: Dependency injected service.

    Returns:
        None (200 OK) if successful.

    Raises:
        HTTPException: 404 if the account is not found or does not belong to the client.
    """
    return await checking_account_service.delete(account_id, client_id)
