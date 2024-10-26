from django.contrib import admin
from django.urls import path
from django.template.response import TemplateResponse
from .models import Book, BookIssue, UserProfile
from django.db.models import Count
import datetime

# Custom Admin Site
class MyAdminSite(admin.AdminSite):
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(self.admin_dashboard), name='admin_dashboard'),
        ]
        return custom_urls + urls

    def admin_dashboard(self, request):
        # Fetch data for the admin dashboard analytics
        total_books = Book.objects.count()
        available_books_count = Book.objects.filter(available=True).count()
        issued_books_count = BookIssue.objects.filter(return_date__isnull=True).count()
        overdue_books_count = BookIssue.objects.filter(return_date__isnull=True, due_date__lt=datetime.datetime.now()).count()

        # Analyze genre popularity
        genre_popularity = Book.objects.values('genre').annotate(total_issues=Count('bookissue')).order_by('-total_issues')

        # Fetch the top 5 popular books
        popular_books = BookIssue.objects.values('book__title').annotate(issue_count=Count('id')).order_by('-issue_count')[:5]

        # Pass the data to the dashboard template
        context = {
            'total_books': total_books,
            'available_books_count': available_books_count,
            'issued_books_count': issued_books_count,
            'overdue_books_count': overdue_books_count,
            'genre_popularity': genre_popularity,
            'popular_books': popular_books,
        }
        return TemplateResponse(request, 'admin/dashboard.html', context)

# Register the custom admin site
admin_site = MyAdminSite(name='myadmin')

# Custom Admin for Book
class BookAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'author', 'publication_date', 'isbn', 'available', 
        'book_type', 'book_language', 'book_id', 'book_copy_no', 
        'book_publisher', 'book_edition', 'book_subject', 
        'book_location', 'genre'
    )
    search_fields = ('title', 'author', 'isbn')
    list_filter = ('book_type', 'book_language', 'available', 'genre')
    readonly_fields = ('book_unique_id',)
    list_per_page = 10

# Custom Admin for UserProfile
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'date_of_birth')
    search_fields = ('user__username', 'user__email')
    list_filter = ('date_of_birth',)

# Register models with the default admin site
admin.site.register(Book, BookAdmin)
admin.site.register(BookIssue)
admin.site.register(UserProfile, UserProfileAdmin)

# Register models with the custom admin site
admin_site.register(Book, BookAdmin)
admin_site.register(BookIssue)
admin_site.register(UserProfile, UserProfileAdmin)
