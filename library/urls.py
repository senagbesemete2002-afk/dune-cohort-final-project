from django.urls import path, include
from django.contrib.auth import views as auth_views
from rest_framework.routers import DefaultRouter
from . import views
from . import api
from .drf_views import BookViewSet, LoanViewSet

router = DefaultRouter()
router.register('books', BookViewSet, basename='book')
router.register('loans', LoanViewSet, basename='loan')

urlpatterns = [

    path('', views.home, name='home'),

    path('books/', views.book_list, name='book_list'),

    path('books/<int:id>/', views.book_detail, name='book_detail'),

    path('books/edit/<int:id>/', views.edit_book, name='edit_book'),

    path('books/delete/<int:id>/', views.delete_book, name='delete_book'),

    path('books/borrow/<int:id>/', views.borrow_book, name='borrow_book'),
    path('books/return/<int:loan_id>/', views.return_book, name='return_book'),
    path('books/my-loans/', views.my_loans, name='my_loans'),
    path('books/borrowers/', views.borrowers_list, name='borrowers_list'),
    path('books/overdue/', views.overdue_loans, name='overdue_loans'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('accounts/register/student/', views.register, {'role': 'student'}, name='register_student'),
    path('accounts/register/staff/', views.register, {'role': 'staff'}, name='register_staff'),
    path('accounts/register/', views.register, name='register'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', views.logout_view, name='logout'),

    # API
    path('api/books/', api.api_books, name='api_books'),
    path('api/books/<int:id>/', api.api_book_detail, name='api_book_detail'),
    path('api/loans/', api.api_loans, name='api_loans'),
    path('api/loans/<int:id>/', api.api_loan_detail, name='api_loan_detail'),
    path('api/v2/', include(router.urls)),

    path('add-book/', views.add_book, name='add_book'),

]
 


 