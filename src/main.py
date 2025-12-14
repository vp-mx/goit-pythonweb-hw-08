"""
ContactHub API - REST API for managing personal and business contacts.

This module provides endpoints for CRUD operations on contacts,
searching capabilities, and birthday tracking functionality.
"""

from fastapi import FastAPI, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import date, timedelta
from typing import List

from connection import get_db
from models import Contact
from schemas import ContactResponse, ContactBase, ContactUpdate

app = FastAPI(
    title="ContactHub API",
    description="REST API for managing personal and business contacts with search and birthday tracking",
    version="1.0.0",
)


def _is_birthday_within_days(
        birthday: date | None, current_date: date, days: int
) -> bool:
    """Check if a birthday falls within the specified number of days from current date.

    :param birthday: The birthday date to check
    :param current_date: Reference date (typically today)
    :param days: Number of days to look ahead
    :return: True if birthday is within the specified range, False otherwise
    :rtype: bool
    """
    if birthday is None:
        return False

    end_date = current_date + timedelta(days=days)
    birthday_this_year = birthday.replace(year=current_date.year)

    if birthday_this_year < current_date:
        birthday_this_year = birthday_this_year.replace(year=current_date.year + 1)

    return current_date <= birthday_this_year <= end_date


@app.post(
    "/contacts/",
    response_model=ContactResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Contacts"],
    summary="Create a new contact",
    description="Add a new contact to the database. Email must be unique.",
)
def create_contact(contact: ContactBase, db: Session = Depends(get_db)):
    """Create a new contact entry in the database.

    :param contact: Contact data to create
    :param db: Database session
    :return: The created contact
    :rtype: ContactResponse
    :raises HTTPException: If email is already registered (status 400)
    """
    existing_contact = db.query(Contact).filter(Contact.email == contact.email).first()
    if existing_contact:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Contact with email {contact.email} already exists",
        )

    new_contact = Contact(**contact.model_dump())
    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)
    return new_contact


@app.get(
    "/contacts/",
    response_model=list[ContactResponse],
    tags=["Contacts"],
    summary="Retrieve all contacts",
    description="Get a paginated list of all contacts in the database",
)
def get_contacts_list(
        skip: int = Query(0, ge=0, description="Number of records to skip"),
        limit: int = Query(
            100, ge=1, le=500, description="Maximum number of records to return"
        ),
        db: Session = Depends(get_db),
):
    """Retrieve a list of contacts with pagination support.

    :param skip: Number of records to skip (for pagination)
    :param limit: Maximum number of records to return
    :param db: Database session
    :return: List of contacts
    :rtype: list[ContactResponse]
    """
    contacts = db.query(Contact).offset(skip).limit(limit).all()
    return contacts


@app.get(
    "/contacts/search/",
    response_model=list[ContactResponse],
    tags=["Search"],
    summary="Search contacts",
    description="Search contacts by first name, last name, or email address",
)
def search_contacts_by_query(
        query: str = Query(
            ...,
            min_length=3,
            description="Search query - minimum 3 characters (searches in name, surname, email)",
        ),
        db: Session = Depends(get_db),
):
    """Search for contacts matching the provided query string.

    The search is case-insensitive and looks for matches in:
    - First name
    - Last name
    - Email address

    :param query: Search string (minimum 3 characters)
    :param db: Database session
    :return: List of matching contacts
    :rtype: list[ContactResponse]
    :raises HTTPException: If no contacts match the query (status 404)
    """
    search_pattern = f"%{query}%"
    matching_contacts = (
        db.query(Contact)
        .filter(
            (Contact.first_name.ilike(search_pattern))
            | (Contact.last_name.ilike(search_pattern))
            | (Contact.email.ilike(search_pattern))
        )
        .all()
    )

    if not matching_contacts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No contacts found matching '{query}'",
        )

    return matching_contacts


@app.get(
    "/contacts/birthdays/",
    response_model=list[ContactResponse],
    tags=["Search"],
    summary="Get upcoming birthdays",
    description="Retrieve contacts with birthdays in the next 7 days",
)
def get_upcoming_birthdays(db: Session = Depends(get_db)):
    """Retrieve contacts who have birthdays coming up in the next 7 days.

    This endpoint checks all contacts and returns those whose birthday
    falls within the next week, accounting for year transitions.

    :param db: Database session
    :return: List of contacts with upcoming birthdays
    :rtype: List[ContactResponse]
    """
    current_date = date.today()
    days_to_check = 7

    contacts = db.query(Contact).all()
    contacts_with_upcoming_birthdays = [
        contact
        for contact in contacts
        if _is_birthday_within_days(contact.birthday, current_date, days_to_check)
    ]

    return contacts_with_upcoming_birthdays


@app.get(
    "/contacts/{contact_id}",
    response_model=ContactResponse,
    tags=["Contacts"],
    summary="Get contact by ID",
    description="Retrieve a specific contact by their unique identifier",
)
def get_contact_by_id(contact_id: int, db: Session = Depends(get_db)):
    """Retrieve a single contact by ID.

    :param contact_id: The unique identifier of the contact
    :param db: Database session
    :return: The requested contact
    :rtype: ContactResponse
    :raises HTTPException: If contact with given ID doesn't exist (status 404)
    """
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contact with ID {contact_id} not found",
        )
    return contact


@app.put(
    "/contacts/{contact_id}",
    response_model=ContactResponse,
    tags=["Contacts"],
    summary="Update contact",
    description="Update an existing contact's information",
)
def update_contact_by_id(
        contact_id: int, contact: ContactUpdate, db: Session = Depends(get_db)
):
    """Update an existing contact's information.

    Only provided fields will be updated. Unset fields are ignored.

    :param contact_id: The unique identifier of the contact to update
    :param contact: Updated contact data
    :param db: Database session
    :return: The updated contact
    :rtype: ContactResponse
    :raises HTTPException: If contact with given ID doesn't exist (status 404)
    """
    existing_contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if existing_contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contact with ID {contact_id} not found",
        )

    update_data = contact.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(existing_contact, field, value)

    db.commit()
    db.refresh(existing_contact)
    return existing_contact


@app.delete(
    "/contacts/{contact_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Contacts"],
    summary="Delete contact",
    description="Remove a contact from the database",
)
def delete_contact_by_id(contact_id: int, db: Session = Depends(get_db)):
    """Delete a contact from the database.

    :param contact_id: The unique identifier of the contact to delete
    :param db: Database session
    :return: None
    :rtype: None
    :raises HTTPException: If contact with given ID doesn't exist (status 404)
    """
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contact with ID {contact_id} not found",
        )

    db.delete(contact)
    db.commit()
    return None


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
