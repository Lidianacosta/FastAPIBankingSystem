from collections.abc import Callable

from httpx import AsyncClient, codes


async def test_create_account_success(
    client: AsyncClient,
    access_token: str,
    get_checking_accounts_url: Callable[[int], str],
    created_client: dict,
):
    payload = {
        "balance": 1000,
        "number": 1,
        "branch": "111",
        "limit": 1000,
        "withdrawal_limit": 500,
    }

    response = await client.post(
        get_checking_accounts_url(created_client["id"]),
        json=payload,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == codes.CREATED


async def test_create_account_fail_for_invalid_client_id(
    client: AsyncClient,
    access_token: str,
    get_checking_accounts_url: Callable[[int], str],
):
    payload = {
        "balance": 1000,
        "number": 1,
        "branch": "111",
        "limit": 1000,
        "withdrawal_limit": 500,
    }

    response = await client.post(
        get_checking_accounts_url(0),
        json=payload,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    data = response.json()

    assert response.status_code == codes.NOT_FOUND
    assert data["detail"] == "Client not found"
