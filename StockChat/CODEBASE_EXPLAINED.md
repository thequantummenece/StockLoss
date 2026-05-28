# StockChat — Complete Codebase Explanation

This document walks through every file in the StockChat Django project, explaining what each piece does, why it exists, and how it connects to the rest of the system.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Directory Structure](#2-directory-structure)
3. [Entry Points — manage.py, wsgi.py, asgi.py](#3-entry-points)
4. [Configuration — settings.py and .env](#4-configuration)
5. [URL Routing — StockChat/urls.py and Home/urls.py](#5-url-routing)
6. [Models — Home/models.py](#6-models)
7. [Forms — Home/forms.py](#7-forms)
8. [Views — Home/views.py](#8-views)
9. [Admin — Home/admin.py](#9-admin)
10. [App Config — Home/apps.py](#10-app-config)
11. [Migrations](#11-migrations)
12. [Templates](#12-templates)
13. [Tests — Home/tests.py](#13-tests)
14. [Other Files — requirements.txt, .gitignore, .env](#14-other-files)
15. [Request Lifecycle — How a Request Flows Through the App](#15-request-lifecycle)

---

## 1. Project Overview

StockChat is a Django 5.2.7 web application that provides:
- **User authentication** — signup, login, logout
- **Portfolio tracking** — add stocks, view holdings, delete entries
- **Contact form** — visitors can submit messages
- **Static pages** — home (landing) and about

The architecture is a single Django project (`StockChat`) with one app (`Home`) that contains all models, views, forms, and templates. It uses Django's built-in `User` model for authentication and SQLite as the database.

**Tech stack:**
- Python 3.13, Django 5.2.7
- Bootstrap 5.3.2 (via CDN) for the frontend
- python-dotenv for environment variable management
- SQLite (development database)

---

## 2. Directory Structure

```
StockChat/                          # Django project root (where manage.py lives)
├── manage.py                       # CLI entry point for Django commands
├── .env                            # Environment variables (SECRET_KEY, DEBUG)
├── .gitignore                      # Files excluded from version control
├── requirements.txt                # Python package dependencies
├── db.sqlite3                      # SQLite database file (auto-created)
│
├── StockChat/                      # Project configuration package
│   ├── __init__.py                 # Makes this directory a Python package
│   ├── settings.py                 # All Django settings
│   ├── urls.py                     # Root URL configuration
│   ├── wsgi.py                     # WSGI entry point (production sync server)
│   └── asgi.py                     # ASGI entry point (production async server)
│
├── Home/                           # The main (and only) Django app
│   ├── __init__.py                 # Makes this directory a Python package
│   ├── apps.py                     # App configuration class
│   ├── models.py                   # Database models (Portfolio, Contact)
│   ├── forms.py                    # Form classes (ContactForm, PortfolioAddForm)
│   ├── views.py                    # View functions (all page logic)
│   ├── urls.py                     # App-level URL patterns
│   ├── admin.py                    # Django admin customization
│   ├── tests.py                    # Automated test suite (31 tests)
│   └── migrations/                 # Database migration files
│       ├── __init__.py
│       ├── 0001_initial.py         # Creates Contact model
│       ├── 0002_portfolio.py       # Creates Portfolio model
│       ├── 0003_add_ticker_to_portfolio.py  # Adds ticker field + data migration
│       └── 0004_update_portfolio_constraint_and_related_name.py
│
└── templates/                      # HTML templates (project-level)
    ├── base.html                   # Master layout (navbar, footer, CSS)
    └── Home/
        ├── home.html               # Landing page with hero banner
        ├── about.html              # About page
        ├── contact.html            # Contact form page
        ├── signup.html             # Registration page
        ├── login.html              # Login page
        └── portfolio.html          # Portfolio dashboard
```

---

## 3. Entry Points

### `manage.py`

```python
#!/usr/bin/env python
import os
import sys

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'StockChat.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
```

**What it does:** This is Django's command-line interface. Every `python manage.py <command>` goes through this file.

- `os.environ.setdefault(...)` — Sets the `DJANGO_SETTINGS_MODULE` environment variable to tell Django which settings file to use. `setdefault` means it only sets it if not already defined (so you can override it externally).
- `execute_from_command_line(sys.argv)` — Parses CLI arguments (`runserver`, `migrate`, `test`, etc.) and dispatches to the appropriate Django management command.
- The `try/except ImportError` block provides a helpful error message if Django isn't installed — common when you forget to activate your virtual environment.

**Common commands run through this:**
```bash
python manage.py runserver       # Start dev server
python manage.py migrate         # Apply database migrations
python manage.py makemigrations  # Generate migration files from model changes
python manage.py test Home       # Run the test suite
python manage.py createsuperuser # Create an admin user
```

### `StockChat/wsgi.py`

```python
import os
from django.core.wsgi import get_wsgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'StockChat.settings')
application = get_wsgi_application()
```

**What it does:** Exposes the WSGI (Web Server Gateway Interface) `application` object. This is the entry point for synchronous production servers like Gunicorn or uWSGI. The variable **must** be named `application` — that's the WSGI spec convention.

WSGI is the standard Python protocol for web servers to communicate with web frameworks. When you deploy with `gunicorn StockChat.wsgi:application`, Gunicorn imports this file and calls `application` for every incoming HTTP request.

### `StockChat/asgi.py`

```python
import os
from django.core.asgi import get_asgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'StockChat.settings')
application = get_asgi_application()
```

**What it does:** Same as WSGI but for ASGI (Asynchronous Server Gateway Interface). Used by async servers like Uvicorn or Daphne. Needed if you want WebSockets, HTTP/2, or async views. Currently the project uses standard synchronous views, so this file exists as a placeholder for future async support.

---

## 4. Configuration

### `StockChat/settings.py`

This is the central configuration file. Every Django setting is defined here. Let's walk through each section:

#### Environment Setup

```python
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")
```

- `BASE_DIR` — Resolves to the `StockChat/` directory (where `manage.py` lives). `Path(__file__)` is this settings file, `.resolve()` makes it absolute, `.parent.parent` goes up two directories (from `StockChat/StockChat/settings.py` to `StockChat/`).
- `load_dotenv(...)` — Reads the `.env` file and loads its key-value pairs into `os.environ`. This is provided by the `python-dotenv` package. It allows you to keep secrets out of source code.

#### Security Settings

```python
SECRET_KEY = os.environ.get("SECRET_KEY", "django-insecure-change-me-in-production")
DEBUG = os.environ.get("DEBUG", "False").lower() in ("true", "1", "yes")
ALLOWED_HOSTS = [
    h.strip()
    for h in os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    if h.strip()
]
```

- `SECRET_KEY` — A cryptographic secret used for signing cookies, CSRF tokens, password reset tokens, and sessions. **Must be unique and unpredictable in production.** Read from the environment so it's never hardcoded in source code.
- `DEBUG` — When `True`, Django shows detailed error pages with stack traces. **Must be `False` in production** for security. The expression converts string values like `"True"`, `"1"`, `"yes"` to a boolean.
- `ALLOWED_HOSTS` — A list of hostnames the server will respond to. Prevents HTTP Host header attacks. Parsed from a comma-separated environment variable (e.g., `"mysite.com,www.mysite.com"`). The list comprehension strips whitespace and filters empty strings.

#### Installed Apps

```python
INSTALLED_APPS = [
    'django.contrib.admin',          # Built-in admin interface
    'django.contrib.auth',           # Authentication system (User model, login, permissions)
    'django.contrib.contenttypes',   # Tracks models across apps (used by auth)
    'django.contrib.sessions',       # Server-side session storage
    'django.contrib.messages',       # Flash messages (success/error notifications)
    'django.contrib.staticfiles',    # Serves CSS/JS/images in development
    'Home',                          # Our custom app
]
```

Each entry tells Django to include that app — it discovers models, migrations, admin registrations, template tags, etc. The order matters: `contenttypes` must come before `auth` because auth depends on it.

#### Middleware

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',      # HTTPS redirects, HSTS headers
    'django.contrib.sessions.middleware.SessionMiddleware', # Reads/writes session cookies
    'django.middleware.common.CommonMiddleware',           # URL normalization (trailing slashes)
    'django.middleware.csrf.CsrfViewMiddleware',          # CSRF token validation on POST
    'django.contrib.auth.middleware.AuthenticationMiddleware', # Attaches request.user
    'django.contrib.messages.middleware.MessageMiddleware',    # Enables flash messages
    'django.middleware.clickjacking.XFrameOptionsMiddleware', # Sets X-Frame-Options header
]
```

Middleware is a pipeline — every request passes through each middleware top-to-bottom, and every response passes back bottom-to-top. Order matters:
- `SessionMiddleware` must come before `AuthenticationMiddleware` (auth reads from the session).
- `CsrfViewMiddleware` must come before any view that processes POST forms.

#### Templates

```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],   # Project-level templates directory
        'APP_DIRS': True,                     # Also look in each app's templates/ folder
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',  # Adds `request` to templates
                'django.contrib.auth.context_processors.auth',  # Adds `user` and `perms`
                'django.contrib.messages.context_processors.messages', # Adds `messages`
            ],
        },
    },
]
```

- `DIRS` — Explicit directories to search for templates. Our templates live at `StockChat/templates/`.
- `APP_DIRS: True` — Also searches `<app>/templates/` in each installed app.
- **Context processors** automatically inject variables into every template context. That's why `{{ user }}` and `{{ messages }}` are available in every template without the view explicitly passing them.

#### Database

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

SQLite — a file-based database. Perfect for development. The file `db.sqlite3` is auto-created on first migration. For production you'd typically switch to PostgreSQL.

#### Password Validators

```python
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
```

These run when a user creates an account or changes their password:
1. **UserAttributeSimilarityValidator** — Rejects passwords too similar to username/email
2. **MinimumLengthValidator** — Requires at least 8 characters (default)
3. **CommonPasswordValidator** — Rejects 20,000 most common passwords (e.g., "password123")
4. **NumericPasswordValidator** — Rejects all-numeric passwords

#### Static Files and Auth

```python
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'
```

- `STATIC_URL` — URL prefix for static files (CSS/JS). In templates: `{% static 'file.css' %}` resolves to `/static/file.css`.
- `STATIC_ROOT` — Where `collectstatic` copies files for production serving.
- `DEFAULT_AUTO_FIELD` — All auto-created primary keys use `BigAutoField` (64-bit integers) instead of the older `AutoField` (32-bit).
- `LOGIN_URL` — Where `@login_required` redirects unauthenticated users. `'login'` is the **URL name**, not a path.
- `LOGIN_REDIRECT_URL` / `LOGOUT_REDIRECT_URL` — Where to redirect after login/logout (used by Django's built-in auth views; our custom views handle their own redirects).

### `.env`

```
SECRET_KEY=django-insecure-*2ar_=(__8k_k5j!u%kg51@=mxl5$gg4$k*_6y5v&22c$j5acb
DEBUG=True
```

This file stores environment-specific configuration. `load_dotenv()` in `settings.py` reads it. This file is listed in `.gitignore` so it's never committed to version control. In production, you'd set these as real environment variables on the server instead.

---

## 5. URL Routing

Django uses a two-level URL configuration:

### `StockChat/urls.py` (Root URL Config)

```python
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('Home.urls')),
]
```

- `path('admin/', admin.site.urls)` — All URLs starting with `/admin/` go to Django's built-in admin interface.
- `path('', include('Home.urls'))` — Everything else is delegated to `Home/urls.py`. The empty string `''` means no prefix — the Home app's URLs are mounted at the root.

`include()` is a key Django pattern: it lets each app define its own URL patterns, then the root config wires them together. This keeps URL definitions close to the views they reference.

### `Home/urls.py` (App URL Config)

```python
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('portfolio/', views.portfolio_view, name='portfolio'),
    path('portfolio/delete/<int:pk>/', views.portfolio_delete, name='portfolio_delete'),
]
```

Each `path()` maps a URL pattern to a view function:
- **First argument** — The URL pattern. `''` matches the root URL (`/`). `'about/'` matches `/about/`.
- **Second argument** — The view function to call when this URL is requested.
- **`name`** — A symbolic name used throughout the codebase for reverse URL resolution. In templates: `{% url 'home' %}` produces `/`. In Python: `reverse('home')` produces `/`.
- **`<int:pk>`** — A URL path converter. Captures the integer from the URL (e.g., `/portfolio/delete/42/` captures `pk=42`) and passes it as a keyword argument to the view function. `int:` ensures only numeric values match.

**Complete URL table:**

| URL | View | HTTP Methods | Auth Required |
|-----|------|-------------|---------------|
| `/` | `home` | GET | No |
| `/about/` | `about` | GET | No |
| `/contact/` | `contact` | GET, POST | No |
| `/signup/` | `signup_view` | GET, POST | No |
| `/login/` | `login_view` | GET, POST | No |
| `/logout/` | `logout_view` | POST only | No |
| `/portfolio/` | `portfolio_view` | GET, POST | Yes |
| `/portfolio/delete/<pk>/` | `portfolio_delete` | POST only | Yes |

---

## 6. Models

### `Home/models.py`

Models define the database schema. Each model class becomes a database table. Each class attribute becomes a column.

#### Portfolio Model

```python
class Portfolio(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='portfolios')
    ticker = models.CharField(max_length=20, default='UNKNOWN')
    stock_name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()
    invested = models.DecimalField(max_digits=12, decimal_places=2)
    added_at = models.DateTimeField(auto_now_add=True)
```

**Fields explained:**

- `user` — A **ForeignKey** (many-to-one relationship) to Django's built-in `User` model. Each portfolio entry belongs to one user; each user can have many entries.
  - `on_delete=models.CASCADE` — If the user is deleted, all their portfolio entries are automatically deleted too.
  - `related_name='portfolios'` — Allows reverse access: `some_user.portfolios.all()` returns all portfolio entries for that user.

- `ticker` — The stock symbol (e.g., "AAPL", "GOOG"). `max_length=20` sets the database column to `VARCHAR(20)`. `default='UNKNOWN'` exists for the data migration that backfilled this field.

- `stock_name` — Human-readable company name (e.g., "Apple Inc.").

- `quantity` — Number of shares held. `PositiveIntegerField` enforces `>= 0` at the database level.

- `invested` — Total money invested. `DecimalField` is used instead of `FloatField` because **floating-point arithmetic introduces rounding errors with money**. `max_digits=12` allows values up to 9,999,999,999.99. `decimal_places=2` stores cents precision.

- `added_at` — Timestamp of when the entry was first created. `auto_now_add=True` means Django automatically sets this to the current time on creation and the field is not editable afterward.

```python
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "ticker"],
                name="unique_user_ticker",
            ),
        ]
```

**Meta.constraints** — Defines database-level constraints. This `UniqueConstraint` ensures that a user can only have **one entry per ticker symbol**. If user #1 already has an "AAPL" entry, trying to create another "AAPL" for user #1 raises an `IntegrityError`. User #2 can still have their own "AAPL" entry.

This uses the modern `UniqueConstraint` API (Django 2.2+) instead of the older `unique_together` which is deprecated in Django 5.x.

```python
    def __str__(self):
        return f"{self.user.username} — {self.ticker} x{self.quantity}"
```

**`__str__`** — Python's string representation. Used in the admin interface, shell, and anywhere you print a Portfolio object. Example: `"trader — AAPL x10"`.

```python
    @property
    def avg_price(self):
        if self.quantity > 0:
            return round(self.invested / self.quantity, 2)
        return 0
```

**`avg_price`** — A computed property (not stored in the database). Divides total invested by quantity to get the average cost per share. The `@property` decorator lets you access it like an attribute (`holding.avg_price`) instead of calling it as a method (`holding.avg_price()`). The guard `if self.quantity > 0` prevents `ZeroDivisionError`.

#### Contact Model

```python
class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    content = models.TextField()
    dob = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

Stores contact form submissions.

- `EmailField` — A `CharField` that validates email format.
- `TextField` — Unlimited-length text (maps to `TEXT` in SQL).
- `blank=True, null=True` on `dob` — `blank=True` means the field is optional in forms; `null=True` means the database stores `NULL` when no value is provided. Both are needed for optional fields.

```python
    def __str__(self):
        return f"{self.name} — {self.email}"
```

---

## 7. Forms

### `Home/forms.py`

Django forms handle data validation, cleaning, and HTML rendering. They sit between the raw HTTP request and the database.

#### ContactForm

```python
class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ["name", "email", "phone", "content", "dob"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "content": forms.Textarea(attrs={"class": "form-control", "rows": 5}),
            "dob": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        }
```

**`ModelForm`** — A form that is automatically generated from a model. It knows the field types, max lengths, and required/optional status from the model definition. `fields` specifies which model fields to include in the form.

**`widgets`** — Overrides the default HTML widgets. `attrs={"class": "form-control"}` adds Bootstrap's CSS class to each input element for consistent styling. `"type": "date"` on the DOB field tells the browser to show a date picker.

```python
    def clean_name(self):
        name = self.cleaned_data["name"]
        if len(name) < 3:
            raise forms.ValidationError("Name must be at least 3 characters.")
        return name
```

**`clean_<fieldname>`** methods — Django's per-field validation hook. After Django's built-in validation runs (type checking, max_length, etc.), it calls `clean_name()` for the `name` field. If validation fails, raise `ValidationError`. The returned value becomes the cleaned data. There are similar validators for `phone` (min 10 chars) and `content` (min 3 chars).

#### PortfolioAddForm

```python
class PortfolioAddForm(forms.Form):
    ticker = forms.CharField(max_length=20)
    stock_name = forms.CharField(max_length=100)
    quantity = forms.IntegerField(min_value=1)
    invested = forms.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal("0.01"))
```

**`forms.Form`** (not `ModelForm`) — A plain form not tied to a model. Used here because the portfolio view does custom logic (update-or-create), so we don't want `form.save()` to just create a model instance blindly.

- `IntegerField(min_value=1)` — Ensures quantity is at least 1. Django handles the validation automatically.
- `DecimalField(min_value=Decimal("0.01"))` — Ensures invested amount is positive. Uses `Decimal` (not `float`) to avoid floating-point rounding errors with money.

```python
    def clean_ticker(self):
        return self.cleaned_data["ticker"].strip().upper()

    def clean_stock_name(self):
        return self.cleaned_data["stock_name"].strip()
```

These normalizers clean user input: trim whitespace and uppercase the ticker so "aapl" becomes "AAPL". This ensures consistent storage and prevents duplicate entries that differ only in case.

---

## 8. Views

### `Home/views.py`

Views are functions that receive an HTTP request and return an HTTP response. Every URL maps to a view.

#### Static Pages

```python
def home(request):
    return render(request, "Home/home.html")

def about(request):
    return render(request, "Home/about.html")
```

`render(request, template_name)` — Loads the template, renders it with the default context (which includes `user`, `messages`, `request` via context processors), and returns an `HttpResponse` with the rendered HTML.

#### Contact View

```python
def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your form has been sent!")
            return redirect("contact")
        else:
            messages.warning(request, "Please correct the errors below.")
    else:
        form = ContactForm()
    return render(request, "Home/contact.html", {"form": form})
```

This follows Django's standard **form handling pattern**:

1. **GET request** — Create an empty form and display it.
2. **POST request** — Bind the form to the submitted data (`request.POST`).
3. **Validation** — `form.is_valid()` runs all field validators and `clean_*` methods.
4. **Valid** — `form.save()` creates a `Contact` object in the database (since `ContactForm` is a `ModelForm`). Then redirect (PRG pattern — Post/Redirect/Get) to prevent duplicate submissions on browser refresh.
5. **Invalid** — Re-render the form with error messages attached. The form remembers the submitted values so the user doesn't lose their input.

`messages.success(request, ...)` — Stores a flash message in the session. It's displayed once on the next page load (in `base.html`'s messages block) and then automatically cleared.

#### Signup View

```python
def signup_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully!")
            return redirect("home")
    else:
        form = UserCreationForm()
    return render(request, "Home/signup.html", {"form": form})
```

- `request.user.is_authenticated` — If the user is already logged in, redirect them away from the signup page. `request.user` is set by `AuthenticationMiddleware` — it's either a real `User` object or `AnonymousUser`.
- `UserCreationForm` — Django's built-in form with `username`, `password1`, `password2` fields. It handles password strength validation and ensures the two passwords match.
- `form.save()` — Creates the `User` in the database and hashes the password.
- `login(request, user)` — Immediately logs in the newly created user by creating a session.

#### Login View

```python
def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            next_url = request.POST.get("next", request.GET.get("next", ""))
            if next_url and url_has_allowed_host_and_scheme(
                next_url, allowed_hosts={request.get_host()}
            ):
                return redirect(next_url)
            return redirect("home")
    else:
        form = AuthenticationForm()
    return render(request, "Home/login.html", {"form": form})
```

- `AuthenticationForm` — Django's built-in form that validates username+password against the database. If valid, `form.get_user()` returns the authenticated `User` object.
- **Open redirect protection** — When `@login_required` redirects to `/login/?next=/portfolio/`, we want to honor that `next` parameter after login. But an attacker could craft `?next=https://evil.com` to phish users. `url_has_allowed_host_and_scheme()` checks that:
  1. The URL's host matches our server (`request.get_host()`)
  2. The scheme is safe (http/https)
  If the URL fails validation, we fall through to the default `redirect("home")`.
- `request.POST.get("next", request.GET.get("next", ""))` — The `next` value can come from either a hidden form field (POST) or the URL query string (GET). The POST value takes priority.

#### Logout View

```python
@require_POST
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("home")
```

- `@require_POST` — A Django decorator that returns HTTP 405 (Method Not Allowed) for any non-POST request. This prevents CSRF logout attacks — without this, an attacker could embed `<img src="/logout/">` on any page to force-logout users.
- `logout(request)` — Destroys the session and clears `request.user`.

#### Portfolio View

```python
@login_required
def portfolio_view(request):
    if request.method == "POST":
        form = PortfolioAddForm(request.POST)
        if form.is_valid():
            ticker = form.cleaned_data["ticker"]
            stock_name = form.cleaned_data["stock_name"]
            quantity = form.cleaned_data["quantity"]
            invested = form.cleaned_data["invested"]

            updated = Portfolio.objects.filter(
                user=request.user, ticker=ticker
            ).update(
                quantity=F("quantity") + quantity,
                invested=F("invested") + invested,
            )
            if updated:
                messages.success(request, f"{ticker} updated — added {quantity} more shares.")
            else:
                Portfolio.objects.create(
                    user=request.user,
                    ticker=ticker,
                    stock_name=stock_name,
                    quantity=quantity,
                    invested=invested,
                )
                messages.success(request, f"{ticker} added to your portfolio!")
        else:
            messages.warning(request, "Please enter valid data for all fields.")
        return redirect("portfolio")

    holdings = Portfolio.objects.filter(user=request.user).order_by("ticker")
    totals = holdings.aggregate(
        total_invested=Sum("invested"),
        total_shares=Sum("quantity"),
    )
    return render(request, "Home/portfolio.html", {
        "holdings": holdings,
        "total_invested": totals["total_invested"] or 0,
        "total_shares": totals["total_shares"] or 0,
    })
```

**`@login_required`** — Redirects to `LOGIN_URL` (i.e., `/login/`) if the user isn't authenticated. Appends `?next=/portfolio/` so the login view can redirect back after authentication.

**POST handling (adding a stock):**

The update-or-create logic works in two steps:

1. **Try to update** — `Portfolio.objects.filter(user=..., ticker=...).update(...)` issues a single SQL `UPDATE` statement. It returns the number of rows affected (0 or 1).
2. **If no rows updated, create** — The ticker doesn't exist for this user yet, so create a new entry.

**`F("quantity") + quantity`** — `F()` expressions generate SQL that operates on the column value directly in the database, rather than reading the value into Python, modifying it, and writing it back. This prevents race conditions: if two requests try to add shares simultaneously, both updates are applied atomically at the database level. Without `F()`, one update could overwrite the other.

**GET handling (displaying the portfolio):**

- `holdings.aggregate(...)` — Executes a SQL `SELECT SUM(invested), SUM(quantity)` query in the database. Much more efficient than loading all rows into Python and summing in a loop. Returns a dictionary like `{"total_invested": Decimal("4000.00"), "total_shares": 15}`.
- `or 0` — If there are no holdings, `Sum()` returns `None`. The `or 0` provides a sensible default.

#### Portfolio Delete View

```python
@login_required
@require_POST
def portfolio_delete(request, pk):
    holding = get_object_or_404(Portfolio, pk=pk, user=request.user)
    ticker = holding.ticker
    holding.delete()
    messages.success(request, f"{ticker} removed from portfolio.")
    return redirect("portfolio")
```

- **Stacked decorators** — `@login_required` runs first (outermost), then `@require_POST`. If the user isn't logged in, they get redirected before the POST check even runs.
- `get_object_or_404(Portfolio, pk=pk, user=request.user)` — Fetches the object or returns HTTP 404. The `user=request.user` filter is critical for security: it ensures users can only delete **their own** entries. Without it, any logged-in user could delete anyone's holdings by guessing PKs.
- `holding.delete()` — Removes the row from the database.

---

## 9. Admin

### `Home/admin.py`

```python
from django.contrib import admin
from .models import Contact, Portfolio

@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('user', 'ticker', 'stock_name', 'quantity', 'invested', 'added_at')
    search_fields = ('ticker', 'stock_name', 'user__username')
    list_filter = ('added_at', 'user')

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'created_at')
    search_fields = ('name', 'email')
    list_filter = ('created_at',)
```

**`@admin.register(Model)`** — Registers the model with Django's admin site. Equivalent to `admin.site.register(Portfolio, PortfolioAdmin)`.

**`ModelAdmin` options:**
- `list_display` — Columns shown in the admin list view. By default Django only shows `__str__()`.
- `search_fields` — Adds a search box. `user__username` uses Django's double-underscore syntax to search across the ForeignKey relationship (search by the related user's username).
- `list_filter` — Adds filter sidebar. Click a user or date to filter the list.

Access the admin at `/admin/` after creating a superuser with `python manage.py createsuperuser`.

---

## 10. App Config

### `Home/apps.py`

```python
from django.apps import AppConfig

class HomeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Home'
```

Every Django app has a configuration class. Django discovers it automatically when `'Home'` is in `INSTALLED_APPS`.

- `default_auto_field` — Sets the default primary key type for models in this app to `BigAutoField` (64-bit integer). This matches the project-level `DEFAULT_AUTO_FIELD` setting.
- `name = 'Home'` — The Python import path of the app. Must match the directory name exactly.

---

## 11. Migrations

Migrations are Django's way of evolving the database schema over time. Each migration file is a Python script that describes a set of database operations.

### `0001_initial.py` — Creates Contact Table

```python
operations = [
    migrations.CreateModel(
        name="Contact",
        fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, ...)),
            ("name", models.CharField(max_length=100)),
            ("email", models.EmailField(max_length=254)),
            ("phone", models.CharField(max_length=15)),
            ("content", models.TextField()),
            ("dob", models.DateField(blank=True, null=True)),
            ("created_at", models.DateTimeField(auto_now_add=True)),
        ],
    ),
]
```

Creates the `Home_contact` table with all its columns. The `id` field is auto-created by Django as the primary key.

### `0002_portfolio.py` — Creates Portfolio Table

Creates `Home_portfolio` with `stock_name`, `quantity`, `invested`, `added_at`, and a `user_id` foreign key to `auth_user`.

`dependencies` lists what must run first:
- `("Home", "0001_initial")` — The Contact migration
- `migrations.swappable_dependency(settings.AUTH_USER_MODEL)` — Ensures the User table exists (since Portfolio has a FK to it)

### `0003_add_ticker_to_portfolio.py` — Adds Ticker Field + Data Migration

This is a three-step migration:

```python
operations = [
    # Step 1: Add the column with a temporary default
    migrations.AddField(
        model_name='portfolio',
        name='ticker',
        field=models.CharField(default='UNKNOWN', max_length=20),
        preserve_default=False,
    ),
    # Step 2: Data migration — populate ticker from stock_name and merge duplicates
    migrations.RunPython(populate_ticker_and_merge, migrations.RunPython.noop),
    # Step 3: Add unique constraint
    migrations.AlterUniqueTogether(
        name='portfolio',
        unique_together={('user', 'ticker')},
    ),
]
```

**`RunPython`** — Runs arbitrary Python code during migration. The `populate_ticker_and_merge` function:
1. Sets each row's `ticker` to its `stock_name` uppercased with spaces removed
2. Merges duplicate (user, ticker) pairs by summing their quantity and invested values

`migrations.RunPython.noop` is the reverse operation — it does nothing, meaning this migration can't be cleanly reversed.

`preserve_default=False` tells Django: "The default='UNKNOWN' is only for this migration (to populate existing rows), not a permanent model default."

### `0004_update_portfolio_constraint_and_related_name.py`

Modernizes the schema:
1. Removes the old `unique_together` constraint
2. Updates the `ticker` field definition
3. Changes `related_name` from `'portfolio'` to `'portfolios'`
4. Adds the new-style `UniqueConstraint`

---

## 12. Templates

Templates use Django's template language (DTL) with Bootstrap 5 for styling.

### `base.html` — Master Layout

Every other template **extends** this one. It defines the overall page structure:

```
┌─────────────────────────────────────┐
│ <nav> — Navbar                      │
├─────────────────────────────────────┤
│ {% block pre_content %}             │  ← Page headers go here
├─────────────────────────────────────┤
│ {% if messages %} ... alerts ...    │  ← Flash messages
├─────────────────────────────────────┤
│ {% block content %}                 │  ← Main page content
├─────────────────────────────────────┤
│ <footer>                            │
└─────────────────────────────────────┘
```

**Key template features:**

- **`{% block name %}...{% endblock %}`** — Defines overridable regions. Child templates fill these blocks.
- **`{% url 'name' %}`** — Reverse URL resolution. Generates the URL from its name, so URLs are never hardcoded in HTML.
- **`{% if user.is_authenticated %}`** — Conditional rendering. Shows different nav items for logged-in vs anonymous users.
- **`{% csrf_token %}`** — Inserts a hidden CSRF token in forms. Django's CSRF middleware rejects POST requests without a valid token.
- **`{{ message.tags }}`** — Outputs the message level as a CSS class (e.g., `success`, `warning`). Bootstrap maps `alert-success` to green, `alert-warning` to yellow.

**Sticky footer CSS:**

```css
html { height: 100%; }
body { min-height: 100%; display: flex; flex-direction: column; }
main { flex: 1 0 auto; }
footer { flex-shrink: 0; }
```

Makes the body a flex column that stretches to fill the viewport. `main` grows to fill available space (`flex: 1`), pushing the footer to the bottom even when content is short.

**Design system classes:**
- `.hero` — Full-viewport banner with background image and gradient overlay (home page only)
- `.page-header` — Consistent gradient header for all inner pages
- `.form-card` — Centered card with shadow for form pages (contact, login, signup)
- `.port-header` / `.port-table` — Portfolio-specific dashboard styling
- `.nav-logout-form` / `.nav-logout-btn` — Clean logout button in the navbar

### `home.html`

The landing page. Three sections:
1. **Hero** — Full-viewport banner with CTA button (links to signup or portfolio depending on auth state)
2. **Features** — Three-column grid showing app capabilities
3. **CTA** — Sign-up call to action

### `about.html`

Uses `{% block pre_content %}` for the page header, then static content about the company.

### `contact.html`

Renders the `ContactForm` by iterating over its fields:

```django
{% for field in form %}
<div class="mb-3">
    <label for="{{ field.id_for_label }}" class="form-label">{{ field.label }}</label>
    {{ field }}
    {% for error in field.errors %}
    <div class="text-danger small">{{ error }}</div>
    {% endfor %}
</div>
{% endfor %}
```

- `{{ field }}` — Renders the form widget (input, textarea, etc.) as HTML
- `{{ field.id_for_label }}` — The `id` attribute for the `<label>`'s `for` to match
- `{{ field.errors }}` — Validation errors for this specific field

### `signup.html` and `login.html`

Same form-rendering pattern. Signup additionally shows `{{ field.help_text }}` (password rules). Login includes:
- A hidden `next` field to preserve the redirect URL across the POST
- `{{ form.non_field_errors }}` — Errors not attached to any specific field (e.g., "Invalid username or password")

### `portfolio.html`

The most complex template:

1. **Header** (`pre_content` block) — Shows stats (holdings count, total shares, total invested) and an "Add Stock" button
2. **Collapsible form** — Bootstrap collapse component toggled by the button. Contains a horizontal form row for adding stocks.
3. **Holdings table** — Iterates over `holdings` queryset, showing ticker, quantity, invested, avg price, date, and a delete button per row.
4. **Empty state** — Shows a helpful message when there are no holdings.

The delete button is a mini `<form>` (not an `<a>` link) because deletion must be a POST request:

```django
<form method="post" action="{% url 'portfolio_delete' h.pk %}" class="inline-form"
      onsubmit="return confirm('Remove {{ h.ticker }}?')">
    {% csrf_token %}
    <button type="submit" class="btn btn-sm btn-outline-danger py-0 px-2">x</button>
</form>
```

`onsubmit="return confirm(...)"` — Shows a browser confirmation dialog before submitting.

---

## 13. Tests

### `Home/tests.py`

31 tests organized into 7 test classes. Uses Django's `TestCase` which wraps each test in a database transaction that's rolled back afterward (fast and isolated).

#### Test Classes and What They Cover

**`HomeViewTests` (2 tests)**
- Verifies home and about pages return HTTP 200
- Checks expected content is present in the response

**`ContactViewTests` (5 tests)**
- Page renders on GET
- Valid form submission creates a `Contact` object and redirects
- Short name (< 3 chars) is rejected
- Short phone (< 10 chars) is rejected
- Invalid email format is rejected

**`SignupViewTests` (3 tests)**
- Page renders on GET
- Valid submission creates a `User`, logs them in, redirects to home
- Already-authenticated users are redirected away from the signup page

**`LoginViewTests` (6 tests)**
- Page renders on GET
- Valid credentials log in and redirect to home
- Invalid credentials re-render the login page (HTTP 200, not redirect)
- Already-authenticated users are redirected away
- **Open redirect is blocked** — `?next=https://evil.com` still redirects to home
- **Safe `next` is honored** — `next=/portfolio/` redirects to portfolio after login

**`LogoutViewTests` (2 tests)**
- GET request returns HTTP 405 (Method Not Allowed)
- POST request logs out and redirects to home

**`PortfolioViewTests` (5 tests)**
- Unauthenticated users are redirected to login
- Empty portfolio shows "No holdings yet"
- Adding a stock creates a `Portfolio` object with uppercased ticker
- Adding to an existing ticker updates quantity and invested (F() expression)
- Portfolio totals are correctly computed via aggregate()

**`PortfolioDeleteTests` (4 tests)**
- GET request returns HTTP 405
- POST deletes the user's own holding
- Cannot delete another user's holding (returns 404)
- Deleting a nonexistent PK returns 404

**`PortfolioModelTests` (3 tests)**
- `avg_price` computes correctly (1500 / 10 = 150)
- `avg_price` returns 0 when quantity is 0 (no ZeroDivisionError)
- `__str__` returns expected format

**Key testing patterns used:**

- `self.client` — Django's test client simulates HTTP requests without a server
- `reverse("name")` — Generates URLs by name (not hardcoded paths)
- `self.assertRedirects(response, url)` — Checks the response is a redirect to the expected URL
- `self.assertContains(response, text)` — Checks the text appears in the response body
- `self.client.force_login(user)` — Logs in without needing a password (test shortcut)

---

## 14. Other Files

### `requirements.txt`

```
asgiref==3.10.0         # ASGI spec implementation (Django dependency)
certifi==2025.10.5      # SSL certificate bundle (requests dependency)
charset-normalizer==3.4.4  # Character encoding detection (requests dependency)
Django==5.2.7           # The web framework
idna==3.11              # International domain name support (requests dependency)
python-dotenv==1.2.1    # Loads .env files into os.environ
requests==2.32.5        # HTTP client library (may be used for external API calls)
sqlparse==0.5.3         # SQL formatting (Django dependency for debug toolbar)
tzdata==2025.2          # Timezone database (required on Windows)
urllib3==2.5.0          # HTTP library (requests dependency)
```

Install all dependencies with: `pip install -r requirements.txt`

### `.gitignore`

Tells Git which files/directories to exclude from version control:

```
*.pyc / __pycache__/     # Compiled Python bytecode (auto-generated)
svenv/ / venv/ / .venv/  # Virtual environments (large, machine-specific)
db.sqlite3               # Database file (contains local data)
staticfiles/             # Collected static files (generated by collectstatic)
.env                     # Environment secrets (NEVER commit)
.idea/ / .vscode/        # IDE configuration (personal preference)
.DS_Store                # macOS directory metadata
```

---

## 15. Request Lifecycle — How a Request Flows Through the App

Here's the complete journey of a request to `POST /portfolio/` (adding a stock):

```
1. Browser sends POST /portfolio/ with form data + CSRF token + session cookie

2. Django's WSGI/ASGI handler receives the request

3. MIDDLEWARE PIPELINE (top to bottom):
   ├─ SecurityMiddleware       → checks HTTPS, adds security headers
   ├─ SessionMiddleware        → reads session cookie, loads session data
   ├─ CommonMiddleware         → normalizes URL (trailing slash)
   ├─ CsrfViewMiddleware      → validates CSRF token from POST data
   ├─ AuthenticationMiddleware → reads user ID from session, sets request.user
   ├─ MessageMiddleware        → enables flash messages
   └─ XFrameOptionsMiddleware  → adds X-Frame-Options header

4. URL RESOLUTION:
   ├─ StockChat/urls.py: path('', include('Home.urls'))  → matches, strips nothing
   └─ Home/urls.py: path('portfolio/', views.portfolio_view)  → matches!

5. DECORATOR CHECK:
   └─ @login_required → request.user.is_authenticated? Yes → proceed

6. VIEW FUNCTION: portfolio_view(request)
   ├─ request.method == "POST" → True
   ├─ form = PortfolioAddForm(request.POST)
   ├─ form.is_valid()
   │   ├─ Django validates each field (type, min_value, max_length)
   │   ├─ clean_ticker() → strips and uppercases
   │   └─ clean_stock_name() → strips whitespace
   ├─ Portfolio.objects.filter(user=..., ticker=...).update(F("quantity") + ...)
   │   └─ SQL: UPDATE home_portfolio SET quantity = quantity + 5 WHERE user_id=1 AND ticker='AAPL'
   │   └─ Returns 1 (one row updated)
   ├─ messages.success(request, "AAPL updated...")
   └─ return redirect("portfolio")  → HttpResponseRedirect to /portfolio/

7. MIDDLEWARE PIPELINE (bottom to top):
   ├─ MessageMiddleware        → stores flash message in session
   ├─ SessionMiddleware        → writes session to database, sets cookie
   └─ SecurityMiddleware       → adds security headers

8. Browser receives HTTP 302, follows redirect to GET /portfolio/

9. Steps 3-7 repeat for the GET request, this time:
   ├─ portfolio_view runs the GET branch
   ├─ holdings = Portfolio.objects.filter(user=request.user).order_by("ticker")
   │   └─ SQL: SELECT * FROM home_portfolio WHERE user_id=1 ORDER BY ticker
   ├─ holdings.aggregate(Sum("invested"), Sum("quantity"))
   │   └─ SQL: SELECT SUM(invested), SUM(quantity) FROM home_portfolio WHERE user_id=1
   └─ render() loads portfolio.html, passes holdings + totals as context

10. Template rendering:
    ├─ portfolio.html extends base.html
    ├─ base.html renders navbar, checks {% if messages %} → shows "AAPL updated" alert
    ├─ portfolio.html renders stats header, holdings table
    └─ Final HTML is returned as the response body

11. Browser renders the page
```

This illustrates how Django's components work together: middleware handles cross-cutting concerns, URL routing dispatches to the right view, forms validate input, the ORM talks to the database, and templates produce the HTML output.
