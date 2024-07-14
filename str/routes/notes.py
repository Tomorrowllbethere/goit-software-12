from typing import List
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session
from str.database.models import User
from str.database.db import get_db
from str.schemas import ContactModel, ContactResponse
from str.services.auth import auth_service
import str.repository.notes as repository_notes


router = APIRouter(prefix='/contacts', tags=["contacts"])


@router.get("/search", response_model=ContactResponse|List[ContactResponse], description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def find_contacts(query: str,  db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    """
    This function searches for contacts that match the given query (name or surname)
    for the current authenticated user.
    
    :param query: The query string to search for in contact names or surnames.
    :type query: str.
    :param db: The database session.
    :type db: Session.
    :param current_user: The current authenticated user dependency. 
    :type current_user: User.
    :return: The contact that match the query.
    :rtype: Contact.
    :raises HTTPException: If no contacts are found that match the query, raises a 404 HTTP exception.
    """
    contacts = await repository_notes.find_name(query, current_user, db)
    if  contacts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contacts

@router.get("/email", response_model=ContactResponse|List[ContactResponse], description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def find_contacts_for_email(contact_email:str,  db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    """
    Retrieve contact by email.

    :param contact_email: The email to search for.
    :type contact_email: str
    :param db: The database session dependency.
    :type db: Session
    :param current_user: The current authenticated user dependency.
    :type current_user: User
    :return: The contact found with the given email.
    :rtype: ContactResponse
    :raises HTTPException: If no contacts are found with the given email.
    """
    contacts = await repository_notes.find_email(contact_email, current_user, db)
    if  contacts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contacts

@router.get("/upcoming", response_model=ContactResponse|List[ContactResponse])
async def upcoming_birthdays_contacts(skip: int = None, limit: int = None, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    """
    Retrieve contacts with upcoming birthdays.

    :param skip: The number of records to skip.
    :type skip: int, optional
    :param limit: The maximum number of records to return.
    :type limit: int, optional
    :param db: The database session dependency.
    :type db: Session
    :param current_user: The current authenticated user dependency.
    :type current_user: User
    :return: The contacts upcoming birthdays found.
    :rtype: [List[ContactResponse]
    :raises HTTPException: If no contacts are found.
    """
    contacts = await repository_notes.get_upcoming_birthdays(skip, limit, current_user, db)
    if  contacts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contacts

@router.get("/", response_model=List[ContactResponse], description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def read_contacts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    """
    Retrieve a list of contacts.

    :param skip: The number of records to skip.
    :type skip: int, optional
    :param limit: The maximum number of records to return.
    :type limit: int, optional
    :param db: The database session dependency.
    :type db: Session, optional
    :param current_user: The current authenticated user dependency.
    :type current_user: User, optional
    :return: A list of contacts.
    :rtype: List[ContactResponse]
    """
    contacts = await repository_notes.get_contacts(skip, limit, current_user, db)
    return contacts

@router.get("/{contact_id}", response_model=ContactResponse)
async def read_contact(contact_id: int, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    """
    Retrieve a specific contact by ID.

    :param contact_id: The ID of the contact to retrieve.
    :type contact_id: int
    :param db: The database session dependency.
    :type db: Session, optional
    :param current_user: The current authenticated user dependency.
    :type current_user: User, optional
    :return: The contact found with the given ID.
    :rtype: ContactResponse
    :raises HTTPException: If no contact is found with the given ID.
    """
    contact = await repository_notes.get_contact(contact_id, current_user, db)
    if  contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED, description='No more than 3 requests per minute',
            dependencies=[Depends(RateLimiter(times=3, seconds=60))] )
async def create_contact(body: ContactModel, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    """
    Create a new contact.

    :param body: The contact data to create.
    :type body: ContactModel
    :param db: The database session dependency.
    :type db: Session, optional
    :param current_user: The current authenticated user dependency.
    :type current_user: User, optional
    :return: The created contact.
    :rtype: ContactResponse
    """
    return await repository_notes.create_contact(body, current_user,db)

@router.put("/{contact_id}", response_model=ContactResponse, description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def update_contact(body: ContactModel, contact_id: int, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    """
    Update an existing contact.

    :param body: The contact data to update.
    :type body: ContactModel
    :param contact_id: The ID of the contact to update.
    :type contact_id: int
    :param db: The database session dependency.
    :type db: Session, optional
    :param current_user: The current authenticated user dependency.
    :type current_user: User, optional
    :return: The updated contact.
    :rtype: ContactResponse
    :raises HTTPException: If no contact is found with the given ID.
    """
    contact = await repository_notes.update_contact(contact_id, body, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact

@router.delete("/{contact_id}", response_model=ContactResponse)
async def remove_contact(contact_id: int, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    """
    Delete a contact.

    :param contact_id: The ID of the contact to delete.
    :type contact_id: int
    :param db: The database session dependency.
    :type db: Session, optional
    :param current_user: The current authenticated user dependency.
    :type current_user: User, optional
    :return: The deleted contact.
    :rtype: ContactResponse
    :raises HTTPException: If no contact is found with the given ID.
    """
    contact = await repository_notes.remove_contact(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact




