from types import FunctionType

import pytest
import pytest_asyncio
from httpx import AsyncClient


@pytest.fixture(name="get_checking_accounts_url")
def checking_accounts_url():
    def get_checking_accounts_url(client_id: int):
        return f"/api/individual-clients/{client_id}/checking-accounts/"

    return get_checking_accounts_url


@pytest.fixture()
async def created_client(client: AsyncClient, access_token: str):
    payload = {
        "name": "Fulano de Tal",
        "cpf": "12345678901",
        "address": "Rua Teste, 123",
        "date_of_birth": "1990-01-01",
    }
    response = await client.post(
        "/api/individual-clients/",
        json=payload,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    return response.json()


@pytest_asyncio.fixture(name="accounts")
async def populate_checking_account_table(
    client: AsyncClient,
    access_token: str,
    get_checking_accounts_url: FunctionType,
    created_client: dict,
):
    headers = {"Authorization": f"Bearer {access_token}"}
    accounts = [
        (
            await client.post(
                get_checking_accounts_url(created_client["id"]),
                json={
                    "balance": 1000,
                    "limit": 1000,
                    "withdrawal_limit": 500,
                },
                headers=headers,
            )
        ).json(),
        (
            await client.post(
                get_checking_accounts_url(created_client["id"]),
                json={
                    "balance": 5000,
                    "limit": 1000,
                    "withdrawal_limit": 1000,
                },
                headers=headers,
            )
        ).json(),
    ]

    return accounts
