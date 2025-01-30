import pytest
from unittest.mock import AsyncMock, MagicMock
from src.database.models import User
from src.repository.users import UserRepository
from src.schemas import UserCreate

@pytest.fixture
def user():
    return User(id=1, username="testuser", email="testuser@example.com", hashed_password="hashedpassword")

@pytest.fixture
def user_repository():
    session = AsyncMock()
    return UserRepository(session)

@pytest.mark.asyncio
async def test_get_user_by_id(user_repository, user):
    user_repository.db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=user)))

    fetched_user = await user_repository.get_user_by_id(user.id)
    assert fetched_user.id == user.id

@pytest.mark.asyncio
async def test_get_user_by_username(user_repository, user):
    user_repository.db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=user)))

    fetched_user = await user_repository.get_user_by_username(user.username)
    assert fetched_user.username == user.username

@pytest.mark.asyncio
async def test_get_user_by_email(user_repository, user):
    user_repository.db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=user)))

    fetched_user = await user_repository.get_user_by_email(user.email)
    assert fetched_user.email == user.email

@pytest.mark.asyncio
async def test_create_user(user_repository):
    user_data = UserCreate(
        username="newuser",
        email="newuser@example.com",
        password="newpassword"
    )
    user = User(
        id=1,
        username=user_data.username,
        email=user_data.email,
        hashed_password=user_data.password,
        avatar=None
    )
    user_repository.db.add = AsyncMock()
    user_repository.db.commit = AsyncMock()
    user_repository.db.refresh = AsyncMock()
    user_repository.get_user_by_id = AsyncMock(return_value=user)

    created_user = await user_repository.create_user(user_data)
    assert created_user.username == user_data.username
    assert created_user.email == user_data.email
    assert created_user.hashed_password == user_data.password

@pytest.mark.asyncio
async def test_confirmed_email(user_repository, user):
    user_repository.get_user_by_email = AsyncMock(return_value=user)
    user_repository.db.commit = AsyncMock()

    await user_repository.confirmed_email(user.email)
    await user_repository.db.commit()

    assert user.confirmed is True

@pytest.mark.asyncio
async def test_update_avatar_url(user_repository, user):
    user_repository.get_user_by_email = AsyncMock(return_value=user)
    user_repository.db.commit = AsyncMock()
    user_repository.db.refresh = AsyncMock()

    new_avatar_url = "http://example.com/avatar.png"
    updated_user = await user_repository.update_avatar_url(user.email, new_avatar_url)
    await user_repository.db.commit()
    await user_repository.db.refresh(user)

    assert updated_user.avatar == new_avatar_url