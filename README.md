# StockChat

A Django-based web application for stock market enthusiasts, providing user authentication, community features, and a contact system. Built with Django 5.2 and Bootstrap 5.

## Features

- **User Authentication** — Sign up, log in, and log out with Django's built-in auth system (session-based, CSRF-protected)
- **Landing Page** — Hero section with feature highlights for real-time quotes, portfolio tracking, and community chat
- **About Page** — Information about StockChat's mission and team
- **Contact Form** — Submit inquiries with validation, stored in the database
- **Admin Panel** — Manage contacts with search, filtering, and list display via Django admin
- **Responsive UI** — Mobile-friendly design using Bootstrap 5.3 and Google Fonts (Poppins)

## Tech Stack

| Layer     | Technology              |
|-----------|-------------------------|
| Backend   | Python 3.13, Django 5.2 |
| Frontend  | Bootstrap 5.3, HTML5    |
| Database  | SQLite3                 |
| HTTP      | Requests 2.32           |

## Project Structure

```
StockChat/
├── manage.py                  # Django management script
├── db.sqlite3                 # SQLite database
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables
├── StockChat/                 # Project settings
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── Home/                      # Main app
│   ├── models.py              # Contact model
│   ├── views.py               # All view functions
│   ├── urls.py                # URL routing
│   ├── admin.py               # Admin configuration
│   └── migrations/
└── templates/
    ├── base.html              # Base template with navbar/footer
    └── Home/
        ├── home.html
        ├── about.html
        ├── contact.html
        ├── login.html
        └── signup.html
```

## Getting Started

### Prerequisites

- Python 3.13+

### Installation

```bash
# Clone the repository
git clone https://github.com/thequantummenece/StockLoss.git
cd StockLoss/StockChat

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt

# Run database migrations
python manage.py migrate

# Create a superuser (optional, for admin access)
python manage.py createsuperuser

# Start the development server
python manage.py runserver
```

The app will be available at `http://127.0.0.1:8000/`.

## Routes

| URL        | Method     | Description          |
|------------|------------|----------------------|
| `/`        | GET        | Home / landing page  |
| `/about/`  | GET        | About page           |
| `/contact/`| GET, POST  | Contact form         |
| `/signup/` | GET, POST  | User registration    |
| `/login/`  | GET, POST  | User login           |
| `/logout/` | GET        | User logout          |
| `/admin/`  | GET, POST  | Django admin panel   |

## Database Models

### Contact

| Field       | Type          | Description                  |
|-------------|---------------|------------------------------|
| name        | CharField     | Contact's name (max 100)     |
| email       | EmailField    | Contact's email              |
| phone       | CharField     | Phone number (max 15)        |
| content     | TextField     | Message body                 |
| dob         | DateField     | Date of birth (optional)     |
| created_at  | DateTimeField | Auto-set on creation         |

User accounts use Django's built-in `User` model.

## Running Tests

```bash
python manage.py test
```
