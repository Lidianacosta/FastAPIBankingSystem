from typing import Callable

from httpx import AsyncClient, codes


async def test_create_deposit_success(
    client: AsyncClient,
    access_token: str,
    created_account: dict,
    deposit_url: Callable[[int], str],
    checking_accounts_url: Callable[[int, int], str],
):
    account_id = int(created_account["id"])
    client_id = created_account["client_id"]
    initial_balance = created_account["balance"]
    deposit_value = 500.0

    response = await client.post(
        deposit_url(account_id),
        json={"value": deposit_value},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == codes.OK
    data = response.json()
    assert data["value"] == deposit_value
    assert data["type"] == "deposit"

    resp_account = await client.get(
        checking_accounts_url(client_id, account_id),
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert resp_account.status_code == codes.OK
    assert resp_account.json()["balance"] == initial_balance + deposit_value


async def test_create_deposit_fail_account_not_found(
    client: AsyncClient,
    access_token: str,
    deposit_url: Callable[[int], str],
):
    response = await client.post(
        deposit_url(0),
        json={"value": 100},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == codes.NOT_FOUND
    assert response.json()["detail"] == "Checking account not found"


async def test_delete_deposit_reverts_balance(
    client: AsyncClient,
    access_token: str,
    created_account: dict,
    deposit_url: Callable[[int], str],
    checking_accounts_url: Callable[[int, int], str],
):
    account_id = created_account["id"]
    client_id = created_account["client_id"]
    initial_balance = created_account["balance"]
    deposit_value = 500.0

    resp_dep = await client.post(
        deposit_url(account_id),
        json={"value": deposit_value},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    deposit_id = resp_dep.json()["id"]

    await client.delete(
        f"{deposit_url(account_id)}{deposit_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    resp_account = await client.get(
        checking_accounts_url(client_id, account_id),
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert resp_account.json()["balance"] == initial_balance
