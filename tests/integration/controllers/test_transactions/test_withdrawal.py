from collections.abc import Callable

from httpx import AsyncClient, codes


async def test_create_withdrawal_success(
    client: AsyncClient,
    access_token: str,
    created_account: dict,
    withdrawal_url: Callable[[int], str],
    checking_accounts_url: Callable[[int, int], str],
):
    account_id = created_account["id"]
    client_id = created_account["client_id"]
    initial_balance = created_account["balance"]
    withdrawal_value = 200.0

    response = await client.post(
        withdrawal_url(account_id),
        json={"value": withdrawal_value},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == codes.OK
    data = response.json()
    assert data["value"] == withdrawal_value
    assert data["type"] == "withdrawal"

    resp_account = await client.get(
        checking_accounts_url(client_id, account_id),
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert resp_account.json()["balance"] == initial_balance - withdrawal_value


async def test_withdrawal_fail_insufficient_funds(
    client: AsyncClient,
    access_token: str,
    created_account: dict,
    withdrawal_url: Callable[[int], str],
):
    account_id = created_account["id"]
    withdrawal_value = 2000.0

    response = await client.post(
        withdrawal_url(account_id),
        json={"value": withdrawal_value},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == codes.BAD_REQUEST
    assert "Insufficient funds" in response.json()["detail"]


async def test_withdrawal_fail_daily_limit(
    client: AsyncClient,
    access_token: str,
    created_account: dict,
    withdrawal_url: Callable[[int], str],
):
    account_id = created_account["id"]

    headers = {"Authorization": f"Bearer {access_token}"}
    url = withdrawal_url(account_id)

    for _ in range(3):
        await client.post(url, json={"value": 10}, headers=headers)

    response = await client.post(url, json={"value": 10}, headers=headers)

    assert response.status_code == codes.BAD_REQUEST
    assert "Daily withdrawal count limit" in response.json()["detail"]


async def test_withdrawal_fail_daily_amount_limit(
    client: AsyncClient,
    access_token: str,
    created_account: dict,
    withdrawal_url: Callable[[int], str],
):
    account_id = created_account["id"]
    headers = {"Authorization": f"Bearer {access_token}"}
    url = withdrawal_url(account_id)

    response = await client.post(url, json={"value": 1001.0}, headers=headers)

    assert response.status_code == codes.BAD_REQUEST
    assert "Daily withdrawal amount limit reached" in response.json()["detail"]


async def test_delete_withdrawal_reverts_balance(
    client: AsyncClient,
    access_token: str,
    created_account: dict,
    withdrawal_url: Callable[[int], str],
    checking_accounts_url: Callable[[int, int], str],
):
    account_id = created_account["id"]
    client_id = created_account["client_id"]
    initial_balance = created_account["balance"]
    withdrawal_value = 100.0

    resp_wit = await client.post(
        withdrawal_url(account_id),
        json={"value": withdrawal_value},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    withdrawal_id = resp_wit.json()["id"]

    await client.delete(
        f"{withdrawal_url(account_id)}{withdrawal_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    resp_account = await client.get(
        checking_accounts_url(client_id, account_id),
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert resp_account.json()["balance"] == initial_balance
