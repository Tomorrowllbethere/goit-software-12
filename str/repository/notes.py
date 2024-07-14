from typing import List, Optional
import datetime as dt
from sqlalchemy import or_, and_
from sqlalchemy.orm import Session


from str.database.models import Contact, User
from str.schemas import ContactModel


async def get_contacts(skip: int, limit: int, user: User, db: Session) -> List[Contact]:
    """
    Retrieves a list of contacts for a specific user with specified pagination parameters.

    :param skip: The number of contacts to skip.
    :type skip: int
    :param limit: The maximum number of contacts to return.
    :type limit: int
    :param user: The user to retrieve conatcts for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: A list of contacts.
    :rtype: List[Contact]
    """
    return db.query(Contact).filter(Contact.user_id == user.id).offset(skip).limit(limit).all()


async def get_contact(contact_id: int, user: User, db: Session) -> Contact|None:
    """
    Retrieves a single contact with the specified ID for a specific user.

    :param contact_id: The ID of the contact to retrieve.
    :type contact_id: int
    :param user: The user to retrieve the contact for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: The contact with the specified ID, or None if it does not exist.
    :rtype: Contact | None
    """
    return db.query(Contact).filter(and_(Contact.user_id == user.id, Contact.id == contact_id)).first()


async def find_name(contact_name: str, user: User, db: Session) -> Contact|None:
    """
    Retrieves a contact matching the given name for a specific user.

    :param contact_name: The name of the contact to retrieve.
    :type contact_name: str
    :param user: The user to retrieve the contact for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: Returns the first contact matching the given first name or last name., or None if it does not exist.
    :rtype: Contact | None
    """
    contacts = db.query(Contact).filter(
        or_(
            and_(Contact.user_id == user.id, Contact.first_name.ilike(f"%{contact_name}%")),
            and_(Contact.user_id == user.id, Contact.last_name.ilike(f"%{contact_name}%"))
        )
    ).first()
    return contacts
     

async def find_email(contact_email:str, user: User, db: Session) -> Contact|None:
    """
    Retrieves a contact matching the given email for a specific user.

    :param contact_email: Email of the contact to search.
    :type contact_email: str
    :param user: The user to retrieve the contact for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: Returns the first contact matching the given email, or None if it does not exist.
    :rtype: Contact | None
    """
    return db.query(Contact).filter(and_(Contact.user_id == user.id, Contact.email.ilike(f"%{contact_email}%"))).first()


async def get_upcoming_birthdays(skip: int, limit: int, user: User, db: Session) -> List[Contact]|None:
    """
    Retrieves a list of 7-days-upcoming contacts birthdays for a specific user with specified pagination parameters.

    :param skip: The number of contacts to skip.
    :type skip: int
    :param limit: The maximum number of contacts to return.
    :type limit: int
    :param user: The user to retrieve contacts for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: A list of contacts birthdays, or None, if not exist upcoming birthdays.
    :rtype: List[Contact]|None
    """
    current_year = dt.datetime.now().year
    tdate= dt.datetime.today().date()
    upcoming_birthdays=[] # створюємо список для результатів
    contacts:Contact|List[Contact] = db.query(Contact).filter(Contact.user_id == user.id).offset(skip).limit(limit).all()
    if contacts:
        for contact in contacts: # перебираємо користувачів
                birthdate:Optional[dt.date] = contact.date_of_birth # отримуємо дату народження людини  
                if birthdate is not None:
                    new_bdate = birthdate.replace(year=current_year)
                    days_between=(new_bdate-tdate).days # рахуємо різницю між зараз і днем народження цьогоріч у днях
                    if 0<=days_between<7: # якщо день народження протягом 7 днів від сьогодні
                        upcoming_birthdays.append(contact) 
                            # Додаємо запис у список.
        if not upcoming_birthdays :
            return "There are no contacts scheduled for greetings in the next week."
        else:
            return upcoming_birthdays


async def create_contact(body: ContactModel, user: User, db: Session) -> Contact:
    """
    Creates a new contact for a specific user.

    :param body: The data for the contact to create.
    :type body: ContactModel
    :param user: The user to create the contact for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: The newly created contact.
    :rtype: Contact
    """
    contact = Contact(first_name=body.first_name, 
                      last_name=body.last_name, 
                      email=body.email, 
                      phone_number=body.phone_number, 
                      date_of_birth=body.date_of_birth, 
                      info=body.info,
                      user_id=user.id)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def remove_contact(contact_id: int, user: User, db: Session) -> Contact | None:
    """
    Removes a single contact with the specified ID for a specific user.
    :param contact_id: The ID of the contact to remove.
    :type contact_id: int
    :param user: The user to remove the contact for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: The removed contact, or None if it does not exist.
    :rtype: Contact | None
    """
    contact = db.query(Contact).filter(and_(Contact.user_id == user.id, Contact.id == contact_id)).first()
    if contact:
        db.delete(contact)
        db.commit()
    return contact


async def update_contact(contact_id: int,  body: ContactModel, user: User, db: Session) -> Contact | None:
    """
    Update a single contact with the specified ID for a specific user.

    :param contact_id: The ID of the contact to update.
    :type contact_id: int
    :param body: The updated data for the contact.
    :type body: ContactModel
    :param user: The user to update the contact for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: The updated contact, or None if it does not exist.
    :rtype: Contact | None
    """
    contact = db.query(Contact).filter(and_(Contact.user_id == user.id, Contact.id == contact_id)).first()
    if contact:      
        contact.first_name = body.first_name 
        contact.last_name = body.last_name
        contact.email  = body.email
        contact.phone_number = body.phone_number
        contact.date_of_birth = body.date_of_birth
        contact.info = body.info
        db.commit()
    return contact