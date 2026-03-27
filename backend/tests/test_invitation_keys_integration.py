import os
import pytest
import pytest_asyncio
from unittest.mock import patch

from sqlalchemy import select

from app.database import get_db
from app.invitation_keys import sync_invitation_keys
from app.models import Base, InvitationKey


@pytest_asyncio.fixture
async def client_with_invitation_keys(test_engine, test_db_session):
    test_db_session.add(InvitationKey(key="a" * 32))
    await test_db_session.commit()

    async def override_get_db():
        yield test_db_session

    from app.main import app

    app.dependency_overrides[get_db] = override_get_db

    with patch("app.auth.settings") as mock_settings:
        mock_settings.invitation_keys = ["a" * 32]
        mock_settings.secret = "test-secret"

        from httpx import ASGITransport, AsyncClient

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client_without_invitation_keys(test_engine, test_db_session):
    async def override_get_db():
        yield test_db_session

    from app.main import app

    app.dependency_overrides[get_db] = override_get_db

    with patch("app.auth.settings") as mock_settings:
        mock_settings.invitation_keys = []
        mock_settings.secret = "test-secret"

        from httpx import ASGITransport, AsyncClient

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            yield client

    app.dependency_overrides.clear()


class TestInvitationKeyRegistration:
    @pytest.mark.asyncio
    async def test_registration_with_valid_invitation_key(self, client_with_invitation_keys):
        response = await client_with_invitation_keys.post(
            "/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "securepassword123",
                "forename": "New",
                "surname": "User",
                "pin": "5678",
                "invitation_key": "a" * 32,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["is_active"] is True

    @pytest.mark.asyncio
    async def test_registration_with_invalid_invitation_key(self, client_with_invitation_keys):
        response = await client_with_invitation_keys.post(
            "/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "securepassword123",
                "forename": "New",
                "surname": "User",
                "pin": "5678",
                "invitation_key": "b" * 32,
            },
        )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_registration_without_key_when_required(self, client_with_invitation_keys):
        response = await client_with_invitation_keys.post(
            "/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "securepassword123",
                "forename": "New",
                "surname": "User",
                "pin": "5678",
            },
        )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_registration_without_key_when_disabled(self, client_without_invitation_keys):
        response = await client_without_invitation_keys.post(
            "/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "securepassword123",
                "forename": "New",
                "surname": "User",
                "pin": "5678",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"

    @pytest.mark.asyncio
    async def test_user_linked_to_invitation_key(self, test_db_session, client_with_invitation_keys):
        await client_with_invitation_keys.post(
            "/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "securepassword123",
                "forename": "New",
                "surname": "User",
                "pin": "5678",
                "invitation_key": "a" * 32,
            },
        )

        from app.models import User

        result = await test_db_session.execute(
            select(User).where(User.email == "newuser@example.com")
        )
        user = result.scalar_one()
        assert user.invitation_key_id is not None

        result = await test_db_session.execute(
            select(InvitationKey).where(InvitationKey.key == "a" * 32)
        )
        key = result.scalar_one()
        assert user.invitation_key_id == key.id
