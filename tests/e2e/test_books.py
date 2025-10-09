import uuid
from copy import deepcopy

import pytest
import pytest_asyncio
from starlette import status

from books.application.config import get_settings
from tests.fixtures_data.base64_data import (
    image_file_json_invalid,
    image_file_json_invalid_file_format,
    image_file_json_invalid_file_type,
    image_file_json_valid,
)

# Fixtures
# --------------------------------------------------------------------------
MIN_LENGTH = get_settings().BOOK_TITLE_MIN_LENGTH
MAX_LENGTH = get_settings().BOOK_TITLE_MAX_LENGTH
MIN_YEAR = get_settings().BOOK_MIN_PUBLISHED_YEAR
MAX_YEAR = get_settings().BOOK_MAX_PUBLISHED_YEAR


@pytest.fixture
def test_book(author_uid):
    return {
        "title": "test_title",
        "author": str(author_uid),
        "published_year": 1900,
        "description": "test_description",
        "image": image_file_json_valid,
    }


@pytest.fixture
def test_book_without_image(author_uid):
    return {
        "title": "test_without_image_title",
        "author": str(author_uid),
        "published_year": 1800,
        "description": "test_without_image_description",
    }


@pytest.fixture
def another_test_book(author_uid):
    return {
        "title": "another_test_title",
        "author": str(author_uid),
        "published_year": 1900,
        "description": "another_test_description",
    }


changed_fields = {
    "title": "new_title",
    "published_year": 1800,
    "description": "new_description",
    "image": image_file_json_valid,
}

another_changed_fields = {
    "title": "another_new_title",
    "published_year": 1700,
    "description": "another_new_description",
    "image": image_file_json_valid,
}

invalid_fields = [
    ("title", "a" * (MIN_LENGTH - 1)),
    ("title", "a" * (MAX_LENGTH + 1)),
    ("published_year", MIN_YEAR - 1),
    ("published_year", MAX_YEAR + 1),
    ("author", "not_uuid"),
    ("image", image_file_json_invalid),
    ("image", image_file_json_invalid_file_format),
    ("image", image_file_json_invalid_file_type),
]

wrong_book_uid = "00000000-0000-0000-0000-000000000000"


@pytest_asyncio.fixture
async def header_with_regular_user_token(test_client, regular_user):
    response = await test_client.post("/auth/login", json=regular_user)
    regular_user_token = response.json().get("token")
    return {"Authorization": f"Bearer {regular_user_token}"}


@pytest_asyncio.fixture
async def header_with_admin_user_token(test_client, admin_user):
    response = await test_client.post("/auth/login", json=admin_user)
    admin_user_token = response.json().get("token")
    return {"Authorization": f"Bearer {admin_user_token}"}


# Tests
# Books Routes
# --------------------------------------------------------------------------
async def test_books_route_anonymous_successfully(test_client):
    response = await test_client.get("/books")
    assert response.status_code == status.HTTP_200_OK


async def test_books_route_regular_user_successfully(test_client, header_with_regular_user_token):
    response = await test_client.get("/books", headers=header_with_regular_user_token)
    assert response.status_code == status.HTTP_200_OK


async def test_books_route_admin_user_successfully(test_client, header_with_admin_user_token):
    response = await test_client.get("/books", headers=header_with_admin_user_token)
    assert response.status_code == status.HTTP_200_OK


# Create Book Routes
# --------------------------------------------------------------------------
async def test_create_book_by_admin_user_successfully(test_client, header_with_admin_user_token, test_book, author_uid):
    response = await test_client.post("/books", headers=header_with_admin_user_token, json=test_book)
    assert response.status_code == status.HTTP_201_CREATED
    response_data = response.json()
    assert response_data["title"] == test_book["title"]
    assert response_data["published_year"] == test_book["published_year"]
    assert response_data["description"] == test_book["description"]
    assert "image" in response_data
    assert response_data.get("author")
    assert response_data["author"].get("uid") == author_uid


async def test_create_book_by_admin_user_without_image_successfully(
    test_client, header_with_admin_user_token, author_uid, test_book_without_image
):
    response = await test_client.post("/books", headers=header_with_admin_user_token, json=test_book_without_image)
    assert response.status_code == status.HTTP_201_CREATED
    response_data = response.json()
    assert response_data["title"] == test_book_without_image["title"]
    assert response_data["published_year"] == test_book_without_image["published_year"]
    assert response_data["description"] == test_book_without_image["description"]
    assert response_data.get("author")
    assert response_data["author"].get("uid") == author_uid


async def test_create_book_by_admin_duplicate_title_author_constrain(
    test_client, header_with_admin_user_token, author_uid, test_book_without_image
):
    book_data = deepcopy(test_book_without_image)
    book_data["description"] = "some_description"
    book_data["published_year"] = 1999
    response = await test_client.post("/books", headers=header_with_admin_user_token, json=book_data)
    assert response.status_code == status.HTTP_409_CONFLICT
    assert "detail" in response.json()


async def test_create_book_fails_by_anonymous_user(test_client, author_uid, another_test_book):
    response = await test_client.post("/authors", json=another_test_book)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "detail" in response.json()


async def test_create_book_fails_by_regular_user(
    test_client, author_uid, header_with_regular_user_token, another_test_book
):
    response = await test_client.post("/authors", headers=header_with_regular_user_token, json=another_test_book)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "detail" in response.json()


@pytest.mark.parametrize("required_field", ["title", "author", "published_year", "description"])
async def test_create_book_by_admin_without_required_field(
    test_client, header_with_admin_user_token, required_field, another_test_book
):
    book_data = deepcopy(another_test_book)
    book_data.pop(required_field)
    response = await test_client.post("/authors", headers=header_with_admin_user_token, json=book_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert "detail" in response.json()


async def test_create_book_by_admin_with_empty_request_body(test_client, header_with_admin_user_token):
    book_data = {}
    response = await test_client.post("/authors", headers=header_with_admin_user_token, json=book_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert "detail" in response.json()


async def test_create_book_by_admin_with_unexpected_field(
    test_client, header_with_admin_user_token, author_uid, another_test_book
):
    book_data = deepcopy(another_test_book)
    book_data["uid"] = str(uuid.uuid4())
    response = await test_client.post("/authors", headers=header_with_admin_user_token, json=book_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert "detail" in response.json()


@pytest.mark.parametrize(("field_name", "invalid_value"), invalid_fields)
async def test_create_book_by_admin_with_no_valid_field(
    test_client, header_with_admin_user_token, field_name, invalid_value, another_test_book
):
    book_data = deepcopy(another_test_book)
    book_data[field_name] = invalid_value
    response = await test_client.post("/authors", headers=header_with_admin_user_token, json=book_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert "detail" in response.json()


# Get Book Routes
# --------------------------------------------------------------------------
async def test_get_book_anonymous_successfully(test_client, author_uid, book_uid, author, book):
    response = await test_client.get(f"/books/{book_uid}")
    response_data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert response_data.get("uid") == book_uid
    assert response_data.get("title") == book["title"]
    assert response_data.get("published_year") == book["published_year"]
    assert response_data.get("description") == book["description"]
    assert isinstance(response_data.get("author"), dict)
    for key in author:
        assert response_data["author"][key] == author[key]
    assert "image" in response_data


async def test_get_book_regular_user_successfully(
    test_client, header_with_regular_user_token, author_uid, book_uid, author, book
):
    response = await test_client.get(f"/books/{book_uid}", headers=header_with_regular_user_token)
    response_data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert response_data.get("uid") == book_uid
    assert response_data.get("title") == book["title"]
    assert response_data.get("published_year") == book["published_year"]
    assert response_data.get("description") == book["description"]
    assert isinstance(response_data.get("author"), dict)
    for key in author:
        assert response_data["author"][key] == author[key]
    assert "image" in response_data


async def test_get_book_admin_user_successfully(
    test_client, header_with_admin_user_token, author_uid, book_uid, author, book
):
    response = await test_client.get(f"/books/{book_uid}", headers=header_with_admin_user_token)
    response_data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert response_data.get("uid") == book_uid
    assert response_data.get("title") == book["title"]
    assert response_data.get("published_year") == book["published_year"]
    assert response_data.get("description") == book["description"]
    assert isinstance(response_data.get("author"), dict)
    for key in author:
        assert response_data["author"][key] == author[key]
    assert "image" in response_data


async def test_get_book_wrong_uid(test_client):
    response = await test_client.get(f"/books/{wrong_book_uid}")
    response_data = response.json()
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "detail" in response_data


# Put Book Routes
# --------------------------------------------------------------------------
@pytest.mark.parametrize("changed_field", ["title", "published_year", "description", "image"])
async def test_put_book_one_field_by_admin_successfully(
    test_client, header_with_admin_user_token, mutable_book_uid, changed_field
):
    book_before = (await test_client.get(f"/books/{mutable_book_uid}")).json()
    no_changed_field = {"title", "published_year", "description", "image"}
    no_changed_field.remove(changed_field)
    response = await test_client.put(
        f"/books/{mutable_book_uid}",
        headers=header_with_admin_user_token,
        json={changed_field: changed_fields[changed_field]},
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    book_after = (await test_client.get(f"/books/{mutable_book_uid}")).json()
    for key in no_changed_field:
        assert book_after[key] == book_before[key]
    if changed_field != "image":
        assert book_after[changed_field] == changed_fields[changed_field]


async def test_put_book_author_by_admin_successfully(
    test_client, header_with_admin_user_token, mutable_book_uid, author_uid
):
    book_before = (await test_client.get(f"/books/{mutable_book_uid}")).json()
    response = await test_client.put(
        f"/books/{mutable_book_uid}",
        headers=header_with_admin_user_token,
        json={"author": str(author_uid)},
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    book_after = (await test_client.get(f"/books/{mutable_book_uid}")).json()
    assert book_after["author"] != book_before["author"]
    assert book_after["author"]["uid"] == author_uid


async def test_put_book_all_fields_by_admin_successfully(
    test_client, header_with_admin_user_token, mutable_book_uid, another_author_uid
):
    book_before = (await test_client.get(f"/books/{mutable_book_uid}")).json()
    book_data = deepcopy(another_changed_fields)
    book_data["author"] = str(another_author_uid)
    response = await test_client.put(f"/books/{mutable_book_uid}", headers=header_with_admin_user_token, json=book_data)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    book_after = (await test_client.get(f"/books/{mutable_book_uid}")).json()
    for key in another_changed_fields:
        assert book_after[key] != book_before[key]
    for key in another_changed_fields:
        if key != "image":
            assert book_after[key] == another_changed_fields[key]
    assert book_after["author"] != book_before["author"]
    assert book_after["author"]["uid"] == another_author_uid


async def test_put_book_by_admin_with_empty_request_body(test_client, header_with_admin_user_token, mutable_book_uid):
    book_before = (await test_client.get(f"/books/{mutable_book_uid}")).json()
    response = await test_client.put(f"/books/{mutable_book_uid}", headers=header_with_admin_user_token, json={})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    book_after = (await test_client.get(f"/books/{mutable_book_uid}")).json()
    for key in book_before:
        assert book_after[key] == book_before[key]


async def test_put_book_by_admin_with_unexpected_field(test_client, header_with_admin_user_token, mutable_book_uid):
    book_before = (await test_client.get(f"/books/{mutable_book_uid}")).json()
    response = await test_client.put(
        f"/books/{mutable_book_uid}", headers=header_with_admin_user_token, json={"uid": str(uuid.uuid4())}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    book_after = (await test_client.get(f"/books/{mutable_book_uid}")).json()
    assert book_after["uid"] == book_before["uid"]


@pytest.mark.parametrize(("field_name", "invalid_value"), invalid_fields)
async def test_put_book_by_admin_with_invalid_value_(
    test_client, header_with_admin_user_token, mutable_book_uid, field_name, invalid_value
):
    book_before = (await test_client.get(f"/books/{mutable_book_uid}")).json()
    response = await test_client.put(
        f"/books/{mutable_book_uid}", headers=header_with_admin_user_token, json={field_name: invalid_value}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    book_after = (await test_client.get(f"/books/{mutable_book_uid}")).json()
    assert book_after["uid"] == book_before["uid"]


async def test_put_book_by_anonymous_user(test_client, mutable_book_uid):
    book_before = (await test_client.get(f"/books/{mutable_book_uid}")).json()
    response = await test_client.put(f"/books/{mutable_book_uid}", json={"title": "anonymous"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    book_after = (await test_client.get(f"/books/{mutable_book_uid}")).json()
    assert book_after["title"] == book_before["title"]


async def test_put_author_by_regular_user(test_client, header_with_regular_user_token, mutable_book_uid):
    book_before = (await test_client.get(f"/books/{mutable_book_uid}")).json()
    response = await test_client.put(
        f"/books/{mutable_book_uid}", headers=header_with_regular_user_token, json={"title": "regular"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    book_after = (await test_client.get(f"/books/{mutable_book_uid}")).json()
    assert book_after["title"] == book_before["title"]


# Delete Book Routes
# --------------------------------------------------------------------------
async def test_delete_book_by_anonymous_user(test_client, mutable_book_uid):
    response = await test_client.get(f"/books/{mutable_book_uid}")
    assert response.status_code == status.HTTP_200_OK
    response = await test_client.delete(f"/books/{mutable_book_uid}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    response = await test_client.get(f"/books/{mutable_book_uid}")
    assert response.status_code == status.HTTP_200_OK


async def test_delete_book_by_regular_user(test_client, header_with_regular_user_token, mutable_book_uid):
    response = await test_client.get(f"/books/{mutable_book_uid}")
    assert response.status_code == status.HTTP_200_OK
    response = await test_client.delete(f"/books/{mutable_book_uid}", headers=header_with_regular_user_token)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    response = await test_client.get(f"/books/{mutable_book_uid}")
    assert response.status_code == status.HTTP_200_OK


async def test_delete_book_by_admin_user_successfully(test_client, header_with_admin_user_token, mutable_book_uid):
    response = await test_client.get(f"/books/{mutable_book_uid}")
    assert response.status_code == status.HTTP_200_OK
    response = await test_client.delete(f"/books/{mutable_book_uid}", headers=header_with_admin_user_token)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    response = await test_client.get(f"/books/{mutable_book_uid}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_delete_author_by_admin_user_wrong_uid(test_client, header_with_admin_user_token):
    response = await test_client.delete(f"/books/{wrong_book_uid}", headers=header_with_admin_user_token)
    assert response.status_code == status.HTTP_404_NOT_FOUND
