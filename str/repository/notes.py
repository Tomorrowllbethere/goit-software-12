from typing import List
import datetime as dt
from sqlalchemy import or_, and_
from sqlalchemy.orm import Session


from ..database.models import Contact, User
from ..schemas import ContactModel


async def get_contacts(skip: int, limit: int, user: User, db: Session) -> List[Contact]:
    return db.query(Contact).filter(Contact.user_id == user.id).offset(skip).limit(limit).all()


async def get_contact(contact_id: int, user: User, db: Session) -> Contact:
    return db.query(Contact).filter(and_(Contact.user_id == user.id, Contact.id == contact_id)).first()


async def find_name(contact_name: str, user: User, db: Session) -> Contact|List[Contact]:
    contacts = db.query(Contact).filter(
        or_(
            and_(Contact.user_id == user.id, Contact.first_name.ilike(f"%{contact_name}%")),
            and_(Contact.user_id == user.id, Contact.last_name.ilike(f"%{contact_name}%"))
        )
    ).first()
    return contacts
     

async def find_email(contact_email:str, user: User, db: Session) -> Contact|List[Contact]:
    return db.query(Contact).filter(and_(Contact.user_id == user.id, Contact.email.ilike(f"%{contact_email}%"))).first()


async def get_upcoming_birthdays(skip: int, limit: int, user: User, db: Session) -> List[Contact]:
        current_year = dt.datetime.now().year
        tdate= dt.datetime.today().date()
        upcoming_birthdays=[] # створюємо список для результатів
        contacts:Contact|List[Contact] = db.query(Contact).filter(Contact.user_id == user.id).offset(skip).limit(limit).all()
        if contacts:
            for contact in contacts: # перебираємо користувачів
                    birthdate = contact.date_of_birth # отримуємо дату народження людини   
                    new_bdate = birthdate.replace(year=current_year).date()
                    days_between=(new_bdate-tdate).days # рахуємо різницю між зараз і днем народження цьогоріч у днях
                    if 0<=days_between<7: # якщо день народження протягом 7 днів від сьогодні
                        upcoming_birthdays.append(contact) 
                        # Додаємо запис у список.
        if not upcoming_birthdays :
            return "There are no contacts scheduled for greetings in the next week."
        else:
            return upcoming_birthdays


async def create_contact(body: ContactModel, user: User, db: Session) -> Contact:
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
    contact = db.query(Contact).filter(and_(Contact.user_id == user.id, Contact.id == contact_id)).first()
    if contact:
        db.delete(contact)
        db.commit()
    return contact


async def update_contact(contact_id: int,  body: ContactModel, user: User, db: Session) -> Contact | None:
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

