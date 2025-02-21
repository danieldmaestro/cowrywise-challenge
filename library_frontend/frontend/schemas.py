from datetime import datetime, date
from enum import Enum
from pydantic import Field, field_validator, EmailStr

from typing import Optional

from ninja import Schema

from frontend.models import FrontendLibraryUser
from base.schemas import PageFilter


class EnrollSchema(Schema):
    email: EmailStr
    first_name: str
    last_name: str

    @field_validator('email', mode="after")
    def validate_email(cls, v):
        if FrontendLibraryUser.objects.filter(email=v).exists():
            raise ValueError('A user with this email already exists')
        return v


class CategoriesEnum(str, Enum):
    FICTION = "Fiction"
    TECHNOLOGY = "Technology"
    SCIENCE = "Science"
    NON_FICTION = "Non-Fiction"
    POLITICS = "Politics"
    FANTASY = "Fantasy"


class PublishersEnum(str, Enum):
    WILEY = "Wiley"
    APRESS = "Apress"
    MANNING = "Manning"
    PENGUIN = "Penguin"


class BookSchema(Schema):
    id: int
    identifier: str
    name: str
    publisher: str
    category: str
    status: str


class BookBorrowSchema(Schema):
    email: EmailStr
    duration: int


class BookReturnSchema(Schema):
    email: EmailStr


class BookFilter(PageFilter):
    name__icontains: Optional[str] = Field(None, alias="name")
    category: Optional[CategoriesEnum] = Field(None)
    publisher: Optional[PublishersEnum] = Field(None)


class UserWebhookSchema(Schema):
    email: EmailStr
    first_name: str
    last_name: str
    is_deleted: bool


class BookWebhookSchema(Schema):
    identifier: str
    name: str
    publisher: str
    category: str
    date_borrowed: Optional[date] = None
    duration: Optional[int] = None
    borrowed_by: Optional[UserWebhookSchema] = None
    is_deleted: Optional[bool] = None



