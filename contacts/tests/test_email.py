import pytest
from unittest.mock import AsyncMock, patch
from src.services.email import send_email
from fastapi_mail.errors import ConnectionErrors

@pytest.mark.asyncio
async def test_send_email_success(monkeypatch):
    mock_fm = AsyncMock()
    monkeypatch.setattr("src.services.email.FastMail", lambda conf: mock_fm)
    mock_fm.send_message.return_value = None

    email = "test@example.com"
    username = "testuser"
    host = "http://localhost"

    await send_email(email, username, host)
    mock_fm.send_message.assert_called_once()

@pytest.mark.asyncio
async def test_send_email_invalid_email(monkeypatch):
    mock_fm = AsyncMock()
    monkeypatch.setattr("src.services.email.FastMail", lambda conf: mock_fm)

    email = "invalid_email"
    username = "testuser"
    host = "http://localhost"

    with pytest.raises(ValueError):
        await send_email(email, username, host)

