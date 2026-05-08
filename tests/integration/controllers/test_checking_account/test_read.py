from collections.abc import Callable

from httpx import AsyncClient, codes


async def test_list_checking_account_success(
    client: AsyncClient,
    access_token: str,
    accounts: list[dict[str, str]],
    get_checking_accounts_url: Callable[[int], str],
    created_client: dict,
):
    response = await client.get(
        get_checking_accounts_url(created_client["id"]),
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == codes.OK
    data = response.json()
    assert data == accounts


async def test_get_checking_account_by_id_success(
    client: AsyncClient,
    access_token: str,
    accounts: list[dict[str, str]],
    get_checking_accounts_url: Callable[[int], str],
    created_client: dict,
):
    response = await client.get(
        f"{get_checking_accounts_url(created_client['id'])}{accounts[0]['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == codes.OK
    data = response.json()
    assert data == accounts[0]


async def test_get_checking_account_by_id_fail_for_id_not_exist(
    client: AsyncClient,
    access_token: str,
    get_checking_accounts_url: Callable[[int], str],
    created_client: dict,
):
    response = await client.get(
        f"{get_checking_accounts_url(created_client['id'])}{0}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == codes.NOT_FOUND


async def test_get_checking_account_by_id_fail_for_client_id_not_exist(
    client: AsyncClient,
    access_token: str,
    get_checking_accounts_url: Callable[[int], str],
    accounts: list[dict[str, str]],
):
    response = await client.get(
        f"{get_checking_accounts_url(0)}{accounts[0]['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == codes.FORBIDDEN
