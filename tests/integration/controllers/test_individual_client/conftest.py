import pytest
import pytest_asyncio
from httpx import AsyncClient


@pytest.fixture(name="client_url")
def individual_client_url():
    return "/api/individual-clients/"


@pytest_asyncio.fixture(name="clients")
async def populate_individual_client_table(
    client: AsyncClient, access_token: str, client_url: str
):
    headers = {"Authorization": f"Bearer {access_token}"}
    clients = [
        (
            await client.post(
                client_url,
                json={
                    "name": "Fulano de Tal",
                    "cpf": "12345678901",
                    "address": "Rua Teste, 123",
                    "date_of_birth": "1990-01-01",
                },
                headers=headers,
            )
        ).json(),
        (
            await client.post(
                client_url,
                json={
                    "name": "Fulano de Tal 1",
                    "cpf": "12345678902",
                    "address": "Rua Teste, 124",
                    "date_of_birth": "1990-01-02",
                },
                headers=headers,
            )
        ).json(),
    ]

    return clients
