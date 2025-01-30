import pytest
from datetime import datetime, timedelta, UTC
from jose import jwt, JWTError
from unittest.mock import patch, MagicMock
from src.services.auth import Hash, create_access_token, oauth2_scheme
from src.conf.config import settings

@pytest.fixture
def hash_instance():
    return Hash()

def test_verify_password(hash_instance):
    plain_password = "password123"
    hashed_password = hash_instance.get_password_hash(plain_password)
    assert hash_instance.verify_password(plain_password, hashed_password) is True

def test_get_password_hash(hash_instance):
    password = "password123"
    hashed_password = hash_instance.get_password_hash(password)
    assert hashed_password != password
    assert hash_instance.verify_password(password, hashed_password) is True

@pytest.mark.asyncio
async def test_create_access_token():
    data = {"sub": "testuser"}
    token = await create_access_token(data)
    decoded_data = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    assert decoded_data["sub"] == data["sub"]
    assert "exp" in decoded_data

@pytest.mark.asyncio
async def test_create_access_token_with_expiration():
    data = {"sub": "testuser"}
    expires_delta = 60  # 1 minute
    token = await create_access_token(data, expires_delta)
    decoded_data = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    assert decoded_data["sub"] == data["sub"]
    assert "exp" in decoded_data
    assert datetime.fromtimestamp(decoded_data["exp"], tz=UTC) < datetime.now(UTC) + timedelta(seconds=expires_delta)

def test_oauth2_scheme(monkeypatch):
    mock_request = MagicMock()
    mock_request.headers = {"Authorization": "Bearer testtoken"}
    monkeypatch.setattr("fastapi.security.oauth2.OAuth2PasswordBearer.__call__", lambda self, request: "testtoken")
    token = oauth2_scheme(mock_request)
    assert token == "testtoken"