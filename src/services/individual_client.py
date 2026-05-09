"""Individual Client service layer.

Provides business logic for creating and managing individual clients,
safely handling the relationship between `Client` and `IndividualClient`.
"""

from typing import Annotated

from fastapi import Depends, HTTPException
from sqlmodel import select

from src.models.account import Account, CheckingAccount
from src.models.client import Client, IndividualClient
from src.models.transaction import Transaction
from src.schemas.client import IndividualClientIn, IndividualClientUpdateIn
from src.utils.database import AsyncSessionDep
from src.views.client import IndividualClientOut


class IndividualClientService:
    """Service class for Individual Client management.

    Handles the dual-table creation/update operations necessary for
    the `IndividualClient` and its parent `Client` record.

    Attributes:
        session: The asynchronous database session.

    """

    def __init__(self, session: AsyncSessionDep) -> None:
        """Initialize the service with a database session.

        Args:
            session: The asynchronous database session.

        """
        self.session = session

    async def create(
        self, client_in: IndividualClientIn
    ) -> IndividualClientOut:
        """Create a new individual client.

        Creates the generic `Client` record first to obtain an ID,
        then creates and associates the `IndividualClient` record.

        Args:
            client_in: The schema containing client details.

        Returns:
            The newly created IndividualClient database model.

        Raises:
            HTTPException: 400 if the CPF is already registered.

        """
        statement = select(IndividualClient).where(
            IndividualClient.cpf == client_in.cpf
        )
        result = await self.session.exec(statement)
        if result.first():
            raise HTTPException(
                status_code=400, detail="CPF already registered"
            )

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

        return_data = individual_client.model_dump()
        return_data["address"] = client_in.address
        return IndividualClientOut(**return_data)

    async def read(self, client_id: int) -> IndividualClientOut:
        """Retrieve an individual client by their ID.

        Fetches both the specific individual client and its parent
        client record to construct a full output representation.

        Args:
            client_id: The ID of the individual client to retrieve.

        Returns:
            A consolidated IndividualClientOut schema.

        Raises:
            HTTPException: 404 if the individual client is not found.

        """
        individual = await self.__get_by_id(client_id)
        client = await self.session.get(Client, individual.client_id)

        return IndividualClientOut(
            **individual.model_dump(),
            address=client.address or "" if client else "",
        )

    async def read_all(
        self, offset: int = 0, limit: int = 100
    ) -> list[IndividualClientOut]:
        """List all individual clients with pagination.

        Gathers the base client address for each individual client to
        provide complete output schemas.

        Args:
            offset: The number of records to skip.
            limit: The maximum number of records to return.

        Returns:
            A list of IndividualClientOut schema instances.

        """
        statement = select(IndividualClient).offset(offset).limit(limit)
        result = await self.session.exec(statement)
        individuals = result.all()

        output = []
        for individual in individuals:
            client = await self.session.get(Client, individual.client_id)
            output.append(
                IndividualClientOut(
                    **individual.model_dump(),
                    address=client.address or "" if client else "",
                )
            )
        return output

    async def update(
        self, client_id: int, client_in: IndividualClientUpdateIn
    ) -> IndividualClientOut:
        """Update an existing individual client.

        Updates both the `IndividualClient` specific fields and the base
        `Client` fields (such as address) based on the provided schema.
        If the CPF is being updated, ensures it is not already in use.

        Args:
            client_id: The ID of the client to update.
            client_in: Schema containing the fields to update.

        Returns:
            The updated IndividualClient database model.

        Raises:
            HTTPException: 404 if the client is not found.
            HTTPException: 400 if the new CPF is already registered.

        """
        individual = await self.__get_by_id(client_id)
        data = client_in.model_dump(exclude_unset=True)

        # Check CPF uniqueness if it's being updated
        if "cpf" in data and data["cpf"] != individual.cpf:
            statement = select(IndividualClient).where(
                IndividualClient.cpf == data["cpf"]
            )
            result = await self.session.exec(statement)
            if result.first():
                raise HTTPException(
                    status_code=400, detail="CPF already registered"
                )

        individual_fields = IndividualClient.model_fields.keys()
        client_fields = Client.model_fields.keys()

        for attr, value in data.items():
            if attr in individual_fields:
                setattr(individual, attr, value)

        client = await self.__get_client_by_id(individual.client_id)

        for attr, value in data.items():
            if attr in client_fields:
                setattr(client, attr, value)
        self.session.add(client)

        self.session.add(individual)
        await self.session.commit()
        await self.session.refresh(client)
        await self.session.refresh(individual)

        return IndividualClientOut(
            **individual.model_dump(), address=client.address or ""
        )

    async def delete(self, client_id: int) -> None:
        """Delete an individual client and all associated accounts and transactions.

        Args:
            client_id: The ID of the individual client to delete.

        Raises:
            HTTPException: 404 if the client is not found.

        """
        individual = await self.__get_by_id(client_id)
        client_id_fk = individual.client_id

        # Delete all accounts and transactions associated with this client
        stmt_accounts = select(Account).where(
            Account.client_id == client_id_fk
        )
        result_accounts = await self.session.exec(stmt_accounts)
        accounts = result_accounts.all()

        for account in accounts:
            # Delete CheckingAccount linked to this account
            stmt_checking = select(CheckingAccount).where(
                CheckingAccount.account_id == account.id
            )
            result_checking = await self.session.exec(stmt_checking)
            checking = result_checking.first()
            if checking:
                await self.session.delete(checking)

            # Delete Transactions linked to this account
            stmt_transactions = select(Transaction).where(
                Transaction.account_id == account.id
            )
            result_transactions = await self.session.exec(stmt_transactions)
            transactions = result_transactions.all()
            for transaction in transactions:
                await self.session.delete(transaction)

            # Delete the base Account
            await self.session.delete(account)

        # Delete the specialized individual record
        await self.session.delete(individual)

        # Delete the base client record
        parent_client = await self.session.get(Client, client_id_fk)
        if parent_client:
            await self.session.delete(parent_client)

        await self.session.commit()

    async def __get_by_id(self, client_id) -> IndividualClient:
        """Retrieve an individual client by ID or raise 404.

        Args:
            client_id: The primary key of the individual client.

        Returns:
            The found IndividualClient instance.

        Raises:
            HTTPException: 404 if not found.

        """
        client = await self.session.get(IndividualClient, client_id)
        if not client:
            raise HTTPException(
                status_code=404, detail="Individual client not found"
            )

        return client

    async def __get_client_by_id(self, client_id) -> Client:
        """Retrieve a base client by ID or raise 404.

        Args:
            client_id: The primary key of the base client.

        Returns:
            The found Client instance.

        Raises:
            HTTPException: 404 if not found.

        """
        client = await self.session.get(Client, client_id)
        if not client:
            raise HTTPException(status_code=404, detail="client not found")
        return client


IndividualClientServiceDep = Annotated[
    IndividualClientService, Depends(IndividualClientService)
]
