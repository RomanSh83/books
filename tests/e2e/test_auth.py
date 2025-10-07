from copy import deepcopy

import pytest
from starlette import status


# Register Routes
# -----------------------------------------------------------------------------------------------
async def test_register_user_successfully(test_client, regular_user):
    response = await test_client.post("/auth/register", json=regular_user)
    assert response.status_code == status.HTTP_201_CREATED


async def test_register_user_duplicate_registration(test_client, regular_user):
    response = await test_client.post("/auth/register", json=regular_user)
    assert response.status_code == status.HTTP_409_CONFLICT


@pytest.mark.parametrize("missed_field", ["username", "email", "password"])
async def test_register_user_missed_field(test_client, another_regular_user, missed_field):
    login_user = deepcopy(another_regular_user)
    login_user.pop(missed_field)
    response = await test_client.post("/auth/register", json=login_user)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.parametrize("empty_field", ["username", "email", "password"])
async def test_register_user_with_empty_field(test_client, another_regular_user, empty_field):
    login_user = deepcopy(another_regular_user)
    login_user[empty_field] = ""
    response = await test_client.post("/auth/register", json=login_user)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_register_user_with_empty_request_body(test_client):
    response = await test_client.post("/auth/register", json={})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.parametrize(
    "wrong_email",
    [
        "(wrong_email)@domain.com",
        "wrong_email@&#$*df.com",
        "wrong_email@domain.%#$",
        "wrong_email@domaincom",
        "wrong_emaildomain.com",
        "wrong_email@domain.",
        "wrong_email",
    ],
)
async def test_register_user_with_wrong_email(test_client, another_regular_user, wrong_email):
    another_regular_user["email"] = wrong_email
    response = await test_client.post("/auth/register", json=another_regular_user)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.parametrize(
    "wrong_password",
    [
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
    ],
)
async def test_register_user_wrong_password_complexity(test_client, another_regular_user, wrong_password):
    another_regular_user["password"] = wrong_password
    response = await test_client.post("/auth/register", json=another_regular_user)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


# Login Routes
# -----------------------------------------------------------------------------------------------


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

@pytest.mark.parametrize(
    ("wrong_field", "wrong_value"),
    [
        ("username", "wrong_user"),
        ("email", "wrong_email@domain.com"),
        ("password", "wrong_password_1A")
    ]
)
async def test_login_with_wrong_field(test_client, regular_user, wrong_field, wrong_value):
    login_user = deepcopy(regular_user)
    login_user[wrong_field] = wrong_value
    response = await test_client.post("/auth/login", json=login_user)
    response_data = response.json()
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert not response_data.get("token")



# - `POST /auth/login/` — логин
#   - вход: `username` или `email`, `password`
#   - возврат: токен доступа (JWT)
#
# - (Опционально) `GET /auth/me/` — получить информацию о текущем пользователе

