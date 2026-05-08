import pytest
from httpx import AsyncClient, codes
from types import FunctionType


@pytest.mark.parametrize(
    "field,value",
    [
        ("balance", 2000.0),
        ("branch", "999"),
        ("limit", 5000.0),
        ("withdrawal_limit", 10),
    ],
)
async def test_update_checking_account_fields(
    client: AsyncClient,
    access_token: str,
    get_checking_accounts_url: FunctionType,
    created_client: dict,
    accounts: list[dict],
    field: str,
    value: any,
):
    account_id = accounts[0]["id"]
    client_id = created_client["id"]

    response = await client.patch(
        f"{get_checking_accounts_url(client_id)}{account_id}",
        json={field: value},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == codes.OK
    data = response.json()
    assert data[field] == value


async def test_update_checking_account_fail_for_wrong_owner(
    client: AsyncClient,
    access_token: str,
    get_checking_accounts_url: FunctionType,
    accounts: list[dict],
):
    account_id = accounts[0]["id"]

    response = await client.patch(
        f"{get_checking_accounts_url(0)}{account_id}",
        json={"balance": 9999},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == codes.FORBIDDEN
    assert response.json()["detail"] == "This account does not belong to this client"


async def test_update_checking_account_fail_for_not_found(
    client: AsyncClient,
    access_token: str,
    get_checking_accounts_url: FunctionType,
    created_client: dict,
):
    client_id = created_client["id"]

    response = await client.patch(
        f"{get_checking_accounts_url(client_id)}{0}",
        json={"balance": 9999},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == codes.NOT_FOUND
    assert response.json()["detail"] == "Checking account not found"
