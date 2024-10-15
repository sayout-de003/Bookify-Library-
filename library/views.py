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
            # Check if the book exists and matches the copy number
            try:
                book = Book.objects.get(book_id=book_id, book_copy_no=book_copy_no)
            except Book.DoesNotExist:
                form.add_error(None, "Book ID and Copy Number do not match.")
                return render(request, 'library/book_issue.html', {'form': form})

            book_issue = BookIssue(
                book=book,
                book_copy_no=book_copy_no,
                user=request.user,
                issue_date=timezone.now(),
                due_date=timezone.now() + timezone.timedelta(days=14)  # Set due date to 14 days later
            )
            book_issue.save()
            return redirect('home')  # Redirect to the home page after issuance
    else:
        form = BookIssueForm()

    return render(request, 'library/book_issue.html', {'form': form})
