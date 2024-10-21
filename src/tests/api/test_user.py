from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from dao.user import UserDAO
from models.user import Address, User


@pytest.fixture
async def user(session: AsyncSession):
    user = User(
        first_name="John",
        last_name="Doe",
        age=18,
        addresses=[Address(email_address="Johns@gmail.com")],
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def test_get_users(user: User, client: AsyncClient, skip_auth):
    response = await client.get("/api/v1/users/")
    assert response.status_code == 200
    assert len(response.json()) == 1


async def test_get_user(user: User, client: AsyncClient):
    response = await client.get(f"/api/v1/users/{user.id}")

    assert response.status_code == 200
    assert response.json()["first_name"] == "John"


async def test_create_user(client: AsyncClient, session: AsyncSession):
    response = await client.post(
        "/api/v1/users/",
        json={
            "first_name": "Some",
            "last_name": "Guy",
            "age": 20,
            "addresses": [{"email_address": "some@gmail.com"}],
            "password": "asafqewoijfds",
        },
    )

    user_from_db = await UserDAO(session).get(response.json()["id"])
    assert response.status_code == 200
    assert response.json()["first_name"] == "Some"
    assert user_from_db.first_name == "Some"


async def test_update_user(user: User, client: AsyncClient, session: AsyncSession):
    response = await client.put(
        f"/api/v1/users/{user.id}",
        json={
            "first_name": "Some",
            "addresses": [{"email_address": "some@gmail.com"}],
        },
    )

    await session.refresh(user)
    assert response.status_code == 200
    assert response.json()["first_name"] == "Some"
    assert user.first_name == "Some"
    assert user.addresses[0].email_address == "some@gmail.com"


async def test_delete_user(user: User, client: AsyncClient, session: AsyncSession):
    response = await client.delete(f"/api/v1/users/{user.id}")

    assert response.status_code == 200
    assert len(await UserDAO(session).all()) == 0
