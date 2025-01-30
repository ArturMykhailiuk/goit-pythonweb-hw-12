from typing import List, Optional
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database.models import Contact, User
from src.schemas import ContactBase, ContactUpdate, ContactStatusUpdate



class ContactRepository:
    def __init__(self, session: AsyncSession):
        self.db = session

    async def get_contacts(self, skip: int, limit: int, user: User) -> List[Contact]:
        """
        Retrieve a list of contacts for the given user.

        Parameters:
        - skip: The number of contacts to skip for pagination.
        - limit: The maximum number of contacts to return.
        - user: The user whose contacts to retrieve.

        Returns:
        - A list of contacts.
        """
        stmt = select(Contact).filter_by(user=user).offset(skip).limit(limit)
        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()

    async def get_contact_by_id(self, contact_id: int, user: User) -> Contact | None:
        """
        Retrieve a contact by its ID for the given user.

        Parameters:
        - contact_id: The ID of the contact to retrieve.
        - user: The user who owns the contact.

        Returns:
        - The contact if found, otherwise None.
        """
        # Create a SQLAlchemy select statement to find the contact by ID and user
        stmt = select(Contact).filter_by(id=contact_id, user=user)
        
        # Execute the statement asynchronously
        contact = await self.db.execute(stmt)
        
        # Return the single contact result or None if not found
        return contact.scalar_one_or_none()

    async def create_contact(self, body: ContactBase, user: User) -> Contact:
        """
        Create a new contact for the given user.

        Parameters:
        - body: The JSON payload containing the contact data.
        - user: The user who owns the contact.

        Returns:
        - The created contact.
        """
        # Create a new contact instance with the provided data and user
        contact = Contact(**body.model_dump(exclude_unset=True), user=user)
        
        # Add the contact to the database session
        self.db.add(contact)
        
        # Commit the database transaction
        await self.db.commit()
        
        # Refresh the contact instance with the generated ID
        await self.db.refresh(contact)
        
        # Return the created contact
        return await self.get_contact_by_id(contact.id, user)

    async def remove_contact(self, contact_id: int, user: User) -> Contact | None:
        """
        Delete a contact by ID and user.

        Parameters:
        - contact_id: The ID of the contact to delete.
        - user: The user who owns the contact.

        Returns:
        - The contact if found, otherwise None.
        """
        # Find the contact if it exists
        contact = await self.get_contact_by_id(contact_id, user)
        if contact:
            # Delete the contact
            await self.db.delete(contact)
            # Commit the database transaction
            await self.db.commit()
        return contact

    async def update_contact(self, contact_id: int, body: ContactUpdate, user: User) -> Contact | None:
        """
        Update a contact by ID and user.

        Parameters:
        - contact_id: The ID of the contact to update.
        - body: The JSON payload containing the contact data to update.
        - user: The user who owns the contact.

        Returns:
        - The updated contact if found, otherwise None.
        """
        # Find the contact if it exists
        contact = await self.get_contact_by_id(contact_id, user)
        if contact:
            # Update the contact instance with the provided data
            for key, value in body.model_dump(exclude_unset=True).items():
                setattr(contact, key, value)
            # Commit the database transaction
            await self.db.commit()
            # Refresh the contact instance with the updated fields
            await self.db.refresh(contact)
        return contact

    async def update_status_contact(
        self, contact_id: int, body: ContactStatusUpdate, user: User
    ) -> Contact | None:
        """
        Update the status of a contact by ID and user.

        Parameters:
        - contact_id: The ID of the contact to update.
        - body: The JSON payload containing the contact data to update.
        - user: The user who owns the contact.

        Returns:
        - The updated contact if found, otherwise None.
        """
        # Find the contact if it exists
        contact = await self.get_contact_by_id(contact_id, user)
        if contact:
            # Update the contact instance with the provided data
            contact.done = body.done
            # Commit the database transaction
            await self.db.commit()
            # Refresh the contact instance with the updated fields
            await self.db.refresh(contact)
        return contact

    async def search_contacts(
        self,
        user: User,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
    ) -> List[Contact]:
        """
        Search for contacts by username, first name, last name, or email.

        Parameters:
        - user: The user whose contacts should be searched.
        - first_name: The first name of the contact to search for.
        - last_name: The last name of the contact to search for.
        - email: The email address of the contact to search for.

        Returns:
        - A list of contacts matching the search criteria.
        """
        stmt = select(Contact).filter_by(user=user)
        if first_name:
            # Perform a case-insensitive search for the first name
            stmt = stmt.filter(Contact.first_name.ilike(f"%{first_name}%"))
        if last_name:
            # Perform a case-insensitive search for the last name
            stmt = stmt.filter(Contact.last_name.ilike(f"%{last_name}%"))
        if email:
            # Perform a case-insensitive search for the email address
            stmt = stmt.filter(Contact.email.ilike(f"%{email}%"))
        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()

    async def get_upcoming_birthdays(self) -> List[Contact]:
        """
        Retrieve a list of contacts with birthdays within the next week.

        Returns:
        - A list of contacts with upcoming birthdays.
        """
        # Get the current date
        today = date.today()
        # Calculate the date one week from today
        next_week = today + timedelta(days=7)
        # Query the database for contacts with birthdays between today and one week from today
        stmt = select(Contact).filter(Contact.birthday.between(today, next_week))
        # Execute the query and retrieve the results
        contacts = await self.db.execute(stmt)
        # Return the list of contacts with upcoming birthdays
        return contacts.scalars().all()
