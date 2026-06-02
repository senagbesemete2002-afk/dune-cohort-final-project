# Library Management System

## Project Overview
This is a Django-based library management application. It allows users to register, log in, browse books, borrow and return books, and track loans with overdue monitoring.

## Main Features
- **User authentication**
  - Register a new account
  - Log in and log out
  - Only authenticated users can borrow books

- **Book catalog**
  - View the full list of books
  - See book details like title, author, and description

- **Book management**
  - Add new books to the library
  - Edit existing book information
  - Delete books when necessary

- **Borrow and return workflow**
  - Borrow a book with confirmation
  - Return a book and update loan status
  - View personal loans in `My Loans`

- **Overdue loans**
  - Display overdue loans separately
  - Help track late returns and manage library inventory

## User Journey
1. Register or log in.
2. Browse the list of available books.
3. Open a book detail page.
4. Borrow the book with a confirmation step.
5. Return the book when finished.
6. Review current loans in `My Loans`.
7. Check overdue loans for any late returns.

## Technology Stack
- Django for backend and views
- SQLite database (`db.sqlite3`)
- HTML templates for UI
- CSS for styling
- Media support for book images

## Project Structure
- `library/models.py` — data models for books and loans
- `library/views.py` — page logic and workflows
- `library/templates/library/` — HTML pages for book list, details, forms, and confirmations
- `config/` — Django settings, URL routing, and app configuration

## Future Improvements
- Add search and filtering for books
- Improve page design and mobile responsiveness
- Add email notification for overdue books
- Add an admin dashboard for library staff