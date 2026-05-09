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

    # 1. Cria um depósito na conta real
    resp_dep = await client.post(
        deposit_url(account_id), json={"value": 100}, headers=headers
    )
    deposit_id = resp_dep.json()["id"]

    # 2. Tenta acessar esse depósito usando um account_id falso (0)
    response = await client.get(
        f"{deposit_url(0)}{deposit_id}", headers=headers
    )

    # Nota: No seu service, ele primeiro tenta buscar a conta (404) ou verifica ownership (403).
    # Como usamos account_id 0, ele deve dar 404 na CheckingAccount.
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

    # Tenta deletar de outra conta
    response = await client.delete(
        f"{deposit_url(0)}{deposit_id}", headers=headers
    )

    assert response.status_code == codes.NOT_FOUND
