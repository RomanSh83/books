import uuid
from copy import deepcopy
from datetime import date

import pytest
from starlette import status

from books.application.config import get_settings

# Fixtures
# --------------------------------------------------------------------------
MIN_LENGTH = get_settings().AUTHOR_NAME_MIN_LENGTH
MAX_LENGTH = get_settings().AUTHOR_NAME_MAX_LENGTH
NO_VALID_BIRTH_DATE = date.today().year - get_settings().AUTHOR_MIN_AUTHOR_AGE

test_author = {
    "first_name": "test_first_name",
    "last_name": "test_last_name",
    "birth_date": "1980-01-01",  # yyyy-mm-dd
    "bio": "test_bio",
}

test_author_without_bio = {
    "first_name": "test_author_without_bio_first_name",
    "last_name": "test_author_without_bio_last_name",
    "birth_date": "1981-01-01",  # yyyy-mm-dd
}

another_test_author = {
    "first_name": "another_test_first_name",
    "last_name": "another_test_last_name",
    "birth_date": "1982-01-01",  # yyyy-mm-dd
    "bio": "another_test_bio",
}

changed_fields = {
    "first_name": "new_first_name",
    "last_name": "new_last_name",
    "birth_date": "1900-01-01",  # yyyy-mm-dd
    "bio": "new_bio",
}

another_changed_fields = {
    "first_name": "another_new_first_name",
    "last_name": "another_new_last_name",
    "birth_date": "1910-01-01",  # yyyy-mm-dd
    "bio": "another_new_bio",
}

invalid_fields = [
    ("first_name", ""),
    ("first_name", "a" * (MIN_LENGTH - 1)),
    ("first_name", "a" * (MAX_LENGTH + 1)),
    ("last_name", ""),
    ("last_name", "a" * (MIN_LENGTH - 1)),
    ("last_name", "a" * (MAX_LENGTH + 1)),
    ("birth_date", ""),
    ("birth_date", "12 January 1975"),
    ("birth_date", NO_VALID_BIRTH_DATE),
]

wrong_author_uid = "00000000-0000-0000-0000-000000000000"


# Tests
# Authors Routes
# --------------------------------------------------------------------------
async def test_authors_route_anonymous_successfully(test_client):
    response = await test_client.get("/authors")
    assert response.status_code == status.HTTP_200_OK


async def test_authors_route_regular_user_successfully(test_client, header_with_regular_user_token):
    response = await test_client.get("/authors", headers=header_with_regular_user_token)
    assert response.status_code == status.HTTP_200_OK


async def test_authors_route_admin_user_successfully(test_client, header_with_admin_user_token):
    response = await test_client.get("/authors", headers=header_with_admin_user_token)
    assert response.status_code == status.HTTP_200_OK


# Create Author Routes
# --------------------------------------------------------------------------
async def test_create_author_by_admin_user_successfully(test_client, header_with_admin_user_token):
    response = await test_client.post("/authors", headers=header_with_admin_user_token, json=test_author)
    assert response.status_code == status.HTTP_201_CREATED
    response_data = response.json()
    for key in test_author:
        assert response_data.get(key) == test_author[key]


async def test_create_author_by_admin_user_without_bio_successfully(test_client, header_with_admin_user_token):
    response = await test_client.post("/authors", headers=header_with_admin_user_token, json=test_author_without_bio)
    assert response.status_code == status.HTTP_201_CREATED
    response_data = response.json()
    for key in test_author_without_bio:
        assert response_data.get(key) == test_author_without_bio[key]


async def test_create_author_by_admin_duplicate(test_client, header_with_admin_user_token):
    response = await test_client.post("/authors", headers=header_with_admin_user_token, json=test_author_without_bio)
    assert response.status_code == status.HTTP_409_CONFLICT
    assert "detail" in response.json()


async def test_create_author_fails_by_anonymous_user(test_client):
    response = await test_client.post("/authors", json=another_test_author)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "detail" in response.json()


async def test_create_author_fails_by_regular_user(test_client, header_with_regular_user_token):
    response = await test_client.post("/authors", headers=header_with_regular_user_token, json=another_test_author)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "detail" in response.json()


@pytest.mark.parametrize("required_field", ["first_name", "last_name", "birth_date"])
async def test_create_author_by_admin_without_required_field(test_client, header_with_admin_user_token, required_field):
    author = deepcopy(another_test_author)
    author.pop(required_field)
    response = await test_client.post("/authors", headers=header_with_admin_user_token, json=author)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert "detail" in response.json()


async def test_create_author_by_admin_with_empty_request_body(test_client, header_with_admin_user_token):
    author = {}
    response = await test_client.post("/authors", headers=header_with_admin_user_token, json=author)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert "detail" in response.json()


async def test_create_author_by_admin_with_unexpected_field(test_client, header_with_admin_user_token):
    author = deepcopy(another_test_author)
    author["uid"] = str(uuid.uuid4())
    response = await test_client.post("/authors", headers=header_with_admin_user_token, json=author)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert "detail" in response.json()


@pytest.mark.parametrize(("field_name", "invalid_value"), invalid_fields)
async def test_create_author_by_admin_with_no_valid_field(
    test_client, header_with_admin_user_token, field_name, invalid_value
):
    author = deepcopy(another_test_author)
    author[field_name] = invalid_value
    response = await test_client.post("/authors", headers=header_with_admin_user_token, json=author)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert "detail" in response.json()


# Get Author Routes
# --------------------------------------------------------------------------
async def test_get_author_anonymous_successfully(test_client, author_uid, author):
    response = await test_client.get(f"/authors/{author_uid}")
    response_data = response.json()
    assert response.status_code == status.HTTP_200_OK
    for key in author:
        assert response_data.get(key) == author[key]
    assert response_data.get("uid") == author_uid
    assert "bio" in response_data


async def test_get_author_regular_user_successfully(test_client, header_with_regular_user_token, author_uid, author):
    response = await test_client.get(f"/authors/{author_uid}", headers=header_with_regular_user_token)
    response_data = response.json()
    assert response.status_code == status.HTTP_200_OK
    for key in author:
        assert response_data.get(key) == author[key]
    assert response_data.get("uid") == author_uid
    assert "bio" in response_data


async def test_get_author_admin_user_successfully(test_client, header_with_admin_user_token, author_uid, author):
    response = await test_client.get(f"/authors/{author_uid}", headers=header_with_admin_user_token)
    response_data = response.json()
    assert response.status_code == status.HTTP_200_OK
    for key in author:
        assert response_data.get(key) == author[key]
    assert response_data.get("uid") == author_uid
    assert "bio" in response_data


async def test_get_author_wrong_uid(test_client):
    response = await test_client.get(f"/authors/{wrong_author_uid}")
    response_data = response.json()
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "detail" in response_data


# Put Author Routes
# --------------------------------------------------------------------------
@pytest.mark.parametrize("changed_field", ["first_name", "last_name", "birth_date", "bio"])
async def test_put_author_one_field_by_admin_successfully(
    test_client, header_with_admin_user_token, mutable_author_uid, changed_field
):
    author_before = (await test_client.get(f"/authors/{mutable_author_uid}")).json()
    no_changed_field = {"first_name", "last_name", "birth_date", "bio"}
    no_changed_field.remove(changed_field)
    response = await test_client.put(
        f"/authors/{mutable_author_uid}",
        headers=header_with_admin_user_token,
        json={changed_field: changed_fields[changed_field]},
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    author_after = (await test_client.get(f"/authors/{mutable_author_uid}")).json()
    for key in no_changed_field:
        assert author_after[key] == author_before[key]
    assert author_after[changed_field] == changed_fields[changed_field]


async def test_put_author_all_fields_by_admin_successfully(
    test_client, header_with_admin_user_token, mutable_author_uid
):
    author_before = (await test_client.get(f"/authors/{mutable_author_uid}")).json()
    response = await test_client.put(
        f"/authors/{mutable_author_uid}", headers=header_with_admin_user_token, json=another_changed_fields
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    author_after = (await test_client.get(f"/authors/{mutable_author_uid}")).json()
    for key in another_changed_fields:
        assert author_after[key] != author_before[key]
    for key in another_changed_fields:
        assert author_after[key] == another_changed_fields[key]


async def test_put_author_by_admin_with_empty_request_body(
    test_client, header_with_admin_user_token, mutable_author_uid
):
    author_before = (await test_client.get(f"/authors/{mutable_author_uid}")).json()
    response = await test_client.put(f"/authors/{mutable_author_uid}", headers=header_with_admin_user_token, json={})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    author_after = (await test_client.get(f"/authors/{mutable_author_uid}")).json()
    for key in author_before:
        assert author_after[key] == author_before[key]


async def test_put_author_by_admin_with_unexpected_field(test_client, header_with_admin_user_token, mutable_author_uid):
    author_before = (await test_client.get(f"/authors/{mutable_author_uid}")).json()
    response = await test_client.put(
        f"/authors/{mutable_author_uid}", headers=header_with_admin_user_token, json={"uid": str(uuid.uuid4())}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    author_after = (await test_client.get(f"/authors/{mutable_author_uid}")).json()
    assert author_after["uid"] == author_before["uid"]


@pytest.mark.parametrize(("field_name", "invalid_value"), invalid_fields)
async def test_put_author_by_admin_with_invalid_value_(
    test_client, header_with_admin_user_token, mutable_author_uid, field_name, invalid_value
):
    author_before = (await test_client.get(f"/authors/{mutable_author_uid}")).json()
    response = await test_client.put(
        f"/authors/{mutable_author_uid}", headers=header_with_admin_user_token, json={field_name: invalid_value}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    author_after = (await test_client.get(f"/authors/{mutable_author_uid}")).json()
    assert author_after["uid"] == author_before["uid"]


async def test_put_author_by_anonymous_user(test_client, mutable_author_uid):
    author_before = (await test_client.get(f"/authors/{mutable_author_uid}")).json()
    response = await test_client.put(f"/authors/{mutable_author_uid}", json={"first_name": "anonymous"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    author_after = (await test_client.get(f"/authors/{mutable_author_uid}")).json()
    assert author_after["first_name"] == author_before["first_name"]


async def test_put_author_by_regular_user(test_client, header_with_regular_user_token, mutable_author_uid):
    author_before = (await test_client.get(f"/authors/{mutable_author_uid}")).json()
    response = await test_client.put(
        f"/authors/{mutable_author_uid}", headers=header_with_regular_user_token, json={"first_name": "regular"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    author_after = (await test_client.get(f"/authors/{mutable_author_uid}")).json()
    assert author_after["first_name"] == author_before["first_name"]


# Delete Author Routes
# --------------------------------------------------------------------------
async def test_delete_author_by_anonymous_user(test_client, mutable_author_uid):
    response = await test_client.get(f"/authors/{mutable_author_uid}")
    assert response.status_code == status.HTTP_200_OK
    response = await test_client.delete(f"/authors/{mutable_author_uid}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    response = await test_client.get(f"/authors/{mutable_author_uid}")
    assert response.status_code == status.HTTP_200_OK


async def test_delete_author_by_regular_user(test_client, header_with_regular_user_token, mutable_author_uid):
    response = await test_client.get(f"/authors/{mutable_author_uid}")
    assert response.status_code == status.HTTP_200_OK
    response = await test_client.delete(f"/authors/{mutable_author_uid}", headers=header_with_regular_user_token)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    response = await test_client.get(f"/authors/{mutable_author_uid}")
    assert response.status_code == status.HTTP_200_OK


async def test_delete_author_by_admin_user_successfully(test_client, header_with_admin_user_token, mutable_author_uid):
    response = await test_client.get(f"/authors/{mutable_author_uid}")
    assert response.status_code == status.HTTP_200_OK
    response = await test_client.delete(f"/authors/{mutable_author_uid}", headers=header_with_admin_user_token)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    response = await test_client.get(f"/authors/{mutable_author_uid}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_delete_author_by_admin_user_wrong_uid(test_client, header_with_admin_user_token):
    response = await test_client.delete(f"/authors/{wrong_author_uid}", headers=header_with_admin_user_token)
    assert response.status_code == status.HTTP_404_NOT_FOUND
