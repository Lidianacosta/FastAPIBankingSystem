from httpx import AsyncClient, codes


async def test_read_user_me_success(client: AsyncClient, access_token: str):
    response = await client.get(
        "/api/users/me/",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == codes.OK
    data = response.json()
    assert data["username"] == "test_user"
    assert "hashed_password" not in data


async def test_update_user_me_success(client: AsyncClient, access_token: str):
    new_full_name = "Updated Manager Name"
    new_email = "new_manager@example.com"

    response = await client.patch(
        "/api/users/me/",
        json={"full_name": new_full_name, "email": new_email},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == codes.OK
    data = response.json()
    assert data["full_name"] == new_full_name
    assert data["email"] == new_email


async def test_update_user_me_password_success(
    client: AsyncClient, access_token: str
):
    response = await client.patch(
        "/api/users/me/",
        json={"plain_password": "new_very_secure_password"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == codes.OK

    login_response = await client.post(
        "/api/auth/token",
        data={
            "username": "test_user",
            "password": "new_very_secure_password",
            "grant_type": "password",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert login_response.status_code == codes.OK
    assert "access_token" in login_response.json()


async def test_user_me_unauthorized(client: AsyncClient):
    response = await client.get("/api/users/me/")
    assert response.status_code == codes.UNAUTHORIZED


async def test_update_user_me_fail_for_demo_user(
    client: AsyncClient, demo_access_token: str
):
    response = await client.patch(
        "/api/users/me/",
        json={"full_name": "Should Fail"},
        headers={"Authorization": f"Bearer {demo_access_token}"},
    )

    assert response.status_code == codes.FORBIDDEN
    assert (
        response.json()["detail"]
        == "Action not permitted in demonstration mode."
    )
