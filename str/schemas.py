# схеми. валідація вхідних і вихідних  даних
from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr, constr

import re

class ContactBase(BaseModel):
    first_name: str = Field(max_length=50)
    last_name:str = Field(max_length=50)
    email: EmailStr
    phone_number:str = Field(pattern=r'^\+?1?\d{9,15}$')
    date_of_birth: date
    
class ContactModel(ContactBase):
    info: Optional[constr(max_length=350)]
    
class ContactResponse(ContactBase):
    id: int

    class Config:
        from_attributes = True

class UserModel(BaseModel):
    username: str = Field(min_length=5, max_length=16)
    email: str
    password: str = Field(min_length=6, max_length=10)


class UserDb(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    avatar: str

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    user: UserDb
    detail: str = "User successfully created"


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RequestEmail(BaseModel):
    email: EmailStr

