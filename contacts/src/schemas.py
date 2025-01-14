from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict, EmailStr


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
    done: bool


class ContactStatusUpdate(BaseModel):
    done: bool


class ContactResponse(ContactBase):
    id: int
    done: bool
    created_at: datetime | None
    updated_at: Optional[datetime] | None

    model_config = ConfigDict(from_attributes=True)
