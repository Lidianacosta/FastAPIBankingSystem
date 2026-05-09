import pytest
from httpx import AsyncClient


@pytest.fixture()
async def created_client(client: AsyncClient, access_token: str):
    payload = {
        "name": "Transactor",
        "cpf": "11122233344",
        "address": "Rua das Transações, 100",
        "date_of_birth": "1995-05-05",
    }
    response = await client.post(
        "/api/individual-clients/",
        json=payload,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    return response.json()


@pytest.fixture()
async def created_account(
    client: AsyncClient, access_token: str, created_client: dict
):
    client_id = created_client["id"]
    payload = {
        "balance": 1000.0,
        "limit": 500.0,
        "withdrawal_limit": 3,
        "daily_withdrawal_limit": 1000.0,
    }
    response = await client.post(
        f"/api/individual-clients/{client_id}/checking-accounts/",
        json=payload,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    account_data = response.json()
    account_data["client_id"] = client_id
    return account_data


@pytest.fixture(name="deposit_url")
def get_deposit_url():
    def _deposit_url(account_id: int):
        return f"/api/checking-accounts/{account_id}/deposits/"

    return _deposit_url


@pytest.fixture(name="withdrawal_url")
def get_withdrawal_url():
    def _withdrawal_url(account_id: int):
        return f"/api/checking-accounts/{account_id}/withdrawals/"

    return _withdrawal_url


@pytest.fixture(name="checking_accounts_url")
def checking_accounts_url():
    def _checking_accounts_url(client_id: int, account_id: int):
        return f"/api/individual-clients/{client_id}/checking-accounts/{account_id}"

    return _checking_accounts_url
