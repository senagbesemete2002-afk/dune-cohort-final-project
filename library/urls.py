 
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from . import api


urlpatterns = [

    path('', views.home, name='home'),

    path('books/', views.book_list, name='book_list'),

    path('books/<int:id>/', views.book_detail, name='book_detail'),

    path('books/edit/<int:id>/', views.edit_book, name='edit_book'),

    path('books/delete/<int:id>/', views.delete_book, name='delete_book'),

    path('books/borrow/<int:id>/', views.borrow_book, name='borrow_book'),
    path('books/return/<int:loan_id>/', views.return_book, name='return_book'),
    path('books/overdue/', views.overdue_loans, name='overdue_loans'),
    path('accounts/register/', views.register, name='register'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', views.logout_view, name='logout'),

    # API
    path('api/books/', api.api_books, name='api_books'),
    path('api/books/<int:id>/', api.api_book_detail, name='api_book_detail'),
    path('api/loans/', api.api_loans, name='api_loans'),
    path('api/loans/<int:id>/', api.api_loan_detail, name='api_loan_detail'),

    path('add-book/', views.add_book, name='add_book'),

]
 


 