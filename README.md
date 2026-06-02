# Library Management System

A Django library management application that lets users register, log in, browse books, borrow and return loans, and track overdue items.

## Features

- User registration and login
- Book catalog with details
- Add, edit, and delete books
- Borrow and return books with confirmation workflows
- View personal loans in `My Loans`
- Track overdue loans separately

## Technology Stack

- Django
- SQLite (`db.sqlite3`)
- HTML templates
- CSS styling
- Static files and media support for book images

## Installation

1. Clone or copy the project into a folder.
2. Open a terminal in the project root.
3. Activate your Python virtual environment.

```powershell
& .\venv\Scripts\Activate.ps1
```

4. Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

5. Run database migrations:

```powershell
python manage.py migrate
```

6. Start the development server:

```powershell
python manage.py runserver
```

7. Open the app in your browser at:

```text
http://127.0.0.1:8000/
```

## Project Structure

- `config/` - Django project settings, URLs, WSGI/ASGI
- `library/` - app models, views, forms, URLs, templates
- `library/templates/library/` - app HTML templates
- `templates/` - shared site templates like `base.html`
- `static/css/style.css` - site styling
- `media/` - uploaded book images

## How to Use

1. Register a new account or log in.
2. Browse the book list.
3. Open a book detail page.
4. Borrow a book using the confirmation page.
5. Return borrowed books when finished.
6. Check loans in `My Loans`.
7. Review overdue loans in `Overdue Loans` if any.

## Deployment

This project is configured for deployment on Render.

Required environment variables:

- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG=False`
- `DJANGO_ALLOWED_HOSTS=<your-render-app>.onrender.com`
- `DATABASE_URL=<your-database-url>`

Render deployment files included:

- `requirements.txt`
- `Procfile`
- `runtime.txt`

## Notes

- The dependency file is named `requirements.txt`.
- The database file is `db.sqlite3` for local development.
- If you add new models, run `python manage.py makemigrations` and `python manage.py migrate`.
- Activate the virtual environment before running commands:

```powershell
& .\venv\Scripts\Activate.ps1
```
