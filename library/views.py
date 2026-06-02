from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q, Count
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.http import HttpResponseNotAllowed, Http404
from datetime import date, timedelta
from .models import Book, Loan
from .forms import BookForm, CustomUserCreationForm


def home(request):
    return render(request, 'library/home.html')


@login_required
def dashboard(request):
    if not request.user.is_staff:
        messages.error(request, 'Not authorized to view the dashboard')
        return redirect('home')

    today = date.today()
    borrowed_books = Loan.objects.filter(returned=False).count()
    returned_books = Loan.objects.filter(returned=True).count()
    overdue_books = Loan.objects.filter(returned=False, return_date__lt=today).count()
    missing_books = Book.objects.filter(available_copies=0).count()
    total_books = Book.objects.count()
    visitors = User.objects.count()
    new_members = User.objects.filter(date_joined__gte=today - timedelta(days=30)).count()
    pending_fees = overdue_books * 5

    recent_loans = Loan.objects.select_related('book', 'user').order_by('-borrowed_date')[:5]
    top_books = (
        Book.objects.annotate(loan_count=Count('loan'))
            .order_by('-loan_count')[:3]
    )
    recent_members = User.objects.order_by('-date_joined')[:5]

    context = {
        'borrowed_books': borrowed_books,
        'returned_books': returned_books,
        'overdue_books': overdue_books,
        'missing_books': missing_books,
        'total_books': total_books,
        'visitors': visitors,
        'new_members': new_members,
        'pending_fees': pending_fees,
        'recent_loans': recent_loans,
        'top_books': top_books,
        'recent_members': recent_members,
        'today': today,
    }
    return render(request, 'library/dashboard.html', context)


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

    return render(request, 'library/book_detail.html', {
        'book': book,
        'user_loan': user_loan,
        'overdue_days': overdue_days,
    })


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
    today = date.today()
    
    if request.user.is_staff:
        # Staff can view all overdue loans from students
        loans = Loan.objects.filter(returned=False, return_date__lt=today).select_related('book', 'user')
        is_staff_view = True
    else:
        # Students can view only their own overdue loans
        loans = Loan.objects.filter(user=request.user, returned=False, return_date__lt=today).select_related('book')
        is_staff_view = False

    # annotate days overdue for display
    overdue_list = []
    for loan in loans:
        days_overdue = (today - loan.return_date).days
        overdue_list.append({'loan': loan, 'days_overdue': days_overdue})

    return render(request, 'library/overdue_loans.html', {'overdue_list': overdue_list, 'today': today, 'is_staff_view': is_staff_view})


@login_required
def my_loans(request):
    loans = Loan.objects.filter(user=request.user, returned=False).select_related('book')
    return render(request, 'library/my_loans.html', {'loans': loans})


@login_required
def borrowers_list(request):
    # Only staff can view all borrowers
    if not request.user.is_staff:
        messages.error(request, 'Not authorized to view borrowers list')
        return redirect('home')

    today = date.today()
    loans = Loan.objects.filter(returned=False).select_related('book', 'user').order_by('return_date')
    return render(request, 'library/borrowers_list.html', {'loans': loans, 'today': today})


def logout_view(request):
    if request.method in ('GET', 'POST'):
        auth_logout(request)
        return redirect('home')
    return HttpResponseNotAllowed(['GET', 'POST'])


def register(request, role=None):
    if role not in (None, 'student', 'staff'):
        raise Http404()

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            selected_role = form.cleaned_data.get('role')
            user.is_staff = selected_role == 'staff'
            user.save()
            auth_login(request, user)
            messages.success(request, 'Registration successful. You are now logged in.')
            return redirect('home')
    else:
        form = CustomUserCreationForm(initial={'role': role}) if role in ('student', 'staff') else CustomUserCreationForm()
        if role in ('student', 'staff'):
            form.fields['role'].widget = forms.HiddenInput()

    return render(request, 'registration/register.html', {'form': form, 'role': role})