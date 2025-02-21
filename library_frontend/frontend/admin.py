from django.contrib import admin
from frontend.models import FrontendBook, FrontendLibraryUser

# Register your models here.
class BookAdmin(admin.ModelAdmin):
    list_display = ["name", "identifier", "id", "publisher", "category", "date_borrowed", "duration"]
    raw_id_fields = ["borrowed_by"]
    search_fields = ["name"]

class LibraryUserAdmin(admin.ModelAdmin):
    list_display = ["email", "id", "first_name", "last_name"]
    search_fields = ["email", "first_name", "last_name"]


admin.site.register(FrontendBook, BookAdmin)
admin.site.register(FrontendLibraryUser, LibraryUserAdmin)