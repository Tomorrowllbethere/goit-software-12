import unittest
from unittest.mock import MagicMock
import sys
import os
# Додавання шляху до директорії з модулем
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from datetime import datetime, date

from str.database.models import User
from str.schemas import UserModel
from str.repository.users import (
    get_user_by_email,
    create_user,
    confirmed_email,
    update_token,
    update_avatar)

class TestNotes(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1, username= 'Eric Tomas', email= 'example@meta.com', password='12345usertest')
    
    async def test_get_user_by_email(self):
        user = self.user
        self.session.query().filter().first.return_value = self.user
        result = await get_user_by_email(email="example@meta.com", db=self.session)
        self.assertEqual(result, user)
    
    async def test_get_user_by_email_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_user_by_email(email="example@meta.com", db=self.session)
        self.assertIsNone(result)

    async def test_create_user(self):
        user = UserModel(username= 'Irys Toreno', email= 'eeee0123@meta.com', password='usercst001')
        self.session.query().filter().first.return_value = self.user
        result = await create_user(body=user, db=self.session)
        self.assertEqual(result.email, user.email)
        self.assertEqual(result.username, user.username)
        self.assertEqual(result.password, user.password)

    async def test_update_avatar(self):
        user = User(username= 'Irys Toreno', email= 'eeee0123@meta.com', password='usercst001')
        self.session.query().filter().first.return_value = user
        result = await update_avatar(email=user.email, url='http:\\localhost:8000\\user1.jpg', db=self.session)
        self.assertEqual(result.email, user.email)
        self.assertEqual(result.username, user.username)
        self.assertEqual(result.password, user.password)
        self.assertIsNotNone(result.avatar)

    async def test_confirmed_email(self):
        user = self.user
        self.session.query().filter().first.return_value = user
        result = await confirmed_email(email=user.email, db=self.session)
        self.assertEqual(result.email, user.email)

    async def test_not_confirmed_email(self):
        self.session.query().filter().first.return_value = None
        result = await confirmed_email(email='test@ijk.cm', db=self.session)
        self.assertIsNone(result)

    async def test_update_token(self):
        user = self.user
        self.session.query().filter().first.return_value = user
        result = await update_token(user= self.user, token= 'idCIH123154 HLDJcoih123456', db=self.session)
        self.assertEqual(result.email, user.email)
        self.assertIsNotNone(result.refresh_token)
    

#       py tests/test_repository_users.py 
if __name__ == '__main__':
    unittest.main()
