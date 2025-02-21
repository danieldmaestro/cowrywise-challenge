import requests
import json
from django.utils import timezone
from ninja.errors import ValidationError
from .models import FrontendLibraryUser, FrontendBook
from base.paginate_response import get_page
from base.schemas import DefaultResponse

BACKEND_BOOKS_WEBHOOK_URL = "http://127.0.0.1:2000/api/backend/webhook/books"
BACKEND_USER_WEBHOOK_URL = "http://127.0.0.1:2000/api/backend/webhook/users"

class FrontendLibraryService:

    def enroll_library_user(self, payload):
        lib_user = FrontendLibraryUser.objects.create(**payload.dict())
        self.update_user_on_backend_api(lib_user)
        return DefaultResponse(message="Library user enrolled")

    def get_all_available_books(self, filters, page_schema):
        books = FrontendBook.objects.filter(borrowed_by__isnull=True).filter(**filters.dict())
        data = get_page(books, filters, page_schema)
        return DefaultResponse(data=data, message="Available books retrieved successfully")

    def get_book_by_unique_identifier(self, identifier):
        try:
            return FrontendBook.objects.get(identifier=identifier)
        except FrontendBook.DoesNotExist:
            raise ValidationError(f'Book with identifier "{identifier}" does not exist')


    def get_book_by_id(self, book_id):
        try:
            return FrontendBook.objects.get(id=book_id)
        except FrontendBook.DoesNotExist:
            raise ValidationError(f'Book with id "{book_id}" does not exist')


    def get_book_detail(self, book_unique_id):
        book = self.get_book_by_unique_identifier(book_unique_id)
        return DefaultResponse(data=book, message="Book removed successfully")


    def borrow_book(self, book_unique_id, payload):
        book = self.get_book_by_unique_identifier(book_unique_id)
        if book.borrowed_by:
            raise ValidationError(f'Book with identifier "{book_unique_id}" is already borrowed')

        borrowed_by = FrontendLibraryUser.objects.filter(email__iexact=payload.email).first()
        if not borrowed_by:
            raise ValidationError('A user with this email does not exist')
        book.borrowed_by = borrowed_by
        book.date_borrowed = timezone.now().date()
        book.duration = payload.duration
        book.save()
        self.update_book_on_backend_api(book)
        return DefaultResponse(message="Book borrowed successfully")

    def return_book(self, book_unique_id, payload):
        book = self.get_book_by_unique_identifier(book_unique_id)
        if not book.borrowed_by:
            raise ValidationError(f'Book with identifier "{book_unique_id}" is already available')

        if book.borrowed_by.email != payload.email:
            raise ValidationError(f'You cannot return a book that wasn\'t borrowed by you')
        book.borrowed_by = None
        book.date_borrowed = None
        book.duration = None
        book.save()
        self.update_book_on_backend_api(book)
        return DefaultResponse(message="Book returned successfully")

    def handle_webhook_event_for_book(self, payload):
        payload_dict = payload.dict()
        identifier = payload_dict.get('identifier')
        borrowed_by = payload_dict.pop('borrowed_by', None)
        book = FrontendBook.objects.filter(identifier=identifier).first()
        user = None
        if borrowed_by:
            user = FrontendLibraryUser.objects.filter(email=borrowed_by.email).first()
            if not user:
                user = FrontendLibraryUser.objects.create(**borrowed_by.dict())

        if not book:
            book = FrontendBook.objects.create(**payload_dict, borrowed_by=user)
        else:
            for attr, value in payload_dict.items():
                setattr(book, attr, value)
            book.borrowed_by = user
            book.save()
        return DefaultResponse(message="Book updated successfully")


    def update_book_on_backend_api(self, instance):
        date_borrowed = instance.date_borrowed.isoformat() if instance.date_borrowed else None
        borrowed_by = {
            "email": instance.borrowed_by.email,
            "first_name": instance.borrowed_by.first_name,
            "last_name": instance.borrowed_by.last_name,
            "is_deleted": instance.borrowed_by.is_deleted,
        } if instance.borrowed_by else None

        book_data = {
            "identifier": instance.identifier,
            "name": instance.name,
            "publisher": instance.publisher,
            "category": instance.category,
            "date_borrowed": date_borrowed,
            "duration": instance.duration,
            "borrowed_by": borrowed_by,
            "is_deleted": instance.is_deleted,
        }
        self.send_webhook_data(book_data, BACKEND_BOOKS_WEBHOOK_URL)

    def update_user_on_backend_api(self, instance):
        user_data = {
            "email": instance.email,
            "first_name": instance.first_name,
            "last_name": instance.last_name,
            "is_deleted": instance.is_deleted,
        }
        self.send_webhook_data(user_data, BACKEND_USER_WEBHOOK_URL)

    def send_webhook_data(self, payload, url):
        headers = {"Content-Type": "application/json"}
        try:
            response = requests.post(url, data=json.dumps(payload), headers=headers)
            response.raise_for_status()
            print(f"Webhook sent successfully: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Failed to send webhook: {e}")




