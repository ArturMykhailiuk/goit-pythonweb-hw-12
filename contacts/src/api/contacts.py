from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.schemas import ContactBase, ContactUpdate, ContactStatusUpdate, ContactResponse
from src.database.models import User
from src.services.auth import get_current_user
from src.services.contacts import ContactService

router = APIRouter(prefix="/contacts", tags=["contacts"])



@router.get("/", response_model=List[ContactResponse])
async def read_contacts(
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db), 
    user: User = Depends(get_current_user)
):
    """
    Retrieve a list of contacts for the current user.

    Parameters:
    - skip: The number of contacts to skip for pagination.
    - limit: The maximum number of contacts to return.
    - db: Database session dependency.
    - user: The current authenticated user.

    Returns:
    - A list of contacts belonging to the current user.
    """

    contact_service = ContactService(db)
    contacts = await contact_service.get_contacts(skip, limit, user)
    return contacts



@router.get("/{contact_id}", response_model=ContactResponse)
async def read_contact(contact_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    """
    Retrieve a specific contact by its ID for the current user.

    Parameters:
    - contact_id: The ID of the contact to retrieve.
    - db: Database session dependency.
    - user: The current authenticated user.

    Returns:
    - The contact data if found.

    Raises:
    - HTTPException: If the contact is not found.
    """
    # Initialize the contact service with the database session
    contact_service = ContactService(db)
    
    # Attempt to get the contact by ID for the current user
    contact = await contact_service.get_contact(contact_id, user)
    
    # Raise an exception if the contact was not found
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
        
    # Return the found contact
    return contact


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    body: ContactBase, 
    db: AsyncSession = Depends(get_db), 
    user: User = Depends(get_current_user)
):
    """
    Create a new contact for the current user.

    Parameters:
    - body: The JSON payload containing the contact data.
    - db: Database session dependency.
    - user: The current authenticated user.

    Returns:
    - The created contact data.

    Raises:
    - HTTPException: If the contact creation fails.
    """
    # Initialize the contact service with the database session
    contact_service = ContactService(db)
    
    # Attempt to create the contact with the provided data
    contact = await contact_service.create_contact(body, user)
    
    # Raise an exception if the contact creation fails
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Contact creation failed"
        )
        
    # Return the created contact
    return contact


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    body: ContactUpdate,
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Update an existing contact for the current user.

    Parameters:
    - body: The JSON payload containing the contact data to update.
    - contact_id: The ID of the contact to update.
    - db: Database session dependency.
    - user: The current authenticated user.

    Returns:
    - The updated contact data.

    Raises:
    - HTTPException: If the contact is not found.
    """
    # Initialize the contact service with the database session
    contact_service = ContactService(db)
    
    # Attempt to update the contact with the provided data
    contact = await contact_service.update_contact(contact_id, body, user)
    
    # Raise an exception if the contact does not exist
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
        
    # Return the updated contact
    return contact


@router.patch("/{contact_id}", response_model=ContactResponse)
async def update_status_contact(
    body: ContactStatusUpdate,  # The JSON payload containing the contact status update data
    contact_id: int,  # The ID of the contact to update
    db: AsyncSession = Depends(get_db),  # Database session dependency
    user: User = Depends(get_current_user)  # The current authenticated user
):
    """
    Update the status of an existing contact for the current user.

    Parameters:
    - body: The JSON payload containing the contact status update data.
    - contact_id: The ID of the contact to update.
    - db: Database session dependency.
    - user: The current authenticated user.

    Returns:
    - The updated contact data.

    Raises:
    - HTTPException: If the contact does not exist.
    """
    # Initialize the contact service with the database session
    contact_service = ContactService(db)
    
    # Attempt to update the contact status with the provided data
    contact = await contact_service.update_status_contact(contact_id, body, user)
    
    # Raise an exception if the contact does not exist
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
        
    # Return the updated contact
    return contact


@router.delete("/{contact_id}", response_model=ContactResponse)
async def remove_contact(
    contact_id: int,  # The ID of the contact to remove
    db: AsyncSession = Depends(get_db),  # Database session dependency
    user: User = Depends(get_current_user)  # The current authenticated user
):
    """
    Remove an existing contact for the current user.

    Parameters:
    - contact_id: The ID of the contact to remove.
    - db: Database session dependency.
    - user: The current authenticated user.

    Returns:
    - The removed contact data.

    Raises:
    - HTTPException: If the contact does not exist.
    """
    # Initialize the contact service with the database session
    contact_service = ContactService(db)
    
    # Attempt to remove the contact with the provided ID
    contact = await contact_service.remove_contact(contact_id, user)
    
    # Raise an exception if the contact does not exist
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
        
    # Return the removed contact
    return contact


@router.get("/contacts/search/", response_model=List[ContactResponse])
async def search_contacts(
    first_name: Optional[str] = Query(None, description="Contact's first name"),
    last_name: Optional[str] = Query(None, description="Contact's last name"),
    email: Optional[str] = Query(None, description="Contact's email"),
    db: AsyncSession = Depends(get_db),
):
    """
    Search for contacts based on the provided filter criteria.

    Parameters:
    - first_name: Contact's first name.
    - last_name: Contact's last name.
    - email: Contact's email.
    - db: Database session dependency.

    Returns:
    - A list of contacts matching the filter criteria.

    Raises:
    - HTTPException: If the contact does not exist.
    """
    contact_service = ContactService(db)
    return await contact_service.search_contacts(
        first_name=first_name, last_name=last_name, email=email
    )


@router.get("/contacts/upcoming_birthdays/", response_model=List[ContactResponse])
async def upcoming_birthdays(db: AsyncSession = Depends(get_db)):
    """
    Retrieve a list of contacts with upcoming birthdays within the next week.

    Parameters:
    - db: Database session dependency.

    Returns:
    - A list of contacts with upcoming birthdays.

    Raises:
    - HTTPException: If there is an issue retrieving the contacts.
    """
    # Initialize the contact service with the database session
    contact_service = ContactService(db)
    
    # Fetch and return the list of upcoming birthdays
    return await contact_service.get_upcoming_birthdays()
