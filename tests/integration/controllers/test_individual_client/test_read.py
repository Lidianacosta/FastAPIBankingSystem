from httpx import AsyncClient, codes


async def test_list_individual_client_success(
    client: AsyncClient, access_token: str, clients, client_url: str
):

    response = await client.get(
        client_url,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == codes.OK
    data = response.json()
    assert data == clients


async def test_get_individual_client_by_id_success(
    client: AsyncClient, access_token: str, clients, client_url: str
):
    response = await client.get(
        client_url + str(clients[0]["id"]),
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == codes.OK
    data = response.json()
    assert data == clients[0]


async def test_get_individual_client_by_id_fail_for_id_not_exist(
    client: AsyncClient, access_token: str, client_url: str
):
    response = await client.get(
        client_url + str(0),
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == codes.NOT_FOUND
