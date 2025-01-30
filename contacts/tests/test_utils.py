import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from main import app
from src.database.db import get_db

client = TestClient(app)

@pytest.mark.asyncio
async def test_healthchecker_success(monkeypatch):
    mock_db = AsyncMock()
    mock_db.execute.return_value.scalar_one_or_none.return_value = 1
    monkeypatch.setattr("src.database.db.get_db", lambda: mock_db)

    response = client.get("api/healthchecker")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Welcome to FastAPI!"
    

    

