from types import FunctionType

from httpx import AsyncClient, codes
from sqlmodel.ext.asyncio.session import AsyncSession

from src.models.account import Account, CheckingAccount
from src.utils.database import async_engine


async def test_delete_checking_account_success(
    client: AsyncClient,
    access_token: str,
    get_checking_accounts_url: FunctionType,
    created_client: dict,
):
    client_id = created_client["id"]
    payload = {
        "balance": 100,
        "limit": 100,
        "withdrawal_limit": 5,
        "daily_withdrawal_limit": 1000.0,
    }
    resp = await client.post(
        get_checking_accounts_url(client_id),
        json=payload,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    account_id = resp.json()["id"]

    response = await client.delete(
        f"{get_checking_accounts_url(client_id)}{account_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == codes.NO_CONTENT

    response = await client.get(
        f"{get_checking_accounts_url(client_id)}{account_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == codes.NOT_FOUND


async def test_delete_checking_account_fail_for_id_not_exist(
    client: AsyncClient,
    access_token: str,
    get_checking_accounts_url: FunctionType,
):
    response = await client.delete(
        f"{get_checking_accounts_url(0)}{0}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == codes.NOT_FOUND


async def test_delete_checking_account_cascade(
    client: AsyncClient,
    access_token: str,
    get_checking_accounts_url: FunctionType,
    created_client: dict,
):
    client_id = created_client["id"]
    payload = {
        "balance": 777,
        "limit": 777,
        "withdrawal_limit": 7,
        "daily_withdrawal_limit": 1000.0,
    }
    resp = await client.post(
        get_checking_accounts_url(client_id),
        json=payload,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    data = resp.json()
    account_id = data["id"]

    async with AsyncSession(async_engine) as session:
        db_checking = await session.get(CheckingAccount, account_id)
        assert db_checking is not None
        parent_id = db_checking.account_id

    await client.delete(
        f"{get_checking_accounts_url(client_id)}{account_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    async with AsyncSession(async_engine) as session:
        assert await session.get(CheckingAccount, account_id) is None
        assert await session.get(Account, parent_id) is None


async def test_delete_checking_account_fail_for_wrong_owner(
    client: AsyncClient,
    access_token: str,
    get_checking_accounts_url: FunctionType,
    accounts: list[dict],
):
    account_id = accounts[0]["id"]

    response = await client.delete(
        f"{get_checking_accounts_url(0)}{account_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == codes.FORBIDDEN


async def test_delete_checking_account_fail_for_not_found(
    client: AsyncClient,
    access_token: str,
    get_checking_accounts_url: FunctionType,
    created_client: dict,
):
    client_id = created_client["id"]

    response = await client.delete(
        f"{get_checking_accounts_url(client_id)}{0}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == codes.NOT_FOUND
