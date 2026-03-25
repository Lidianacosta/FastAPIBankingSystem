"""Individual Client controller.

Provides RESTful endpoints for managing individual clients.
All endpoints require authentication.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from src.schemas.client import IndividualClientIn, IndividualClientUpdateIn
from src.services.individual_client import IndividualClientServiceDep
from src.utils.security import get_current_active_user
from src.views.client import IndividualClientOut

router = APIRouter(
    prefix="/individual-clients",
    dependencies=[Depends(get_current_active_user)],
)


@router.get("/", response_model=list[IndividualClientOut])
async def read_individual_clients(
    individual_client_service: IndividualClientServiceDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    """List all individual clients.

    Args:
        individual_client_service: Dependency injected service.
        offset: Pagination offset.
        limit: Maximum number of records to return (max 100).

    Returns:
        A list of individual clients.
    """
    return await individual_client_service.read_all(offset=offset, limit=limit)


@router.post("/", response_model=IndividualClientOut)
async def create_individual_client(
    individual_client: IndividualClientIn,
    individual_client_service: IndividualClientServiceDep,
):
    """Create a new individual client.

    This operation also creates the underlying base client representation.

    Args:
        individual_client: Payload containing individual client details.
        individual_client_service: Dependency injected service.

    Returns:
        The newly created individual client.
    """
    return await individual_client_service.create(individual_client)


@router.get("/{client_id}", response_model=IndividualClientOut)
async def read_individual_client(
    client_id: int, individual_client_service: IndividualClientServiceDep
):
    """Retrieve details of a specific individual client.

    Args:
        client_id: The ID of the client to retrieve.
        individual_client_service: Dependency injected service.

    Returns:
        The requested individual client.

    Raises:
        HTTPException: 404 if the client is not found.
    """
    return await individual_client_service.read(client_id)


@router.patch("/{client_id}", response_model=IndividualClientOut)
async def update_individual_client(
    client_id: int,
    individual_client: IndividualClientUpdateIn,
    individual_client_service: IndividualClientServiceDep,
):
    """Update a specific individual client partially.

    Args:
        client_id: The ID of the client to update.
        individual_client: Payload with the fields to update.
        individual_client_service: Dependency injected service.

    Returns:
        The updated individual client.

    Raises:
        HTTPException: 404 if the client is not found.
    """
    return await individual_client_service.update(client_id, individual_client)


@router.delete("/{client_id}", response_model=None)
async def delete_individual_client(
    client_id: int, individual_client_service: IndividualClientServiceDep
):
    """Delete a specific individual client.

    This operation also deletes the underlying base client representation.

    Args:
        client_id: The ID of the client to delete.
        individual_client_service: Dependency injected service.

    Returns:
        None (200 OK) if successful.

    Raises:
        HTTPException: 404 if the client is not found.
    """
    return await individual_client_service.delete(client_id)
