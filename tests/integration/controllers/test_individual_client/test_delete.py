from httpx import AsyncClient, codes
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.models.client import Client, IndividualClient
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
        "name": "Teste Cascata",
        "cpf": "999",
        "address": "Rua X",
        "date_of_birth": "1990-01-01",
    }

    response = await client.post(
        client_url,
        json=payload,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    data = response.json()

    await client.delete(
        f"{client_url}{data['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    async with AsyncSession(async_engine) as session:
        statement = select(IndividualClient).where(
            IndividualClient.id == data["id"]
        )
        result = await session.exec(statement)
        assert result.first() is None

        statement = select(Client).where(Client.address == data["address"])
        result = await session.exec(statement)
        assert result.first() is None
