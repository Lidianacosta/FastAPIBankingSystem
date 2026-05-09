from httpx import AsyncClient, codes


async def test_update_individual_client_fields(
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

    data_user_created = response.json()
    new_name = "Patch Name Test"
    response = await client.patch(
        client_url + str(data_user_created["id"]),
        json={"name": new_name},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == codes.OK
    data = response.json()
    assert data["name"] == new_name


async def test_update_individual_client_fail_for_duplicate_cpf(
    client: AsyncClient, access_token: str, client_url: str
):
    payload1 = {
        "name": "Cliente 1",
        "cpf": "11111111111",
        "address": "Rua 1",
        "date_of_birth": "1990-01-01",
    }
    payload2 = {
        "name": "Cliente 2",
        "cpf": "22222222222",
        "address": "Rua 2",
        "date_of_birth": "1990-01-01",
    }
    resp1 = await client.post(
        client_url,
        json=payload1,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    client1_id = resp1.json()["id"]
    await client.post(
        client_url,
        json=payload2,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    response = await client.patch(
        f"{client_url}{client1_id}",
        json={"cpf": "22222222222"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == codes.BAD_REQUEST
    assert response.json()["detail"] == "CPF already registered"


async def test_update_individual_client_fail_for_not_found(
    client: AsyncClient, access_token: str, client_url: str
):
    response = await client.patch(
        client_url + str(0),
        json={},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == codes.NOT_FOUND
