import json
from datetime import date, timedelta

from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict

from .models import Book, Loan, Category


def book_to_dict(book):
    data = model_to_dict(book, fields=['id', 'title', 'author', 'description', 'available_copies'])
    data['category'] = book.category.name if book.category else None
    data['cover_image'] = book.cover_image.url if book.cover_image else None
    return data


def loan_to_dict(loan):
    return {
        'id': loan.id,
        'user': {'id': loan.user.id, 'username': loan.user.username},
        'book': {'id': loan.book.id, 'title': loan.book.title},
        'borrowed_date': loan.borrowed_date.isoformat(),
        'return_date': loan.return_date.isoformat(),
        'returned': loan.returned,
    }


@csrf_exempt
def api_books(request):
    if request.method == 'GET':
        qs = Book.objects.all()
        data = [book_to_dict(b) for b in qs]
        return JsonResponse(data, safe=False)

    if request.method == 'POST':
        if not request.user.is_staff:
            return HttpResponseForbidden(json.dumps({'error': 'staff only'}), content_type='application/json')
        try:
            payload = json.loads(request.body)
        except Exception:
            return HttpResponseBadRequest('Invalid JSON')

        title = payload.get('title')
        author = payload.get('author')
        description = payload.get('description', '')
        copies = payload.get('available_copies', 1)
        category_id = payload.get('category_id')

        if not title or not author:
            return HttpResponseBadRequest('Missing title or author')

        book = Book(title=title, author=author, description=description, available_copies=copies)
        if category_id:
            try:
                book.category = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                pass
        book.save()
        return JsonResponse(book_to_dict(book), status=201)

    return HttpResponseBadRequest('Unsupported method')


@csrf_exempt
def api_book_detail(request, id):
    try:
        book = Book.objects.get(id=id)
    except Book.DoesNotExist:
        return JsonResponse({'error': 'not found'}, status=404)

    if request.method == 'GET':
        return JsonResponse(book_to_dict(book))

    if request.method in ('PUT', 'PATCH'):
        if not request.user.is_staff:
            return HttpResponseForbidden(json.dumps({'error': 'staff only'}), content_type='application/json')
        try:
            payload = json.loads(request.body)
        except Exception:
            return HttpResponseBadRequest('Invalid JSON')

        for field in ('title', 'author', 'description', 'available_copies'):
            if field in payload:
                setattr(book, field, payload[field])
        if 'category_id' in payload:
            try:
                book.category = Category.objects.get(id=payload['category_id'])
            except Category.DoesNotExist:
                book.category = None
        book.save()
        return JsonResponse(book_to_dict(book))

    if request.method == 'DELETE':
        if not request.user.is_staff:
            return HttpResponseForbidden(json.dumps({'error': 'staff only'}), content_type='application/json')
        book.delete()
        return JsonResponse({'deleted': True})

    return HttpResponseBadRequest('Unsupported method')


@csrf_exempt
def api_loans(request):
    if request.method == 'GET':
        if request.user.is_staff:
            qs = Loan.objects.select_related('book', 'user').all()
        elif request.user.is_authenticated:
            qs = Loan.objects.select_related('book').filter(user=request.user)
        else:
            return HttpResponseForbidden(json.dumps({'error': 'auth required'}), content_type='application/json')

        data = [loan_to_dict(l) for l in qs]
        return JsonResponse(data, safe=False)

    if request.method == 'POST':
        # Create a loan (borrow) for current user
        if not request.user.is_authenticated:
            return HttpResponseForbidden(json.dumps({'error': 'auth required'}), content_type='application/json')
        try:
            payload = json.loads(request.body)
        except Exception:
            return HttpResponseBadRequest('Invalid JSON')

        book_id = payload.get('book_id')
        if not book_id:
            return HttpResponseBadRequest('Missing book_id')
        try:
            book = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            return JsonResponse({'error': 'book not found'}, status=404)

        if book.available_copies < 1:
            return JsonResponse({'error': 'no copies available'}, status=400)

        existing = Loan.objects.filter(user=request.user, book=book, returned=False).first()
        if existing:
            return JsonResponse({'error': 'already borrowed'}, status=400)

        return_date = date.today() + timedelta(days=14)
        loan = Loan.objects.create(user=request.user, book=book, return_date=return_date)
        book.available_copies -= 1
        book.save()
        return JsonResponse(loan_to_dict(loan), status=201)

    return HttpResponseBadRequest('Unsupported method')


@csrf_exempt
def api_loan_detail(request, id):
    try:
        loan = Loan.objects.select_related('book', 'user').get(id=id)
    except Loan.DoesNotExist:
        return JsonResponse({'error': 'not found'}, status=404)

    if request.method == 'GET':
        # staff can view any; user can view own
        if request.user.is_staff or (request.user.is_authenticated and loan.user == request.user):
            return JsonResponse(loan_to_dict(loan))
        return HttpResponseForbidden(json.dumps({'error': 'forbidden'}), content_type='application/json')

    if request.method == 'POST':
        # use POST to mark returned
        if not (request.user.is_staff or (request.user.is_authenticated and loan.user == request.user)):
            return HttpResponseForbidden(json.dumps({'error': 'forbidden'}), content_type='application/json')
        if loan.returned:
            return JsonResponse({'error': 'already returned'}, status=400)
        loan.returned = True
        loan.save()
        book = loan.book
        book.available_copies += 1
        book.save()
        return JsonResponse(loan_to_dict(loan))

    if request.method == 'DELETE':
        if not request.user.is_staff:
            return HttpResponseForbidden(json.dumps({'error': 'staff only'}), content_type='application/json')
        loan.delete()
        return JsonResponse({'deleted': True})

    return HttpResponseBadRequest('Unsupported method')
