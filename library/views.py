from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.http import HttpResponseNotAllowed

from datetime import date, timedelta

from .models import Book, Loan
from .forms import BookForm


def home(request):

    return render(request, 'library/home.html')


@login_required
def book_list(request):
    q = request.GET.get('q', '').strip()
    if q:
        books = Book.objects.filter(Q(title__icontains=q) | Q(author__icontains=q))
    else:
        books = Book.objects.all()

    return render(request, 'library/book_list.html', {'books': books, 'q': q})


@login_required
def book_detail(request, id):
    book = get_object_or_404(Book, id=id)

    user_loan = None
    if request.user.is_authenticated:
        user_loan = Loan.objects.filter(book=book, user=request.user, returned=False).first()

    overdue_days = None
    if user_loan and user_loan.return_date < date.today():
        overdue_days = (date.today() - user_loan.return_date).days

    return render(request, 'library/book_detail.html', {'book': book, 'user_loan': user_loan, 'overdue_days': overdue_days})


@login_required
def add_book(request):

    if request.method == 'POST':

        form = BookForm(request.POST, request.FILES)

        if form.is_valid():

            form.save()

            messages.success(request, 'Book added successfully')

            return redirect('book_list')

    else:

        form = BookForm()

    return render(request, 'library/add_book.html', {'form': form})


@login_required
def edit_book(request, id):

    book = get_object_or_404(Book, id=id)

    if request.method == 'POST':

        form = BookForm(request.POST, request.FILES, instance=book)

        if form.is_valid():

            form.save()

            messages.success(request, 'Book updated successfully')

            return redirect('book_list')

    else:

        form = BookForm(instance=book)

    return render(request, 'library/edit_book.html', {'form': form})


@login_required
def delete_book(request, id):

    book = get_object_or_404(Book, id=id)

    if request.method == 'POST':
        book.delete()
        messages.success(request, 'Book deleted successfully')
        return redirect('book_list')

    # If not POST, render a confirmation page
    return render(request, 'library/confirm_delete.html', {'book': book})


@login_required
def borrow_book(request, id):
    book = get_object_or_404(Book, id=id)

    if book.available_copies < 1:
        messages.error(request, 'No copies available')
        return redirect('book_detail', id=id)

    existing = Loan.objects.filter(user=request.user, book=book, returned=False).first()
    if existing:
        messages.info(request, 'You have already borrowed this book')
        return redirect('book_detail', id=id)

    if request.method == 'POST':
        return_date = date.today() + timedelta(days=14)
        Loan.objects.create(user=request.user, book=book, return_date=return_date)
        book.available_copies -= 1
        book.save()
        messages.success(request, f'Book borrowed — due {return_date.isoformat()}')
        return redirect('book_detail', id=id)

    return render(request, 'library/confirm_borrow.html', {'book': book})


@login_required
def return_book(request, loan_id):
    loan = get_object_or_404(Loan, id=loan_id, user=request.user)

    if loan.returned:
        messages.info(request, 'This loan is already returned')
        return redirect('book_detail', id=loan.book.id)

    if request.method == 'POST':
        loan.returned = True
        loan.save()
        book = loan.book
        book.available_copies += 1
        book.save()
        messages.success(request, 'Book returned successfully')
        return redirect('book_detail', id=book.id)

    return render(request, 'library/confirm_return.html', {'loan': loan})


@login_required
def overdue_loans(request):
    # Only staff can view the overdue list
    if not request.user.is_staff:
        messages.error(request, 'Not authorized to view overdue loans')
        return redirect('home')

    today = date.today()
    loans = Loan.objects.filter(returned=False, return_date__lt=today).select_related('book', 'user')

    # annotate days overdue for display
    overdue_list = []
    for loan in loans:
        days_overdue = (today - loan.return_date).days
        overdue_list.append({'loan': loan, 'days_overdue': days_overdue})

    return render(request, 'library/overdue_loans.html', {'overdue_list': overdue_list, 'today': today})


def logout_view(request):
    if request.method in ('GET', 'POST'):
        auth_logout(request)
        return redirect('home')
    return HttpResponseNotAllowed(['GET', 'POST'])


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, 'Registration successful. You are now logged in.')
            return redirect('home')
    else:
        form = UserCreationForm()

    return render(request, 'registration/register.html', {'form': form})