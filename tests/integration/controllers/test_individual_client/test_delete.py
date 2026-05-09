from httpx import AsyncClient, codes
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.models.account import CheckingAccount
from src.models.client import Client, IndividualClient
from src.models.transaction import Transaction
from src.utils.database import async_engine


async def test_delete_individual_client_success(
    client: AsyncClient, access_token: str, client_url: str
):
    payload = {
        "name": "Fulano de Tal",
        "cpf": "12345678901",
        "address": "Rua Teste, 123",
        "date_of_birth": "1990-01-01",
    }

    response = await client.post(
        client_url,
        json=payload,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    data = response.json()

    response = await client.delete(
        client_url + str(data["id"]),
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == codes.NO_CONTENT

    response = await client.get(
        client_url + str(data["id"]),
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == codes.NOT_FOUND


async def test_delete_individual_client_fail_for_id_not_exist(
    client: AsyncClient, access_token: str, client_url: str
):
    response = await client.delete(
        client_url + str(0),
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == codes.NOT_FOUND


async def test_delete_individual_client_cascade(
    client: AsyncClient, access_token: str, client_url: str
):
    payload = {
        "name": "Fulano de Tal",
        "cpf": "12345678901",
        "address": "Rua Teste, 123",
        "date_of_birth": "1990-01-01",
    }

    response = await client.post(
        client_url,
        json=payload,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    data = response.json()

    async with AsyncSession(async_engine) as session:
        statement = select(IndividualClient).where(
            IndividualClient.id == data["id"]
        )
        result = await session.exec(statement)
        individual = result.first()
        client_id = individual.client_id

    await client.delete(
        client_url + str(data["id"]),
        headers={"Authorization": f"Bearer {access_token}"},
    )

    async with AsyncSession(async_engine) as session:
        statement = select(IndividualClient).where(
            IndividualClient.id == data["id"]
        )
        result = await session.exec(statement)
        assert result.first() is None

        statement = select(Client).where(Client.id == client_id)
        result = await session.exec(statement)
        assert result.first() is None


async def test_delete_individual_client_full_cascade(
    client: AsyncClient, access_token: str, client_url: str
):
    payload = {
        "name": "Full Cascade Test",
        "cpf": "99988877766",
        "address": "Rua Cascade, 1",
        "date_of_birth": "1990-01-01",
    }
    resp_client = await client.post(
        client_url,
        json=payload,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    client_id = resp_client.json()["id"]

    account_payload = {
        "balance": 1000,
        "limit": 500,
        "withdrawal_limit": 3,
        "daily_withdrawal_limit": 1000.0,
    }
    resp_account = await client.post(
        f"{client_url}{client_id}/checking-accounts/",
        json=account_payload,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    account_id = resp_account.json()["id"]

    await client.post(
        f"/api/checking-accounts/{account_id}/deposits/",
        json={"value": 100},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    await client.delete(
        f"{client_url}{client_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    async with AsyncSession(async_engine) as session:
        assert (await session.get(IndividualClient, client_id)) is None

        stmt_acc = select(CheckingAccount).where(
            CheckingAccount.id == account_id
        )
        assert (await session.exec(stmt_acc)).first() is None

        stmt_trans = select(Transaction).where(
            Transaction.account_id == account_id
        )
        assert (await session.exec(stmt_trans)).first() is None
