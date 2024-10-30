from django.urls import path, include
from . import views  # Import views from the current app

urlpatterns = [
    path('', views.home, name='home'),  # Example URL pattern, replace with your own
    path('books/', views.book_list, name='book_list'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('books/<int:book_id>/', views.book_detail, name='book_detail'),
    path('books/issue/', views.book_issue, name='book_issue'),
    path('profile/', views.user_profile, name='user_profile'),    # Add other URL patterns here
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin_export-books/', views.export_book_data, name='export_book_data'),
    path('genre_popularity_chart/', views.genre_popularity_chart, name='genre_popularity_chart'),
    path('books/<int:book_id>/e-reading/', views.e_reading_view, name='e_reading_view'),
    path('admin_control/', views.admin_control_panel, name='admin_control_panel'),  # Add this line
    path('goal_set/', views.goal_create_and_track, name = 'goal_create_and_track')

    
]

