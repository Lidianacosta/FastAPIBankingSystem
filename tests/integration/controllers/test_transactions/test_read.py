from collections.abc import Callable

import pytest
from httpx import AsyncClient, codes


async def test_list_deposits_success(
    client: AsyncClient,
    access_token: str,
    created_account: dict,
    deposit_url: Callable[[int], str],
):
    account_id = created_account["id"]
    headers = {"Authorization": f"Bearer {access_token}"}

    await client.post(
        deposit_url(account_id), json={"value": 100}, headers=headers
    )
    await client.post(
        deposit_url(account_id), json={"value": 200}, headers=headers
    )

    response = await client.get(deposit_url(account_id), headers=headers)

    assert response.status_code == codes.OK
    data = response.json()
    assert len(data) == 2
    assert data[0]["value"] == pytest.approx(100)
    assert data[1]["value"] == pytest.approx(200)


async def test_get_deposit_by_id_success(
    client: AsyncClient,
    access_token: str,
    created_account: dict,
    deposit_url: Callable[[int], str],
):
    account_id = created_account["id"]
    headers = {"Authorization": f"Bearer {access_token}"}

    resp_dep = await client.post(
        deposit_url(account_id), json={"value": 150}, headers=headers
    )
    deposit_id = resp_dep.json()["id"]

    response = await client.get(
        f"{deposit_url(account_id)}{deposit_id}", headers=headers
    )

    assert response.status_code == codes.OK
    assert response.json()["value"] == pytest.approx(150)


async def test_list_withdrawals_success(
    client: AsyncClient,
    access_token: str,
    created_account: dict,
    withdrawal_url: Callable[[int], str],
):
    account_id = created_account["id"]
    headers = {"Authorization": f"Bearer {access_token}"}

    await client.post(
        withdrawal_url(account_id), json={"value": 50}, headers=headers
    )
    await client.post(
        withdrawal_url(account_id), json={"value": 70}, headers=headers
    )

    response = await client.get(withdrawal_url(account_id), headers=headers)

    assert response.status_code == codes.OK
    data = response.json()
    assert len(data) == 2
    assert data[0]["value"] == pytest.approx(50)
    assert data[1]["value"] == pytest.approx(70)


async def test_get_withdrawal_by_id_success(
    client: AsyncClient,
    access_token: str,
    created_account: dict,
    withdrawal_url: Callable[[int], str],
):
    account_id = created_account["id"]
    headers = {"Authorization": f"Bearer {access_token}"}

    resp_wit = await client.post(
        withdrawal_url(account_id), json={"value": 80}, headers=headers
    )
    withdrawal_id = resp_wit.json()["id"]

    response = await client.get(
        f"{withdrawal_url(account_id)}{withdrawal_id}", headers=headers
    )

    assert response.status_code == codes.OK
    assert response.json()["value"] == pytest.approx(80)
