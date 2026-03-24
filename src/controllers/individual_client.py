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
    return await individual_client_service.read_all(offset=offset, limit=limit)


@router.post("/", response_model=IndividualClientOut)
async def create_individual_client(
    individual_client: IndividualClientIn,
    individual_client_service: IndividualClientServiceDep,
):
    return await individual_client_service.create(individual_client)


@router.get("/{client_id}", response_model=IndividualClientOut)
async def read_individual_client(
    client_id: int, individual_client_service: IndividualClientServiceDep
):
    return await individual_client_service.read(client_id)


@router.patch("/{client_id}", response_model=IndividualClientOut)
async def update_individual_client(
    client_id: int,
    individual_client: IndividualClientUpdateIn,
    individual_client_service: IndividualClientServiceDep,
):
    return await individual_client_service.update(client_id, individual_client)


@router.delete("/{client_id}", response_model=None)
async def delete_individual_client(
    client_id: int, individual_client_service: IndividualClientServiceDep
):
    return await individual_client_service.delete(client_id)
