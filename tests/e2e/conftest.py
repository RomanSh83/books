import pytest_asyncio


@pytest_asyncio.fixture
async def header_with_regular_user_token(test_client, regular_user):
    response = await test_client.post("/auth/login", json=regular_user)
    regular_user_token = response.json().get("token")
    return {"Authorization": f"Bearer {regular_user_token}"}


@pytest_asyncio.fixture
async def header_with_another_regular_user_token(test_client, another_regular_user):
    response = await test_client.post("/auth/login", json=another_regular_user)
    another_regular_user_token = response.json().get("token")
    return {"Authorization": f"Bearer {another_regular_user_token}"}


@pytest_asyncio.fixture
async def header_with_admin_user_token(test_client, admin_user):
    response = await test_client.post("/auth/login", json=admin_user)
    admin_user_token = response.json().get("token")
    return {"Authorization": f"Bearer {admin_user_token}"}
