from typing import Union, List
from ninja import Router, UploadedFile, Query
from base.schemas import DefaultResponse, PageSchema
from base.response import RESPONSE_CODES

from .schemas import BookSchema, BookFilter, EnrollSchema,\
    BookBorrowSchema, BookReturnSchema
from .services import FrontendLibraryService

from .schemas import BookWebhookSchema

# Create your views here.

router = Router(tags=["Frontend"])


@router.post("/enroll",
                     response={RESPONSE_CODES: DefaultResponse}, auth=None)
def enroll_user(request, payload: EnrollSchema):
    return 200, FrontendLibraryService().enroll_library_user(payload)


@router.post("/webhook/books",
                     response={RESPONSE_CODES: DefaultResponse}, auth=None)
def webhook_book_update(request, payload: BookWebhookSchema):
    return 200, FrontendLibraryService().handle_webhook_event_for_book(payload)


@router.get("/available_books",
                     response={RESPONSE_CODES: DefaultResponse[PageSchema[BookSchema]]}, auth=None)
def all_available_books(request, filters: BookFilter = Query(...)):
    return 200, FrontendLibraryService().get_all_available_books(filters, BookSchema)


@router.get("/books/{book_unique_id}",
                     response={RESPONSE_CODES: DefaultResponse[BookSchema]}, auth=None)
def book_detail(request, book_unique_id: str):
    return 200, FrontendLibraryService().get_book_detail(book_unique_id)


@router.put("/books/{book_unique_id}/borrow",
                     response={RESPONSE_CODES: DefaultResponse}, auth=None)
def borrow_book_from_catalogue(request, book_unique_id: str, payload: BookBorrowSchema):
    return 200, FrontendLibraryService().borrow_book(book_unique_id, payload)


@router.put("/books/{book_unique_id}/return",
                     response={RESPONSE_CODES: DefaultResponse}, auth=None)
def return_book_to_catalogue(request, book_unique_id: str, payload: BookReturnSchema):
    return 200, FrontendLibraryService().borrow_book(book_unique_id, payload)

