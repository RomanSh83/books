from copy import deepcopy

import pytest
import pytest_asyncio
from starlette import status

# Fixtures
# --------------------------------------------------------------------------
auth_user = {"username": "auth_user", "email": "auth_user@domain.com", "password": "auth_user_1A"}
another_auth_user = {"username": "another_user", "email": "another_user@domain.com", "password": "another_user"}

wrong_data_fields = [  # (name, value)
    ("username", "wrong_user"),
    ("email", "wrong_email@domain.com"),
    ("password", "wrong_password_1A"),
]

invalid_email_strings = [
    "(wrong_email)@domain.com",
    "wrong_email@&#$*df.com",
    "wrong_email@domain.%#$",
    "wrong_email@domaincom",
    "wrong_emaildomain.com",
    "wrong_email@domain.",
    "wrong_email",
    "",
]

invalid_password_strings = [
    "",  # empty
    "short",  # too short
    "toolongpasswordtoolongpassword_1A",  # too long
    "12345678",  # only num
    "asdfghjk",  # only lower
    "ASDFGHJK",  # only upper
    "!@#$%^&*",  # only special
    "123asdfg",  # nums and lower
    "123ASDFG",  # nums and upper
    "123!@#$%",  # nums and special
    "asdFGHJK",  # lower and upper
    "asd!@#$%",  # lower and special
    "ASD!@#$%",  # upper and special
    "123asdFG",  # nums, lower and upper
    "123asd!@",  # nums, lower and special
    "asdASD!@",  # lower, upper and special
]


@pytest_asyncio.fixture
async def regular_user_token(test_client, regular_user):
    response = await test_client.post("/auth/login", json=regular_user)
    return response.json().get("token")


# Tests
# Register Routes
# --------------------------------------------------------------------------
async def test_register_user_successfully(test_client):
    response = await test_client.post("/auth/register", json=auth_user)
    assert response.status_code == status.HTTP_201_CREATED


async def test_register_user_duplicate_registration(test_client):
    response = await test_client.post("/auth/register", json=auth_user)
    assert response.status_code == status.HTTP_409_CONFLICT


@pytest.mark.parametrize("missed_field", ["username", "email", "password"])
async def test_register_user_missed_field(test_client, missed_field):
    test_user = deepcopy(another_auth_user)
    test_user.pop(missed_field)
    response = await test_client.post("/auth/register", json=test_user)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.parametrize("empty_field", ["username", "email", "password"])
async def test_register_user_with_empty_field(test_client, empty_field):
    test_user = deepcopy(another_auth_user)
    test_user[empty_field] = ""
    response = await test_client.post("/auth/register", json=test_user)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_register_user_with_empty_request_body(test_client):
    response = await test_client.post("/auth/register", json={})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.parametrize("wrong_email", invalid_email_strings)
async def test_register_user_with_wrong_email(test_client, wrong_email):
    test_user = deepcopy(another_auth_user)
    test_user["email"] = wrong_email
    response = await test_client.post("/auth/register", json=test_user)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.parametrize("wrong_password", invalid_password_strings)
async def test_register_user_wrong_password_complexity(test_client, wrong_password):
    test_user = deepcopy(another_auth_user)
    test_user["password"] = wrong_password
    response = await test_client.post("/auth/register", json=test_user)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_register_user_with_unexpected_field(test_client):
    test_user = deepcopy(another_auth_user)
    another_auth_user["some_field"] = "some_value"
    response = await test_client.post("/auth/register", json=test_user)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


# Login Routes
# --------------------------------------------------------------------------
async def test_login_with_username_and_email_fields_successfully(test_client, regular_user):
    response = await test_client.post("/auth/login", json=regular_user)
    response_data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert response_data.get("token")


@pytest.mark.parametrize("removed_field", ["username", "email"])
async def test_login_with_one_login_field_successfully(test_client, regular_user, removed_field):
    login_user = deepcopy(regular_user)
    login_user.pop(removed_field)
    response = await test_client.post("/auth/login", json=login_user)
    response_data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert response_data.get("token")


@pytest.mark.parametrize("required_field", [("username", "email"), ("password",)])
async def test_login_without_required_field(test_client, regular_user, required_field):
    login_user = deepcopy(regular_user)
    for field in required_field:
        login_user.pop(field)
    response = await test_client.post("/auth/login", json=login_user)
    response_data = response.json()
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert not response_data.get("token")


async def test_login_with_empty_request_body(test_client):
    response = await test_client.post("/auth/login", json={})
    response_data = response.json()
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert not response_data.get("token")


@pytest.mark.parametrize(("field_name", "wrong_value"), wrong_data_fields)
async def test_login_with_wrong_data_field(test_client, regular_user, field_name, wrong_value):
    login_user = deepcopy(regular_user)
    login_user[field_name] = wrong_value
    response = await test_client.post("/auth/login", json=login_user)
    response_data = response.json()
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert not response_data.get("token")


# Get User Routes
# --------------------------------------------------------------------------
async def test_get_current_user_successfully(test_client, regular_user_token, regular_user):
    headers = {"Authorization": f"Bearer {regular_user_token}"}
    response = await test_client.get("/auth/me", headers=headers)
    response_data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert "uid" in response_data
    assert "username" in response_data
    assert "email" in response_data
    assert response_data["username"] == regular_user["username"]
    assert response_data["email"] == regular_user["email"]


async def test_get_current_user_fails_wrong_token(test_client, regular_user):
    headers = {"Authorization": "Bearer some_token"}
    response = await test_client.get("/auth/me", headers=headers)
    response_data = response.json()
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "uid" not in response_data
    assert "username" not in response_data
    assert "email" not in response_data


# Тесты на обработку невалидных токенов возможны только при написании unit тестов
# на use_case и сервис токенизации и в данном проекте не представлены
