from django.urls import path
from . import views  # Import views from the current app

urlpatterns = [
    path('', views.home, name='home'),  # Example URL pattern, replace with your own
    path('books/', views.book_list, name='book_list'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('books/<int:book_id>/', views.book_detail, name='book_detail'),
    # Add other URL patterns here
]
