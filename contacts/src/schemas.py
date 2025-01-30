from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from src.database.models import UserRole


class ContactBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    birthday: date
    additional_info: Optional[str] = None


class ContactCreate(ContactBase):
    done: bool


class ContactUpdate(ContactBase):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    birthday: Optional[date] = None
    additional_info: Optional[str] = None
    done: Optional[bool] = None


class ContactStatusUpdate(BaseModel):
    done: bool


class ContactResponse(ContactBase):
    id: int
    done: bool
    created_at: datetime | None
    updated_at: Optional[datetime] | None

    model_config = ConfigDict(from_attributes=True)
    
    
# Схема користувача
class User(BaseModel):
    id: int
    username: str
    email: str
    avatar: str

    model_config = ConfigDict(from_attributes=True)

# Схема для запиту реєстрації
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

# Схема для токену
class Token(BaseModel):
    access_token: str
    token_type: str

class RequestEmail(BaseModel):
    email: EmailStr
    
class ResetPassword(BaseModel):
    token: str
    new_password: str
    
class UserModel(BaseModel):
    id: int
    username: str
    role: UserRole