from datetime import date
from enum import Enum
from pydantic import Field, field_validator, EmailStr

from typing import List, Optional

from ninja import Schema

from .models import BackendLibraryUser, BackendBook
from base.schemas import PageFilter


class EnrollSchema(Schema):
    email: EmailStr
    first_name: str
    last_name: str

    @field_validator('email', mode="after")
    def validate_email(cls, v):
        if BackendLibraryUser.objects.filter(email=v).exists():
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


class AddBookSchema(Schema):
    name: str
    publisher: str
    category: CategoriesEnum


class LibraryUserSchema(Schema):
    id: int
    email: EmailStr
    first_name: str
    last_name: str


class BookSchema(Schema):
    id: int
    identifier: str
    name: str
    publisher: str
    category: str
    status: str


class BookSchemaWithBorrower(BookSchema):
    borrowed_by: Optional[LibraryUserSchema] = None
    date_borrowed: Optional[date] = None
    date_available: Optional[date] = None


class LibraryUserWithBooksSchema(LibraryUserSchema):
    borrowed_books: List[BookSchema]


class SearchFilter(PageFilter):
    search: Optional[str] = None


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

