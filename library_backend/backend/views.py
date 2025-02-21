from ninja import Router, Query
from base.schemas import DefaultResponse, PageSchema
from base.response import RESPONSE_CODES

from .schemas import BookSchema, AddBookSchema, LibraryUserSchema, SearchFilter, \
    LibraryUserWithBooksSchema, BookSchemaWithBorrower, BookFilter, BookWebhookSchema, UserWebhookSchema
from .services import BackendLibraryService

# Create your views here.

router = Router(tags=["Backend"])


@router.post("/books",
                     response={RESPONSE_CODES: DefaultResponse}, auth=None)
def add_book_to_catalogue(request, payload: AddBookSchema):
    return 200, BackendLibraryService().create_book(payload)


@router.get("/books",
                     response={RESPONSE_CODES: DefaultResponse[PageSchema[BookSchema]]}, auth=None)
def all_books(request, filters: BookFilter = Query(...)):
    return 200, BackendLibraryService().get_all_books(filters, BookSchema)


@router.post("/webhook/books",
                     response={RESPONSE_CODES: DefaultResponse}, auth=None)
def webhook_book_update(request, payload: BookWebhookSchema):
    return 200, BackendLibraryService().handle_webhook_event_for_book(payload)


@router.post("/webhook/users",
                     response={RESPONSE_CODES: DefaultResponse}, auth=None)
def webhook_user_update(request, payload: UserWebhookSchema):
    return 200, BackendLibraryService().handle_webhook_event_for_user(payload)


@router.get("/available_books",
                     response={RESPONSE_CODES: DefaultResponse[PageSchema[BookSchema]]}, auth=None)
def all_available_books(request, filters: BookFilter = Query(...)):
    return 200, BackendLibraryService().get_all_available_books(filters, BookSchema)


@router.get("/unavailable_books",
                     response={RESPONSE_CODES: DefaultResponse[PageSchema[BookSchemaWithBorrower]]}, auth=None)
def all_unavailable_books(request, filters: BookFilter = Query(...)):
    return 200, BackendLibraryService().get_all_unavailable_books(filters, BookSchemaWithBorrower)


@router.get("/books/{book_unique_id}",
                     response={RESPONSE_CODES: DefaultResponse[BookSchema]}, auth=None)
def book_detail(request, book_unique_id: str):
    return 200, BackendLibraryService().get_book_detail(book_unique_id)


@router.put("/books/{book_unique_id}/remove",
                     response={RESPONSE_CODES: DefaultResponse}, auth=None)
def remove_book_from_catalogue(request, book_unique_id: str):
    return 200, BackendLibraryService().remove_book(book_unique_id)


@router.get("/users",
                     response={RESPONSE_CODES: DefaultResponse[PageSchema[LibraryUserSchema]]}, auth=None)
def all_enrolled_users(request, filters: SearchFilter = Query(...)):
    return 200, BackendLibraryService().get_all_enrolled_users(filters, LibraryUserSchema)


@router.get("/users_with_borrowed_books",
                     response={RESPONSE_CODES: DefaultResponse[PageSchema[LibraryUserWithBooksSchema]]}, auth=None)
def all_enrolled_users_with_borrowed_books(request, filters: SearchFilter = Query(...)):
    return 200, BackendLibraryService().get_all_enrolled_users_with_borrowed_books(filters, LibraryUserWithBooksSchema)

