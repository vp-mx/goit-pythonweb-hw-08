from pydantic import BaseModel, Field, EmailStr
from datetime import date
from typing import Optional


class ContactBase(BaseModel):
    """Base schema for a contact in the address book."""

    first_name: str = Field(min_length=3, max_length=50)
    last_name: str = Field(min_length=3, max_length=50)
    email: EmailStr
    phone: str = Field(min_length=10, max_length=20)
    birthday: date
    additional_data: Optional[str] = None


class ContactUpdate(BaseModel):
    """Schema for updating an existing contact. All fields are optional."""

    first_name: Optional[str] = Field(None, min_length=3, max_length=50)
    last_name: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, min_length=10, max_length=20)
    birthday: Optional[date] = None
    additional_data: Optional[str] = None


class ContactResponse(ContactBase):
    """Schema for returning contact data in responses."""

    id: int

    class Config:
        from_attributes = True
