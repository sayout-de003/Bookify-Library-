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
    def book_unique_id(self):
        return f"{self.book_id}-{self.book_copy_no}"

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

