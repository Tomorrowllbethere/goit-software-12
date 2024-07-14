import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session


import sys
import os
from datetime import datetime, date
# Додавання шляху до директорії з модулем
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from str.database.models import Contact, User
from str.schemas import ContactModel
from str.repository.notes import ( 
    get_contact, 
    get_contacts, 
    find_email, 
    find_name, 
    get_upcoming_birthdays, 
    create_contact, 
    remove_contact, 
    update_contact
)


class TestNotes(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)
        self.contact = Contact(first_name= 'Jon', last_name ='Smith', 
                            email= 'teexample@ex.com', phone_number='0120104000', 
                            date_of_birth=self.test_dateobj, info='it is a test contact')
        
    test_dateobj=datetime.strptime('2002-07-17', "%Y-%m-%d").date()

    async def test_get_contacts(self):
        notes = [Contact(), Contact(), Contact()]
        self.session.query().filter().offset().limit().all.return_value = notes
        result = await get_contacts(skip=0, limit=10, user=self.user, db=self.session)
        self.assertEqual(result, notes)

    async def test_get_contact_found(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await get_contact(contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_get_note_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_contact(contact_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

# get contact for email
    async def test_get_contact_from_email(self):
        contact = Contact(email='exam@com.ua')
        self.session.query().filter().first.return_value = contact
        result = await find_email(contact_email='exam@com.ua', user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_get_contact_from_email_none(self):
        self.session.query().filter().first.return_value = None
        result = await find_email(contact_email='exam@com.ua', user=self.user, db=self.session)
        self.assertIsNone(result)

# get contact for first or last name
    async def test_get_contact_from_name(self):
        contact = Contact(first_name='Ron')
        self.session.query().filter().first.return_value = contact
        result = await find_name(contact_name='Ron', user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_get_contact_from_name_none(self):
        self.session.query().filter().first.return_value = None
        result = await find_name(contact_name='Ron', user=self.user, db=self.session)
        self.assertIsNone(result)
        
# get upcomming_birthdays
    async def test_get_upcomming_birthdays(self):
        notes = [
                 Contact(date_of_birth=datetime.strptime('2002-07-15', "%Y-%m-%d").date()), 
                 Contact(date_of_birth=datetime.strptime('2005-07-17', "%Y-%m-%d").date()),
                 self.contact]
        self.session.query().filter().offset().limit().all.return_value = notes
        results = await get_upcoming_birthdays(skip=0, limit=10, user=self.user, db=self.session)
        # result_dates = [result.date_of_birth for result in results]
        # note_dates = [note.date_of_birth for note in notes]
        # print(f"Result dates: {result_dates}")
        # print(f"Note dates: {note_dates}")
        self.assertEqual(notes, results)

    async def test_get_upcomming_birthdays_none(self):

        self.session.query().filter().offset().limit().all.return_value = None
        results = await get_upcoming_birthdays(skip=0, limit=10, user=self.user, db=self.session)
        self.assertIsNone(results)

    async def test_create_note(self):
        
        body = ContactModel(first_name= 'Ron', last_name ='Smith', 
                            email= 'testexample@ex.com', phone_number='0120104512', 
                            date_of_birth=self.test_dateobj, info='it is a model of contact')
        result = await create_contact(body=body, user=self.user, db=self.session)
        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.info, body.info)
        self.assertEqual(result.email, body.email)
        self.assertTrue(hasattr(result, "id"))

    async def test_remove_note_found(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await remove_contact(contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_remove_note_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await remove_contact(contact_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_update_note_found(self):
        body = ContactModel(first_name= 'Ron', last_name ='Smith', 
                            email= 'testexample@ex.com', phone_number='0111100011' , 
                            date_of_birth=self.test_dateobj , info='it is a model of contact update')
        
        note = Contact(email=body.email)
        self.session.query().filter().first.return_value = note
        self.session.commit.return_value = None
        result = await update_contact(contact_id=1, body=body, user=self.user, db=self.session)
        self.assertEqual(result, note)

    async def test_update_note_not_found(self):
        body = ContactModel(first_name= 'Ron', last_name ='Smith', 
                            email= 'testexample@ex.com', phone_number='0120104512', 
                            date_of_birth=self.test_dateobj, info='it is a model of contact')
        self.session.query().filter().first.return_value = None
        self.session.commit.return_value = None
        result = await update_contact(contact_id=1, body=body, user=self.user, db=self.session)
        self.assertIsNone(result)


#       py tests/test_repository_notes.py 
if __name__ == '__main__':
    unittest.main()

