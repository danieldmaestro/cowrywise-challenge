import json
import requests
from django.db.models import Q
from ninja.errors import ValidationError
from .models import BackendLibraryUser, BackendBook
from base.paginate_response import get_page
from base.schemas import DefaultResponse


FRONTEND_BOOK_WEBHOOK_URL = "http://host.docker.internal:2001/api/frontend/webhook/books"

class BackendLibraryService:

    def get_book_by_unique_identifier(self, identifier):
        try:
            return BackendBook.objects.get(identifier=identifier)
        except BackendBook.DoesNotExist:
            raise ValidationError(f'Book with identifier "{identifier}" does not exist')


    def get_book_by_id(self, book_id):
        try:
            return BackendBook.objects.get(id=book_id)
        except BackendBook.DoesNotExist:
            raise ValidationError(f'Book with id "{book_id}" does not exist')


    def create_book(self, payload):
        book = BackendBook.objects.create(**payload.dict())
        self.update_book_on_frontend_api(book)
        return DefaultResponse(message="Book created successfully")


    def get_book_detail(self, book_unique_id):
        book = self.get_book_by_unique_identifier(book_unique_id)
        return DefaultResponse(data=book, message="Book detail retrieved successfully")

    def remove_book(self, book_unique_id):
        book = self.get_book_by_unique_identifier(book_unique_id)
        book.is_deleted = True
        book.save()
        self.update_book_on_frontend_api(book)
        return DefaultResponse(message="Book removed successfully")

    def get_all_available_books(self, filters, page_schema):
        books = BackendBook.objects.filter(borrowed_by__isnull=True).filter(**filters.dict())
        data = get_page(books, filters, page_schema)
        return DefaultResponse(data=data, message="Available books retrieved successfully")


    def get_all_books(self, filters, page_schema):
        books = BackendBook.objects.filter(**filters.dict())
        data = get_page(books, filters, page_schema)
        return DefaultResponse(data=data, message="All books retrieved successfully")


    def get_all_unavailable_books(self, filters, page_schema):
        books = BackendBook.objects.filter(borrowed_by__isnull=False).filter(**filters.dict())
        data = get_page(books, filters, page_schema)
        return DefaultResponse(data=data, message="Unavailable books retrieved successfully")

    def get_all_enrolled_users(self, filters, page_schema):
        filters_dict = filters.dict()
        search = filters_dict.pop('search', None)
        if search:
            users = BackendLibraryUser.objects.filter(
                Q(first_name__icontains=search) | Q(last_name__icontains=search) | Q(email__icontains=search)
            ).filter(**filters.dict())
        else:
            users = BackendLibraryUser.objects.filter(**filters.dict())
        data = get_page(users, filters, page_schema)
        return DefaultResponse(data=data, message="Enrolled users retrieved successfully")

    def get_all_enrolled_users_with_borrowed_books(self, filters, page_schema):
        filters_dict = filters.dict()
        search = filters_dict.pop('search', None)
        if search:
            users = BackendLibraryUser.objects.filter(
                Q(first_name__icontains=search) | Q(last_name__icontains=search) | Q(email__icontains=search)
            ).filter(**filters.dict()).prefetch_related('borrowed_books')
        else:
            users = BackendLibraryUser.objects.filter(**filters.dict()).prefetch_related('borrowed_books')
        data = get_page(users, filters, page_schema)
        return DefaultResponse(data=data, message="Enrolled users with borrowed books retrieved successfully")

    def handle_webhook_event_for_book(self, payload):
        payload_dict = payload.dict()
        identifier = payload_dict.get('identifier')
        borrowed_by = payload_dict.pop('borrowed_by', None)
        book = BackendBook.objects.filter(identifier=identifier).first()
        user = None
        if borrowed_by:
            user = BackendLibraryUser.objects.filter(email=borrowed_by['email']).first()
            if not user:
                user = BackendLibraryUser.objects.create(**borrowed_by)

        if not book:
            book = BackendBook.objects.create(**payload_dict, borrowed_by=user)
        else:
            for attr, value in payload_dict.items():
                setattr(book, attr, value)
            book.borrowed_by = user
            book.save()
        return DefaultResponse(message="Book updated successfully")

    def handle_webhook_event_for_user(self, payload):
        payload_dict = payload.dict()
        user = BackendLibraryUser.objects.filter(email=payload_dict['email']).first()
        if not user:
            user = BackendLibraryUser.objects.create(**payload_dict)
        else:
            for attr, value in payload_dict.items():
                setattr(user, attr, value)
            user.save()
        return DefaultResponse(message="Library User updated successfully")

    def update_book_on_frontend_api(self, instance):
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
        self.send_webhook_data(book_data, FRONTEND_BOOK_WEBHOOK_URL)


    def send_webhook_data(self, payload, url):
        headers = {"Content-Type": "application/json"}
        try:
            response = requests.post(url, data=json.dumps(payload), headers=headers)
            response.raise_for_status()
            print(f"Webhook sent successfully: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Failed to send webhook: {e}")