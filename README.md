# Contacts API

This project is a REST API for managing contacts, built using FastAPI and SQLAlchemy. The API allows you to create, read, update, and delete contacts, as well as search for contacts by name, last name, or email, and get a list of contacts with upcoming birthdays.

## Features

- Create a new contact
- Get a list of all contacts
- Get a contact by ID
- Update an existing contact
- Delete a contact
- Search contacts by name, last name, or email
- Get a list of contacts with birthdays in the next 7 days

## Requirements

- Python 3.8+
- PostgreSQL

## Endpoints

### Create a new contact

    URL: contacts
    Method: POST
    Request Body:
    {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone": "123-456-7890",
        "birthday": "1990-01-01",
        "additional_info": "Some additional info"
    }

### Get a list of all contacts

    URL: contacts
    Method: GET
    Query Parameters:
        - skip (optional): Number of records to skip
        - limit (optional): Maximum number of records to return

### Get a contact by ID

    URL: /contacts/{contact_id}
    Method: GET

### Update an existing contact

    URL: /contacts/{contact_id}
    Method: PUT
    Request Body:
    {
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "jane.doe@example.com",
        "phone": "987-654-3210",
        "birthday": "1991-02-02",
        "additional_info": "Updated additional info"
    }

### Delete a contact

    URL: /contacts/{contact_id}
    Method: DELETE

### Search contacts

    URL: /contacts/search/
    Method: GET
    Query Parameters:
        - first_name (optional): First name to search for
        - last_name (optional): Last name to search for
        - email (optional): Email to search for

### Get contacts with upcoming birthdays

    URL: /contacts/upcoming_birthdays/
    Method: GET
