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


class FrontendLibraryUser(BaseModel):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)

    def __str__(self):
        return self.first_name + " " + self.last_name

    @property
    def borrowed_books(self):
        return self.borrowed_books.all()


class FrontendBook(BaseModel):
    name = models.CharField(max_length=255)
    identifier = models.CharField(max_length=255, blank=True)
    publisher = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    borrowed_by = models.ForeignKey(FrontendLibraryUser, on_delete=models.SET_NULL,
                                    null=True, blank=True, related_name="borrowed_books")
    date_borrowed = models.DateField(null=True, blank=True)
    duration = models.IntegerField(null=True, blank=True)


    def __str__(self):
        return self.name

    @property
    def date_available(self):
        if self.date_borrowed and self.duration:
            return self.date_borrowed + timedelta(days=self.duration)

    @property
    def status(self):
        return "Available" if not self.borrowed_by else "Unavailable"




