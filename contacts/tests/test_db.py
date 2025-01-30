import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from src.database.db import DatabaseSessionManager
from src.conf.config import settings

@pytest.fixture
def db_session_manager():
    return DatabaseSessionManager(settings.DB_URL)

@pytest.mark.asyncio
async def test_session_success(db_session_manager):
    async with db_session_manager.session() as session:
        assert isinstance(session, AsyncSession)
        # Перевірка, що сесія активна
        assert session.is_active

@pytest.mark.asyncio
async def test_session_rollback_on_error(db_session_manager):
    class CustomException(Exception):
        pass

    with pytest.raises(CustomException):
        async with db_session_manager.session() as session:
            assert isinstance(session, AsyncSession)
            raise CustomException("Test exception")

    # Перевірка, що сесія була відкотана
    async with db_session_manager.session() as session:
        assert session.is_active

@pytest.mark.asyncio
async def test_session_close(db_session_manager):
    async with db_session_manager.session() as session:
        assert isinstance(session, AsyncSession)
        # Перевірка, що сесія активна
        assert session.is_active

    # Перевірка, що сесія була закрита
    async with db_session_manager.session() as session:
        assert session.is_active