import pytest
from httpx import AsyncClient, codes


async def test_create_individual_client_success(
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

    assert response.status_code == codes.CREATED
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["cpf"] == payload["cpf"]
    assert "id" in data


async def test_create_individual_client_fail_for_nunique_cpf(
    client: AsyncClient, access_token: str, client_url: str
):
    payload = {
        "name": "Fulano de Tal",
        "cpf": "12345678901",
        "address": "Rua Teste, 123",
        "date_of_birth": "1990-01-01",
    }

    await client.post(
        client_url,
        json=payload,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    response = await client.post(
        client_url,
        json=payload,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == codes.BAD_REQUEST
    data = response.json()
    assert data["detail"] == "CPF already registered"


@pytest.mark.parametrize("field", ["address", "name", "cpf", "date_of_birth"])
async def test_create_individual_client_fail_for_missing_fields(
    client: AsyncClient, access_token: str, field, client_url: str
):
    payload = {}

    response = await client.post(
        client_url,
        json=payload,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == codes.UNPROCESSABLE_ENTITY
    data = response.json()
    assert {
        "type": "missing",
        "loc": ["body", field],
        "msg": "Field required",
        "input": {},
    } in data["detail"]
