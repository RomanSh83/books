import uuid
from copy import deepcopy

import pytest
from starlette import status

# Fixtures
# --------------------------------------------------------------------------
admin_comment = {"text": "admin_comment"}
regular_comment = {"text": "regular_comment"}
anonymous_comment = {"text": "anonymous_comment"}

invalid_fields = [("text", "")]

wrong_comment_uid = "00000000-0000-0000-0000-000000000000"


# Tests
# Comments Routes
# --------------------------------------------------------------------------
async def test_comments_route_anonymous_successfully(test_client, book_uid):
    response = await test_client.get(f"/books/{book_uid}")
    assert response.status_code == status.HTTP_200_OK


async def test_comments_route_regular_user_successfully(test_client, header_with_regular_user_token, book_uid):
    response = await test_client.get(f"/books/{book_uid}", headers=header_with_regular_user_token)
    assert response.status_code == status.HTTP_200_OK


async def test_comments_route_admin_user_successfully(test_client, header_with_admin_user_token, book_uid):
    response = await test_client.get(f"/books/{book_uid}", headers=header_with_admin_user_token)
    assert response.status_code == status.HTTP_200_OK


# Create Comment Routes
# --------------------------------------------------------------------------
async def test_create_comment_by_admin_user_successfully(test_client, header_with_admin_user_token, book_uid):
    response = await test_client.post(
        f"/books/{book_uid}/comments", headers=header_with_admin_user_token, json=admin_comment
    )
    assert response.status_code == status.HTTP_201_CREATED
    response_data = response.json()
    assert response_data.get("text") == admin_comment["text"]
    assert "uid" in response_data
    assert "created_by" in response_data
    assert "created_at" in response_data


async def test_create_comment_by_admin_duplicate_text_successfully(test_client, header_with_admin_user_token, book_uid):
    response = await test_client.post(
        f"/books/{book_uid}/comments", headers=header_with_admin_user_token, json=admin_comment
    )
    assert response.status_code == status.HTTP_201_CREATED
    response_data = response.json()
    assert response_data.get("text") == admin_comment["text"]
    assert "uid" in response_data
    assert "created_by" in response_data
    assert "created_at" in response_data


async def test_create_comment_by_regular_user_successfully(test_client, header_with_regular_user_token, book_uid):
    response = await test_client.post(
        f"/books/{book_uid}/comments", headers=header_with_regular_user_token, json=regular_comment
    )
    assert response.status_code == status.HTTP_201_CREATED
    response_data = response.json()
    assert response_data.get("text") == regular_comment["text"]
    assert "uid" in response_data
    assert "created_by" in response_data
    assert "created_at" in response_data


async def test_create_comments_fails_by_anonymous_user(test_client, book_uid):
    response = await test_client.post(f"/books/{book_uid}/comments", json=regular_comment)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "detail" in response.json()


async def test_create_comment_by_admin_with_empty_request_body(test_client, header_with_admin_user_token, book_uid):
    response = await test_client.post(f"/books/{book_uid}/comments", headers=header_with_admin_user_token, json={})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert "detail" in response.json()


async def test_create_comment_by_regular_with_empty_request_body(test_client, header_with_regular_user_token, book_uid):
    response = await test_client.post(f"/books/{book_uid}/comments", headers=header_with_regular_user_token, json={})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert "detail" in response.json()


async def test_create_comment_by_admin_with_unexpected_field(test_client, header_with_admin_user_token, book_uid):
    response = await test_client.post(
        f"/books/{book_uid}/comments", headers=header_with_admin_user_token, json={"uid": str(uuid.uuid4())}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert "detail" in response.json()


async def test_create_comment_by_regular_with_unexpected_field(test_client, header_with_regular_user_token, book_uid):
    response = await test_client.post(
        f"/books/{book_uid}/comments", headers=header_with_regular_user_token, json={"uid": str(uuid.uuid4())}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert "detail" in response.json()


@pytest.mark.parametrize(("field_name", "invalid_value"), invalid_fields)
async def test_create_comment_by_admin_user_with_no_valid_field(
    test_client, header_with_admin_user_token, book_uid, field_name, invalid_value
):
    comment_data = deepcopy(admin_comment)
    comment_data[field_name] = invalid_value
    response = await test_client.post(
        f"/books/{book_uid}/comments", headers=header_with_admin_user_token, json=comment_data
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert "detail" in response.json()


@pytest.mark.parametrize(("field_name", "invalid_value"), invalid_fields)
async def test_create_comment_by_regular_user_with_no_valid_field(
    test_client, header_with_regular_user_token, book_uid, field_name, invalid_value
):
    comment_data = deepcopy(admin_comment)
    comment_data[field_name] = invalid_value
    response = await test_client.post(
        f"/books/{book_uid}/comments", headers=header_with_regular_user_token, json=comment_data
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert "detail" in response.json()


# Get Comment Routes
# --------------------------------------------------------------------------
async def test_get_comment_anonymous_successfully(test_client, book_uid, comment_uid, comment):
    response = await test_client.get(f"/books/{book_uid}/comments/{comment_uid}")
    response_data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert response_data.get("text") == comment["text"]


async def test_get_comment_regular_user_successfully(
    test_client, header_with_regular_user_token, book_uid, comment_uid, comment
):
    response = await test_client.get(
        f"/books/{book_uid}/comments/{comment_uid}", headers=header_with_regular_user_token
    )
    response_data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert response_data.get("text") == comment["text"]


async def test_get_comment_admin_user_successfully(
    test_client, header_with_admin_user_token, book_uid, comment_uid, comment
):
    response = await test_client.get(f"/books/{book_uid}/comments/{comment_uid}", headers=header_with_admin_user_token)
    response_data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert response_data.get("text") == comment["text"]


async def test_get_comment_wrong_uid(test_client, book_uid):
    response = await test_client.get(f"/books/{book_uid}/comments/{wrong_comment_uid}")
    response_data = response.json()
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "detail" in response_data


# Put Comment Routes
# --------------------------------------------------------------------------
async def test_put_comment_by_admin_successfully(
    test_client, header_with_admin_user_token, another_book_uid, mutable_comment_uid
):
    comment_before = (await test_client.get(f"/books/{another_book_uid}/comments/{mutable_comment_uid}")).json()
    payload = {"text": "comment_changed_by_admin"}
    response = await test_client.put(
        f"/books/{another_book_uid}/comments/{mutable_comment_uid}",
        headers=header_with_admin_user_token,
        json=payload,
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    comment_after = (await test_client.get(f"/books/{another_book_uid}/comments/{mutable_comment_uid}")).json()
    assert comment_after["text"] != comment_before["text"]
    assert comment_after["text"] == payload["text"]


async def test_put_comment_by_comment_author_successfully(
    test_client, header_with_regular_user_token, another_book_uid, mutable_comment_uid
):
    comment_before = (await test_client.get(f"/books/{another_book_uid}/comments/{mutable_comment_uid}")).json()
    payload = {"text": "comment_changed_by_author"}
    response = await test_client.put(
        f"/books/{another_book_uid}/comments/{mutable_comment_uid}",
        headers=header_with_regular_user_token,
        json=payload,
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    comment_after = (await test_client.get(f"/books/{another_book_uid}/comments/{mutable_comment_uid}")).json()
    assert comment_after["text"] != comment_before["text"]
    assert comment_after["text"] == payload["text"]


async def test_put_comment_by_comments_not_author_fails(
    test_client, header_with_another_regular_user_token, another_book_uid, mutable_comment_uid
):
    comment_before = (await test_client.get(f"/books/{another_book_uid}/comments/{mutable_comment_uid}")).json()
    payload = {"text": "comment_changed_by_not_author"}
    response = await test_client.put(
        f"/books/{another_book_uid}/comments/{mutable_comment_uid}",
        headers=header_with_another_regular_user_token,
        json=payload,
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    comment_after = (await test_client.get(f"/books/{another_book_uid}/comments/{mutable_comment_uid}")).json()
    assert comment_after["text"] == comment_before["text"]
    assert comment_after["text"] != payload["text"]


async def test_put_comment_by_anonymous_fails(test_client, another_book_uid, mutable_comment_uid):
    comment_before = (await test_client.get(f"/books/{another_book_uid}/comments/{mutable_comment_uid}")).json()
    payload = {"text": "comment_changed_by_anonymous"}
    response = await test_client.put(
        f"/books/{another_book_uid}/comments/{mutable_comment_uid}",
        json=payload,
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    comment_after = (await test_client.get(f"/books/{another_book_uid}/comments/{mutable_comment_uid}")).json()
    assert comment_after["text"] == comment_before["text"]
    assert comment_after["text"] != payload["text"]


async def test_put_comment_by_admin_with_empty_request_body(
    test_client, header_with_admin_user_token, another_book_uid, mutable_comment_uid
):
    comment_before = (await test_client.get(f"/books/{another_book_uid}/comments/{mutable_comment_uid}")).json()
    response = await test_client.put(
        f"/books/{another_book_uid}/comments/{mutable_comment_uid}",
        headers=header_with_admin_user_token,
        json={},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    comment_after = (await test_client.get(f"/books/{another_book_uid}/comments/{mutable_comment_uid}")).json()
    assert comment_after["text"] == comment_before["text"]


async def test_put_comment_by_admin_with_empty_field(
    test_client, header_with_admin_user_token, another_book_uid, mutable_comment_uid
):
    comment_before = (await test_client.get(f"/books/{another_book_uid}/comments/{mutable_comment_uid}")).json()
    payload = {"text": ""}
    response = await test_client.put(
        f"/books/{another_book_uid}/comments/{mutable_comment_uid}",
        json=payload,
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    comment_after = (await test_client.get(f"/books/{another_book_uid}/comments/{mutable_comment_uid}")).json()
    assert comment_after["text"] == comment_before["text"]
    assert comment_after["text"] != payload["text"]


@pytest.mark.parametrize(("field_name", "invalid_value"), invalid_fields)
async def test_put_comment_by_admin_with_invalid_value(
    test_client, header_with_admin_user_token, another_book_uid, mutable_comment_uid, field_name, invalid_value
):
    comment_before = (await test_client.get(f"/books/{another_book_uid}/comments/{mutable_comment_uid}")).json()
    response = await test_client.put(
        f"/books/{another_book_uid}/comments/{mutable_comment_uid}",
        headers=header_with_admin_user_token,
        json={field_name: invalid_value},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    comment_after = (await test_client.get(f"/books/{another_book_uid}/comments/{mutable_comment_uid}")).json()
    assert comment_after["text"] == comment_before["text"]


@pytest.mark.parametrize(("field_name", "invalid_value"), invalid_fields)
async def test_put_comment_by_comment_author_with_invalid_value(
    test_client, header_with_regular_user_token, another_book_uid, mutable_comment_uid, field_name, invalid_value
):
    comment_before = (await test_client.get(f"/books/{another_book_uid}/comments/{mutable_comment_uid}")).json()
    response = await test_client.put(
        f"/books/{another_book_uid}/comments/{mutable_comment_uid}",
        headers=header_with_regular_user_token,
        json={field_name: invalid_value},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    comment_after = (await test_client.get(f"/books/{another_book_uid}/comments/{mutable_comment_uid}")).json()
    assert comment_after["text"] == comment_before["text"]


# Delete Book Routes
# --------------------------------------------------------------------------
async def test_delete_comment_by_anonymous_user(test_client, another_book_uid, mutable_comment_uid):
    response = await test_client.get(f"/books/{another_book_uid}/comments/{mutable_comment_uid}")
    assert response.status_code == status.HTTP_200_OK
    response = await test_client.delete(f"/books/{another_book_uid}/comments/{mutable_comment_uid}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    response = await test_client.get(f"/books/{another_book_uid}/comments/{mutable_comment_uid}")
    assert response.status_code == status.HTTP_200_OK


async def test_delete_comment_by_comment_author(test_client, header_with_regular_user_token, book_uid):
    payload = {"text": "comment_by_comment_author_to delete"}
    response = await test_client.post(
        f"/books/{book_uid}/comments", headers=header_with_regular_user_token, json=payload
    )
    assert response.status_code == status.HTTP_201_CREATED
    test_uid = response.json()["uid"]
    response = await test_client.get(f"/books/{book_uid}/comments/{test_uid}")
    assert response.status_code == status.HTTP_200_OK
    response = await test_client.delete(
        f"/books/{book_uid}/comments/{test_uid}", headers=header_with_regular_user_token
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    response = await test_client.get(f"/books/{book_uid}/comments/{test_uid}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_delete_comment_by_not_comment_author(
    test_client, header_with_regular_user_token, header_with_another_regular_user_token, book_uid
):
    payload = {"text": "comment_by_not_comment_author_to delete"}
    response = await test_client.post(
        f"/books/{book_uid}/comments", headers=header_with_regular_user_token, json=payload
    )
    assert response.status_code == status.HTTP_201_CREATED
    test_uid = response.json()["uid"]
    response = await test_client.get(f"/books/{book_uid}/comments/{test_uid}")
    assert response.status_code == status.HTTP_200_OK
    response = await test_client.delete(
        f"/books/{book_uid}/comments/{test_uid}", headers=header_with_another_regular_user_token
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    response = await test_client.get(f"/books/{book_uid}/comments/{test_uid}")
    assert response.status_code == status.HTTP_200_OK


async def test_delete_comment_not_comment_author_by_admin(
    test_client, header_with_regular_user_token, header_with_admin_user_token, book_uid
):
    payload = {"text": "comment_by_not_comment_author_by_admin_to_delete"}
    response = await test_client.post(
        f"/books/{book_uid}/comments", headers=header_with_regular_user_token, json=payload
    )
    assert response.status_code == status.HTTP_201_CREATED
    test_uid = response.json()["uid"]
    response = await test_client.get(f"/books/{book_uid}/comments/{test_uid}")
    assert response.status_code == status.HTTP_200_OK
    response = await test_client.delete(f"/books/{book_uid}/comments/{test_uid}", headers=header_with_admin_user_token)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    response = await test_client.get(f"/books/{book_uid}/comments/{test_uid}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_delete_comment_by_admin_user_wrong_uid(test_client, header_with_admin_user_token, book_uid):
    response = await test_client.delete(
        f"/books/{book_uid}/comments/{wrong_comment_uid}", headers=header_with_admin_user_token
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
