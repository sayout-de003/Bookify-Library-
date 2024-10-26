from django.db import models
from multiselectfield import MultiSelectField
from django.contrib.auth.models import User

# Define choices for BookType and BookLanguage
class BookType(models.TextChoices):
    HARDCOVER = 'HC', 'Hardcover'
    PAPERBACK = 'PB', 'Paperback'
    EBOOK = 'EB', 'Ebook'

class BookLanguage(models.TextChoices):
    ENGLISH = 'EN', 'English'
    SPANISH = 'ES', 'Spanish'
    FRENCH = 'FR', 'French'
    # Add other languages as needed

GENRE_CHOICES = [
    ('Fiction', 'Fiction'),
    ('Non-Fiction', 'Non-Fiction'),
    ('Science Fiction', 'Science Fiction'),
    ('Fantasy', 'Fantasy'),
    ('Romance', 'Romance'),
    ('Mystery', 'Mystery'),
    ('Thriller', 'Thriller'),
    ('Biography', 'Biography'),
    ('History', 'History'),
    ('Travel', 'Travel'),
    ('Cooking', 'Cooking'),
    ('Art', 'Art'),
    ('Music', 'Music'),
    ('Science', 'Science'),
    ('Technology', 'Technology'),
    ('Business', 'Business'),
    ('Self-Help', 'Self-Help'),
    ('Health', 'Health'),
    ('Fiction', 'Fiction'),
    ('Non-Fiction', 'Non-Fiction'),
    ('Science Fiction', 'Science Fiction'),
    ('Fantasy', 'Fantasy'),
    ('Romance', 'Romance'), 
    ('Mystery', 'Mystery'),
    ('Thriller', 'Thriller'),
    ('Biography', 'Biography'),
    ('History', 'History'),
    ('Travel', 'Travel'),
    ('Cooking', 'Cooking'),
    ('Art', 'Art'),
    ('Music', 'Music'),
    # Add other genres as needed
]

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    description = models.TextField()
    publication_date = models.DateField()
    isbn = models.CharField(max_length=13)
    available = models.BooleanField(default=True)
    rack_number = models.CharField(max_length=10)
    book_image = models.ImageField(upload_to='book_images/')
    book_file = models.FileField(upload_to='book_files/', null=True, blank=True)  
    book_id = models.CharField(max_length=10, unique=True)
    book_copy_no = models.CharField(max_length=10)
    book_type = models.CharField(max_length=10, choices=BookType.choices)
    book_language = models.CharField(max_length=20, choices=BookLanguage.choices)
    book_pages = models.IntegerField()
    book_publisher = models.CharField(max_length=200)
    book_edition = models.CharField(max_length=20)
    book_subject = models.CharField(max_length=200)
    book_location = models.CharField(max_length=200)
    genre = MultiSelectField(choices=GENRE_CHOICES)

    @property
    def is_available_for_e_reading(self):
        return bool(self.book_file)
    @property
    def book_unique_id(self):
        # Ensure this does not call __str__ or any method that leads to it
        return self.id  # or however you define a unique ID

    def __str__(self):
        return f"{self.title} ({self.book_unique_id})"


# models.py
from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True, max_length=255)
    bio = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    favorite_books = models.ManyToManyField('library.Book', blank=True)  # Assuming there's a Book model in 'library' app

    def __str__(self):
        return self.user.username

# BookIssue model definition
# models.py
from django.conf import settings
from django.db import models
from django.utils import timezone

class BookIssue(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    book_copy_no = models.CharField(max_length=50)
    issue_date = models.DateTimeField()
    due_date = models.DateTimeField()
    return_date = models.DateTimeField(null=True, blank=True)  # Returned books will have this field filled
    fine = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    def calculate_fine(self):
        if self.return_date and self.return_date > self.due_date:
            overdue_days = (self.return_date - self.due_date).days
            self.fine = overdue_days * 1.00  # Assuming a fine of 1.00 per overdue day
        elif timezone.now() > self.due_date:
            overdue_days = (timezone.now() - self.due_date).days
            self.fine = overdue_days * 1.00
        else:
            self.fine = 0.00
        return self.fine

from django.db import models
from django.contrib.auth.models import User
from .models import Book  # If Book is in the same models.py file, you can omit this

class UserReadingProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    current_page = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.book.title} - Page {self.current_page}"
