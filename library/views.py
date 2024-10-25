from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm
from .models import Book
from django.db import models

# User Registration View
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')  # Redirect to the home page
    else:
        form = UserRegistrationForm()
    return render(request, 'library/register.html', {'form': form})

# User Login View
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome, {username}!")
                return redirect('home')  # Redirect to the home page
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'library/login.html', {'form': form})

# User Logout View
def logout_view(request):
    logout(request)
    return redirect('login')  # Redirect to the login page after logout

# Home Page View
def home(request):
    return render(request, 'library/home.html')

# Book List View with Search Functionality
@login_required
def book_list(request):
    query = request.GET.get('q', '')
    books = Book.objects.filter(
        models.Q(title__icontains=query) | 
        models.Q(author__icontains=query) | 
        models.Q(publication_date__year=query) | 
        models.Q(rating__icontains=query) | 
        models.Q(book_language__icontains=query)
    ) if query else Book.objects.all()
    
    return render(request, 'library/book_list.html', {'books': books, 'query': query})

# Book Detail View
@login_required
def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    return render(request, 'library/book_detail.html', {'book': book})

from django.shortcuts import render, get_object_or_404, redirect
from .models import Book
from .forms import BookIssueForm
from django.utils import timezone
from django.http import Http404

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Book, BookIssue
from .forms import BookIssueForm

@login_required
def book_issue(request):
    if request.method == 'POST':
        form = BookIssueForm(request.POST)
        if form.is_valid():
            book_id = form.cleaned_data['book_id']
            book_copy_no = form.cleaned_data['book_copy_no']
            
            # Check if the book copy is already issued
            if BookIssue.objects.filter(book_id=book_id, book_copy_no=book_copy_no, return_date__isnull=True).exists():
                form.add_error(None, "This copy is already issued.")
                return render(request, 'library/book_issue.html', {'form': form})

            # Check if the book exists
            try:
                book = Book.objects.get(book_id=book_id, book_copy_no=book_copy_no)
            except Book.DoesNotExist:
                form.add_error(None, "Book ID and Copy Number do not match.")
                return render(request, 'library/book_issue.html', {'form': form})

            # Create a new book issue
            book_issue = BookIssue(
                book=book,
                book_copy_no=book_copy_no,
                user=request.user,
                issue_date=timezone.now(),
                due_date=timezone.now() + timezone.timedelta(days=14)  # Set due date to 14 days later
            )
            book_issue.save()

            # Mark the book as unavailable
            book.available = False
            book.save()

            return redirect('home')  # Redirect to the home page after issuance
    else:
        form = BookIssueForm()

    return render(request, 'library/book_issue.html', {'form': form})

# views.py
@login_required
def user_profile(request):
    issued_books = BookIssue.objects.filter(user=request.user).order_by('-issue_date')

    # Calculate fines for overdue books
    for book_issue in issued_books:
        book_issue.calculate_fine()
        book_issue.save()

    return render(request, 'library/user_profile.html', {
        'issued_books': issued_books,
    })


from django.shortcuts import render
from .models import Book, BookIssue
from django.db.models import Count
import datetime

from django.shortcuts import render
from django.db.models import Count
from .models import Book, BookIssue
from django.utils import timezone

@login_required
def admin_dashboard(request):
    # Filters
    genre_filter = request.GET.getlist('genre', None)
    start_date = request.GET.get('start_date', None)
    end_date = request.GET.get('end_date', None)
    available_filter = request.GET.get('available', None)

    # Get all books
    books = Book.objects.all()

    # Apply filters
    if genre_filter:
        books = books.filter(genre__in=genre_filter)

    if start_date and end_date:
        books = books.filter(publication_date__range=[start_date, end_date])

    if available_filter is not None:
        available_filter = available_filter.lower() == 'true'  # Convert to boolean
        books = books.filter(available=available_filter)

    # Analyze genre popularity
    genre_popularity = books.values('genre').annotate(total_issues=Count('bookissue')).order_by('-total_issues')

    # Book availability analysis
    available_books_count = books.filter(available=True).count()
    issued_books_count = BookIssue.objects.filter(return_date__isnull=True).count()

    # Overdue books
    overdue_books_count = BookIssue.objects.filter(return_date__isnull=True, due_date__lt=timezone.now()).count()

    # Get the top 5 most popular books
    popular_books = BookIssue.objects.values('book__title').annotate(issue_count=Count('id')).order_by('-issue_count')[:5]

    return render(request, 'library/admin_dashboard.html', {
        'books': books,
        'genre_popularity': genre_popularity,
        'available_books_count': available_books_count,
        'issued_books_count': issued_books_count,
        'overdue_books_count': overdue_books_count,
        'popular_books': popular_books,
        'selected_genres': genre_filter,
        'start_date': start_date,
        'end_date': end_date,
        'available_filter': available_filter,
    })

import plotly.express as px
from django.http import JsonResponse

import plotly.express as px
from django.http import JsonResponse
from .models import Book
from django.db.models import Count
from django.contrib.auth.decorators import login_required

@login_required
def genre_popularity_chart(request):
    genre_popularity = Book.objects.values('genre').annotate(total_issues=Count('bookissue')).order_by('-total_issues')

    # Prepare data for the chart
    labels = [item['genre'] for item in genre_popularity]
    values = [item['total_issues'] for item in genre_popularity]

    # Create the Plotly figure
    fig = px.bar(x=labels, y=values, title="Genre Popularity", labels={'x':'Genre', 'y':'Number of Issues'})

    # Serialize the figure to JSON
    fig_json = fig.to_json()

    # Return the serialized figure as a JSON response
    return JsonResponse(fig_json, safe=False)
import csv
from django.http import HttpResponse

@login_required
def export_book_data(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="books.csv"'

    writer = csv.writer(response)
    writer.writerow(['Title', 'Author', 'Publication Date', 'ISBN', 'Available', 'Genre'])

    books = Book.objects.all()
    for book in books:
        writer.writerow([book.title, book.author, book.publication_date, book.isbn, book.available, book.genre])

    return response
