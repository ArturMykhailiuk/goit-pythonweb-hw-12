import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from unittest.mock import AsyncMock, MagicMock
from src.database.models import Contact, User
from src.repository.contacts import ContactRepository
from src.schemas import ContactBase, ContactUpdate, ContactStatusUpdate
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.fixture
def user():
    return User(id=1, username="testuser", email="testuser@example.com", hashed_password="hashedpassword")

@pytest.fixture
def contact_repository():
    session = AsyncMock(spec=AsyncSession)
    return ContactRepository(session)

@pytest.mark.asyncio
async def test_create_contact(contact_repository, user):
    contact_data = ContactBase(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone="123-456-7890",
        birthday="1990-01-01",
        additional_info="Some additional info"
    )
    contact = Contact(id=1, **contact_data.model_dump(), user=user)
    contact_repository.db.add = AsyncMock()
    contact_repository.db.commit = AsyncMock()
    contact_repository.db.refresh = AsyncMock()
    contact_repository.get_contact_by_id = AsyncMock(return_value=contact)

    await contact_repository.db.add(contact)
    await contact_repository.db.commit()
    await contact_repository.db.refresh(contact)

    created_contact = await contact_repository.create_contact(contact_data, user)
    assert created_contact.first_name == "John"
    assert created_contact.last_name == "Doe"
    assert created_contact.email == "john.doe@example.com"

@pytest.mark.asyncio
async def test_get_contacts(contact_repository, user):
    contact1 = Contact(id=1, first_name="John", last_name="Doe", email="john.doe@example.com", user=user)
    contact2 = Contact(id=2, first_name="Jane", last_name="Doe", email="jane.doe@example.com", user=user)
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [contact1, contact2]
    contact_repository.db.execute = AsyncMock(return_value=mock_result)

    contacts = await contact_repository.get_contacts(skip=0, limit=10, user=user)
    assert len(contacts) == 2

@pytest.mark.asyncio
async def test_get_contact_by_id(contact_repository, user):
    contact = Contact(id=1, first_name="John", last_name="Doe", email="john.doe@example.com", user=user)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = contact
    contact_repository.db.execute = AsyncMock(return_value=mock_result)

    fetched_contact = await contact_repository.get_contact_by_id(contact.id, user)
    assert fetched_contact.id == contact.id

@pytest.mark.asyncio
async def test_remove_contact(contact_repository, user):
    contact = Contact(id=1, first_name="John", last_name="Doe", email="john.doe@example.com", user=user)
    contact_repository.get_contact_by_id = AsyncMock(return_value=contact)
    contact_repository.db.delete = AsyncMock()
    contact_repository.db.commit = AsyncMock()

    await contact_repository.db.delete(contact)
    await contact_repository.db.commit()

    removed_contact = await contact_repository.remove_contact(contact.id, user)
    assert removed_contact.id == contact.id

@pytest.mark.asyncio
async def test_update_contact(contact_repository, user):
    contact = Contact(id=1, first_name="John", last_name="Doe", email="john.doe@example.com", user=user)
    contact_repository.get_contact_by_id = AsyncMock(return_value=contact)
    contact_repository.db.commit = AsyncMock()
    contact_repository.db.refresh = AsyncMock()

    update_data = ContactUpdate(first_name="Jane")
    updated_contact = await contact_repository.update_contact(contact.id, update_data, user)
    await contact_repository.db.commit()
    await contact_repository.db.refresh(contact)
    assert updated_contact.first_name == "Jane"

@pytest.mark.asyncio
async def test_update_status_contact(contact_repository, user):
    contact = Contact(id=1, first_name="John", last_name="Doe", email="john.doe@example.com", user=user)
    contact_repository.get_contact_by_id = AsyncMock(return_value=contact)
    contact_repository.db.commit = AsyncMock()
    contact_repository.db.refresh = AsyncMock()

    status_update = ContactStatusUpdate(done=True)
    updated_contact = await contact_repository.update_status_contact(contact.id, status_update, user)
    await contact_repository.db.commit()
    await contact_repository.db.refresh(contact)
    assert updated_contact.done is True


@pytest.mark.asyncio
async def test_get_contact_by_id_not_found(contact_repository, user):
    contact_repository.get_contact_by_id = AsyncMock(return_value=None)

    result = await contact_repository.get_contact_by_id(999, user)
    assert result is None

@pytest.mark.asyncio
async def test_update_contact_not_found(contact_repository, user):
    contact_repository.get_contact_by_id = AsyncMock(return_value=None)

    update_data = ContactUpdate(first_name="Jane")
    result = await contact_repository.update_contact(999, update_data, user)
    assert result is None

@pytest.mark.asyncio
async def test_update_status_contact_not_found(contact_repository, user):
    contact_repository.get_contact_by_id = AsyncMock(return_value=None)

    status_update = ContactStatusUpdate(done=True)
    result = await contact_repository.update_status_contact(999, status_update, user)
    assert result is None

@pytest.mark.asyncio
async def test_delete_contact_not_found(contact_repository, user):
    contact_repository.get_contact_by_id = AsyncMock(return_value=None)

    result = await contact_repository.remove_contact(999, user)
    assert result is None
    
@pytest.mark.asyncio
async def test_search_contact(contact_repository, user):
    contact1 = Contact(id=1, first_name="John", last_name="Doe", email="john.doe@example.com", user=user)
    contact2 = Contact(id=2, first_name="Jane", last_name="Doe", email="jane.doe@example.com", user=user)
    contact_repository.search_contact = AsyncMock(return_value=[contact1, contact2])

    result = await contact_repository.search_contact("Doe", user)
    assert len(result) == 2
    assert result[0].first_name == "John"
    assert result[1].first_name == "Jane"
    
@pytest.mark.asyncio
async def test_search_contact_by_first_name(contact_repository, user):
    contact1 = Contact(id=1, first_name="John", last_name="Doe", email="john.doe@example.com", user=user)
    contact_repository.search_contact = AsyncMock(return_value=[contact1])

    result = await contact_repository.search_contact(first_name="John", user=user)
    assert len(result) == 1
    assert result[0].first_name == "John"
    
@pytest.mark.asyncio
async def test_search_contact_by_last_name(contact_repository, user):
    contact1 = Contact(id=1, first_name="John", last_name="Doe", email="john.doe@example.com", user=user)
    contact_repository.search_contact = AsyncMock(return_value=[contact1])

    result = await contact_repository.search_contact(last_name="Doe", user=user)
    assert len(result) == 1
    assert result[0].last_name == "Doe"
    
@pytest.mark.asyncio
async def test_search_contact_by_email(contact_repository, user):
    contact1 = Contact(id=1, first_name="John", last_name="Doe", email="john.doe@example.com", user=user)
    contact_repository.search_contact = AsyncMock(return_value=[contact1])

    result = await contact_repository.search_contact(email="john.doe@example.com", user=user)
    assert len(result) == 1
    assert result[0].email == "john.doe@example.com"

@pytest.mark.asyncio
async def test_search_contact_by_multiple_fields(contact_repository, user):
    contact1 = Contact(id=1, first_name="John", last_name="Doe", email="john.doe@example.com", user=user)
    contact_repository.search_contact = AsyncMock(return_value=[contact1])

    result = await contact_repository.search_contact(first_name="John", last_name="Doe", email="john.doe@example.com", user=user)
    assert len(result) == 1
    assert result[0].first_name == "John"
    assert result[0].last_name == "Doe"
    assert result[0].email == "john.doe@example.com"
    

