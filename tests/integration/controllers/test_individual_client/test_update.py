import pytest
from httpx import AsyncClient, codes


@pytest.mark.parametrize(
    "field,value",
    [
        ("name", "Patch Name Test"),
        ("cpf", "10987654321"),
        ("address", "Rua Teste Patch, 123"),
        ("date_of_birth", "2000-01-01"),
    ],
)
async def test_patch_individual_client_fields(
    client: AsyncClient,
    access_token: str,
    field: str,
    value: str,
    client_url: str,
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

    data_user_created = response.json()
    response = await client.patch(
        client_url + str(data_user_created["id"]),
        json={field: value},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    print(response.json())

    assert response.status_code == codes.OK
    data = response.json()
    assert data[field] == value


async def test_patch_individual_client_fields_fail_for_id_not_exist(
    client: AsyncClient, access_token: str, client_url: str
):
    response = await client.patch(
        client_url + str(0),
        json={},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == codes.NOT_FOUND
