import  os
import binascii
from datetime import timedelta

from django.db import models

from base.base_model import BaseModel


# Create your models here.

CATEGORIES = [
    "Fiction",
    "Technology",
    "Non-Fiction",
    "Fantasy",
    "Science",
    "Other",
]


class BackendLibraryUser(BaseModel):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)

    def __str__(self):
        return self.first_name + " " + self.last_name

    @property
    def borrowed_books(self):
        return self.borrowed_books.all()


class BackendBook(BaseModel):
    name = models.CharField(max_length=255)
    identifier = models.CharField(max_length=255, blank=True)
    publisher = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    borrowed_by = models.ForeignKey(BackendLibraryUser, on_delete=models.SET_NULL,
                                    null=True, blank=True, related_name="borrowed_books")
    date_borrowed = models.DateField(null=True, blank=True)
    duration = models.IntegerField(null=True, blank=True)

    @staticmethod
    def generate_unique_identifier():
        unique = False
        unique_identifier = None
        while not unique:
            number = binascii.b2a_hex(os.urandom(8)).upper().decode("utf-8")
            unique_identifier = f"BOOK-{number}"
            if not BackendBook.objects.filter(identifier=unique_identifier).exists():
                unique = True
        return unique_identifier

    def __str__(self):
        return self.name

    @property
    def date_available(self):
        if self.date_borrowed and self.duration:
            return self.date_borrowed + timedelta(days=self.duration)

    @property
    def status(self):
        return "Available" if not self.borrowed_by else "Unavailable"



    def save(self, *args, **kwargs):
        if not self.identifier:
            self.identifier = BackendBook.generate_unique_identifier()
        super(BackendBook, self).save(*args, **kwargs)

