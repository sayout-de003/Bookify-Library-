# library/admin.py
from django.contrib import admin
from .models import Book, UserProfile

class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'publication_date', 'isbn', 'available', 'book_type', 'book_language', 'book_id', 'book_copy_no', 'book_publisher', 'book_edition', 'book_subject', 'book_location', 'genre')
    search_fields = ('title', 'author', 'isbn')
    list_filter = ('book_type', 'book_language', 'available', 'genre')
    readonly_fields = ('book_unique_id',)
    list_per_page = 10


admin.site.register(Book, BookAdmin)

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'date_of_birth')
    search_fields = ('user__username', 'user__email')
    list_filter = ('date_of_birth',)

admin.site.register(UserProfile, UserProfileAdmin)
