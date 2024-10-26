from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Q
from collections import defaultdict

import plotly.express as px
import plotly.graph_objs as go
import json
import csv
import os
import plotly  # Add this import

from .forms import UserRegistrationForm, BookIssueForm
from .models import Book, BookIssue, UserReadingProgress# Add this import

# User Registration View
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
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
            if user:
                login(request, user)
                messages.success(request, f"Welcome, {username}!")
                return redirect('home')
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'library/login.html', {'form': form})

# User Logout View
@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

# Home Page View
def home(request):
    return render(request, 'library/home.html')

# Book List View with Search Functionality
@login_required
def book_list(request):
    query = request.GET.get('q', '')
    books = Book.objects.filter(
        Q(title__icontains=query) | 
        Q(author__icontains=query) | 
        Q(publication_date__year=query) | 
        Q(genre__icontains=query)
    ) if query else Book.objects.all()
    
    return render(request, 'library/book_list.html', {'books': books, 'query': query})

# Book Detail View
@login_required
def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    return render(request, 'library/book_detail.html', {'book': book})

# Book Issue View
@login_required
def book_issue(request):
    if request.method == 'POST':
        form = BookIssueForm(request.POST)
        if form.is_valid():
            book_id = form.cleaned_data['book_id']
            book_copy_no = form.cleaned_data['book_copy_no']

            # Check for existing book issue
            if BookIssue.objects.filter(book_id=book_id, book_copy_no=book_copy_no, return_date__isnull=True).exists():
                form.add_error(None, "This copy is already issued.")
            else:
                book = get_object_or_404(Book, id=book_id)
                book_issue = BookIssue(
                    book=book,
                    book_copy_no=book_copy_no,
                    user=request.user,
                    issue_date=timezone.now(),
                    due_date=timezone.now() + timezone.timedelta(days=14)
                )
                book_issue.save()
                book.available = False  # Mark book as unavailable
                book.save()
                messages.success(request, "Book issued successfully!")
                return redirect('home')
    else:
        form = BookIssueForm()

    return render(request, 'library/book_issue.html', {'form': form})

# User Profile View
@login_required
def user_profile(request):
    issued_books = BookIssue.objects.filter(user=request.user).order_by('-issue_date')
    for book_issue in issued_books:
        book_issue.calculate_fine()  # Assuming this method calculates fines
        book_issue.save()

    return render(request, 'library/user_profile.html', {'issued_books': issued_books})



@login_required
def admin_dashboard(request):
    # Filters
    genre_filter = request.GET.getlist('genre', None)
    start_date = request.GET.get('start_date', None)
    end_date = request.GET.get('end_date', None)
    available_filter = request.GET.get('available', None)
    chart_type = request.GET.get('chart_type', 'bar')  # Default to bar chart

    books = Book.objects.all()

    # Apply filters
    if genre_filter:
        books = books.filter(genre__in=genre_filter)
    if start_date and end_date:
        books = books.filter(publication_date__range=[start_date, end_date])
    if available_filter is not None:
        books = books.filter(available=available_filter.lower() == 'true')

    # Calculate statistics
    genre_popularity = books.values('genre').annotate(total_issues=Count('bookissue')).order_by('-total_issues')
    available_books_count = books.filter(available=True).count()
    issued_books_count = BookIssue.objects.filter(return_date__isnull=True).count()
    overdue_books_count = BookIssue.objects.filter(return_date__isnull=True, due_date__lt=timezone.now()).count()
    popular_books = BookIssue.objects.values('book__title').annotate(issue_count=Count('id')).order_by('-issue_count')[:5]

    # New Metrics
    total_users = UserProfile.objects.count()
    top_users = BookIssue.objects.values('user__username').annotate(total_issues=Count('id')).order_by('-total_issues')[:5]

    # Calculate book issuance trends
    issue_trend_data = BookIssue.objects.values('issue_date').annotate(total_issues=Count('id')).order_by('issue_date')
    issue_dates = [data['issue_date'].strftime('%Y-%m-%d') for data in issue_trend_data]
    issue_counts = [data['total_issues'] for data in issue_trend_data]

    # Prepare chart data for Plotly
    chart_data = {
        'data': [],
        'layout': {
            'title': 'Genre Popularity',
            'xaxis': {'title': 'Genre'},
            'yaxis': {'title': 'Number of Issues'},
        },
    }

    if chart_type == 'bar':
        chart_data['data'] = [{
            'x': [genre['genre'] for genre in genre_popularity],
            'y': [genre['total_issues'] for genre in genre_popularity],
            'type': 'bar',
            'name': 'Genre Popularity',
        }]
    elif chart_type == 'line':
        chart_data['data'] = [{
            'x': issue_dates,
            'y': issue_counts,
            'type': 'scatter',
            'mode': 'lines+markers',
            'name': 'Book Issuance Trend',
        }]
    elif chart_type == 'pie':
        chart_data['data'] = [{
            'labels': [genre['genre'] for genre in genre_popularity],
            'values': [genre['total_issues'] for genre in genre_popularity],
            'type': 'pie',
            'name': 'Genre Popularity',
        }]

    return render(request, 'library/admin_dashboard.html', {
        'books': books,
        'genre_popularity': genre_popularity,
        'available_books_count': available_books_count,
        'issued_books_count': issued_books_count,
        'overdue_books_count': overdue_books_count,
        'popular_books': popular_books,
        'top_users': top_users,
        'total_users': total_users,
        'selected_genres': genre_filter,
        'start_date': start_date,
        'end_date': end_date,
        'available_filter': available_filter,
        'chart_data': chart_data,
        'chart_type': chart_type,  # Pass the selected chart type to the template
    })




def genre_popularity_chart(request):
    # Example data
    genre_popularity = [
        {'genre': 'Fiction', 'total_issues': 150},
        {'genre': 'Non-Fiction', 'total_issues': 90},
        {'genre': 'Science Fiction', 'total_issues': 50},
    ]

    genres = [item['genre'] for item in genre_popularity]
    total_issues = [item['total_issues'] for item in genre_popularity]

    # Create Plotly figure
    fig = go.Figure(data=[go.Bar(x=genres, y=total_issues)])
    fig.update_layout(title='Genre Popularity',
                      xaxis_title='Genre',
                      yaxis_title='Number of Issues')

    # Convert the figure to JSON
    fig_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    # Example data for book issuance trend
    issue_dates = ['2024-01-01', '2024-01-02', '2024-01-03']
    issue_counts = [5, 10, 7]

    return render(request, 'library/admin_dashboard.html', {
        'chart_data': fig_json,
        'issue_dates': json.dumps(issue_dates),
        'issue_counts': json.dumps(issue_counts),
        # Add other context variables as needed
    })

# Export Book Data as CSV
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

# E-Reading View
@login_required
def e_reading_view(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    # Check if the book is available for e-reading
    if not book.book_file:
        return render(request, 'library/error.html', {'message': "This book is not available for e-reading."})

    # Determine the file extension (PDF, ePub, etc.)
    file_extension = os.path.splitext(book.book_file.name)[-1].lower()

    # Get or create the user's reading progress
    reading_progress, created = UserReadingProgress.objects.get_or_create(user=request.user, book=book)

    if request.method == 'POST':
        current_page = request.POST.get('current_page')
        if current_page:
            reading_progress.current_page = min(int(current_page), book.book_pages)
            if reading_progress.current_page >= book.book_pages:
                reading_progress.completed = True
            reading_progress.save()
            return JsonResponse({'status': 'success'})  # Return JSON response for AJAX

    context = {
        'book': book,
        'reading_progress': reading_progress,
        'file_extension': file_extension,
    }

    return render(request, 'library/e_reading.html', context)

# Admin Control Panel View
@login_required
def admin_control_panel(request):
    return render(request, 'library/admin_control.html')  # Admin control panel


