from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from src.repository.contacts import ContactRepository
from src.schemas import ContactBase, ContactUpdate, ContactStatusUpdate, ContactResponse
from src.database.models import User


class ContactService:
    def __init__(self, db: AsyncSession):
        self.contact_repository = ContactRepository(db)

    async def create_contact(self, body: ContactBase, user: User):
        return await self.contact_repository.create_contact(body, user)

    async def get_contacts(self, skip: int, limit: int, user: User):
        return await self.contact_repository.get_contacts(skip, limit, user)

    async def get_contact(self, contact_id: int, user: User):
        return await self.contact_repository.get_contact_by_id(contact_id, user)

    async def update_contact(self, contact_id: int, body: ContactUpdate, user: User):
        return await self.contact_repository.update_contact(contact_id, body, user)

    async def update_status_contact(self, contact_id: int, body: ContactStatusUpdate, user: User):
        return await self.contact_repository.update_status_contact(contact_id, body, user)

    async def remove_contact(self, contact_id: int, user: User):
        return await self.contact_repository.remove_contact(contact_id, user)

    async def search_contacts(
        self,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
    ) -> List[ContactResponse]:
        contacts = await self.contact_repository.search_contacts(
            first_name=first_name, last_name=last_name, email=email
        )
        return contacts

    async def get_upcoming_birthdays(self) -> List[ContactResponse]:
        contacts = await self.contact_repository.get_upcoming_birthdays()
        return contacts
