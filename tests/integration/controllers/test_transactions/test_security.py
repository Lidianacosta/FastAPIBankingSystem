from collections.abc import Callable

from httpx import AsyncClient, codes


async def test_transaction_access_forbidden_for_wrong_account(
    client: AsyncClient,
    access_token: str,
    created_account: dict,
    deposit_url: Callable[[int], str],
):
    account_id = created_account["id"]
    headers = {"Authorization": f"Bearer {access_token}"}

    resp_dep = await client.post(
        deposit_url(account_id), json={"value": 100}, headers=headers
    )
    deposit_id = resp_dep.json()["id"]

    response = await client.get(
        f"{deposit_url(0)}{deposit_id}", headers=headers
    )

    assert response.status_code == codes.NOT_FOUND


async def test_delete_transaction_forbidden_for_wrong_account(
    client: AsyncClient,
    access_token: str,
    created_account: dict,
    deposit_url: Callable[[int], str],
):
    account_id = created_account["id"]
    headers = {"Authorization": f"Bearer {access_token}"}

    resp_dep = await client.post(
        deposit_url(account_id), json={"value": 100}, headers=headers
    )
    deposit_id = resp_dep.json()["id"]

    response = await client.delete(
        f"{deposit_url(0)}{deposit_id}", headers=headers
    )

    assert response.status_code == codes.NOT_FOUND
