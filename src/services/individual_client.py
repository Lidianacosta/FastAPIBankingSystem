from typing import Annotated

from fastapi import Depends, HTTPException
from sqlmodel import select

from src.models.client import Client, IndividualClient
from src.schemas.client import IndividualClientIn, IndividualClientUpdateIn
from src.utils.database import AsyncSessionDep
from src.views.client import IndividualClientOut


class IndividualClientService:
    def __init__(self, session: AsyncSessionDep) -> None:
        self.session = session

    async def create(self, client_in: IndividualClientIn) -> IndividualClient:
        client = Client(address=client_in.address, type="individual")
        self.session.add(client)
        await self.session.flush([client])

        individual_client = IndividualClient(
            name=client_in.name,
            cpf=client_in.cpf,
            date_of_birth=client_in.date_of_birth,
            client_id=client.id,
        )
        self.session.add(individual_client)
        await self.session.commit()
        await self.session.refresh(individual_client)
        return individual_client

    async def read(self, client_id: int) -> IndividualClientOut:
        individual = await self.__get_by_id(client_id)
        client = await self.session.get(Client, individual.client_id)

        return IndividualClientOut(
            **individual.model_dump(),
            address=client.address if client else "",
        )

    async def read_all(
        self, offset: int = 0, limit: int = 100
    ) -> list[IndividualClientOut]:
        statement = select(IndividualClient).offset(offset).limit(limit)
        result = await self.session.exec(statement)
        individuals = result.all()

        output = []
        for individual in individuals:
            client = await self.session.get(Client, individual.client_id)
            output.append(
                IndividualClientOut(
                    **individual.model_dump(),
                    address=client.address if client else "",
                )
            )
        return output

    async def update(
        self, client_id: int, client_in: IndividualClientUpdateIn
    ) -> IndividualClient:
        individual = await self.__get_by_id(client_id)
        data = client_in.model_dump(exclude_unset=True)

        individual_fields = IndividualClient.model_fields.keys()
        client_fields = Client.model_fields.keys()

        for attr, value in data.items():
            if attr in individual_fields:
                setattr(individual, attr, value)

        if individual.client_id:
            client = await self.session.get(Client, individual.client_id)
            if client:
                for attr, value in data.items():
                    if attr in client_fields:
                        setattr(client, attr, value)
                self.session.add(client)

        self.session.add(individual)
        await self.session.commit()
        await self.session.refresh(individual)
        return individual

    async def delete(self, client_id: int) -> None:
        client = await self.__get_by_id(client_id)
        await self.session.delete(client)
        await self.session.commit()

    async def __get_by_id(self, client_id) -> IndividualClient:
        client = await self.session.get(IndividualClient, client_id)
        if not client:
            raise HTTPException(
                status_code=404, detail="Individual client not found"
            )
        return client


IndividualClientServiceDep = Annotated[
    IndividualClientService, Depends(IndividualClientService)
]
