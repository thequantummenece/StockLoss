# StockChat — Complete Codebase Explanation

This document walks through the StockChat Django project, explaining what each piece does, why it exists, and how it connects to the rest of the system.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Directory Structure](#2-directory-structure)
3. [Entry Points — manage.py, wsgi.py, asgi.py](#3-entry-points)
4. [Configuration — settings.py and .env](#4-configuration)
5. [URL Routing](#5-url-routing)
6. [Home App — Core Pages & Auth](#6-home-app)
7. [Portfolio App — Holdings Tracker](#7-portfolio-app)
8. [Communities App — Reddit-Style Posts](#8-communities-app)
9. [Friends App — Social Connections](#9-friends-app)
10. [Chat App — Direct Messaging](#10-chat-app)
11. [Market Data App — Placeholder](#11-market-data-app)
12. [Templates & UI Architecture](#12-templates--ui-architecture)
13. [Migrations](#13-migrations)
14. [Request Lifecycle](#14-request-lifecycle)

---

## 1. Project Overview

StockChat is a Django 5.2.7 web application for stock market investors. It provides:

- **User authentication** — signup, login, logout
- **Portfolio tracking** — add stocks, view holdings, track invested amounts
- **Communities** — Reddit-style posts with upvote/downvote and threaded comments
- **Friends** — send/accept/decline friend requests, search users
- **Chat** — real-time direct messaging between friends (AJAX polling)
- **Contact form** — visitors can submit messages
- **Static pages** — landing page and about

The project follows a **multi-app architecture** where each feature is a separate Django app with its own models, views, forms, URLs, and templates.

**Tech stack:**
- Python 3.13, Django 5.2.7
- Bootstrap 5.3.2 + Bootstrap Icons (via CDN) for the frontend
- Inter font family for professional financial UI
- python-dotenv for environment variable management
- SQLite (development database)

---

## 2. Directory Structure

```
StockChat/
├── manage.py
├── db.sqlite3
├── requirements.txt
├── .env
│
├── StockChat/                     # Project configuration
│   ├── settings.py                # All Django settings
│   ├── urls.py                    # Root URL config — includes all app URLs
│   ├── wsgi.py
│   └── asgi.py
│
├── templates/
│   └── base.html                  # Master layout (navbar, sidebar, footer)
│
├── Home/                          # Core: landing, about, contact, auth
│   ├── models.py                  # Contact model
│   ├── views.py                   # home, about, contact, signup, login, logout
│   ├── forms.py                   # ContactForm
│   ├── urls.py
│   ├── admin.py
│   └── templates/Home/            # home, about, contact, login, signup HTML
│
├── portfolio/                     # Portfolio tracker
│   ├── models.py                  # Portfolio model (db_table='Home_portfolio')
│   ├── views.py                   # portfolio_view, portfolio_delete
│   ├── forms.py                   # PortfolioAddForm
│   ├── urls.py
│   ├── admin.py
│   └── templates/portfolio/
│
├── communities/                   # Reddit-style posts
│   ├── models.py                  # Post, Vote, Comment
│   ├── views.py                   # post_list, post_create, post_detail, post_vote, post_comment, post_delete
│   ├── forms.py                   # PostForm, CommentForm
│   ├── urls.py
│   ├── admin.py
│   ├── templatetags/
│   │   └── community_tags.py      # get_vote filter (dict lookup by post ID)
│   └── templates/communities/     # post_list, post_create, post_detail HTML
│
├── friends/                       # Friend system
│   ├── models.py                  # Friendship model (pending/accepted)
│   ├── views.py                   # friends_list, search_users, send/accept/decline/cancel/unfriend
│   ├── urls.py
│   ├── admin.py
│   ├── templatetags/
│   │   └── friend_tags.py         # get_status filter (dict lookup by user ID)
│   └── templates/friends/         # friends_list, search HTML
│
├── chat/                          # Direct messaging
│   ├── models.py                  # Message model
│   ├── views.py                   # inbox, conversation, send_message, poll_messages, unread_count
│   ├── urls.py
│   ├── admin.py
│   └── templates/chat/            # inbox, conversation, not_friends HTML
│
└── market_data/                   # Placeholder for live market data
    ├── views.py
    ├── urls.py
    └── templates/market_data/
```

---

## 3. Entry Points

### `manage.py`

Django's command-line interface. Every `python manage.py <command>` goes through this file.

- `os.environ.setdefault(...)` sets `DJANGO_SETTINGS_MODULE` so Django knows which settings to load.
- `execute_from_command_line(sys.argv)` dispatches to the appropriate management command.

**Common commands:**
```bash
python manage.py runserver       # Start dev server
python manage.py migrate         # Apply database migrations
python manage.py makemigrations  # Generate migrations from model changes
python manage.py test            # Run tests
python manage.py createsuperuser # Create admin user
```

### `StockChat/wsgi.py` / `StockChat/asgi.py`

Entry points for production servers. `wsgi.py` exposes the WSGI `application` object for synchronous servers (Gunicorn). `asgi.py` does the same for async servers (Daphne, Uvicorn).

---

## 4. Configuration

### `StockChat/settings.py`

#### Key Settings

- **`SECRET_KEY`** — Cryptographic secret read from `.env`. Used for signing sessions, CSRF tokens, etc.
- **`DEBUG`** — Parsed from env var. Shows detailed error pages when `True`. Must be `False` in production.
- **`ALLOWED_HOSTS`** — Comma-separated hostnames from env var. Prevents HTTP Host header attacks.

#### Installed Apps

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'Home',
    'portfolio',
    'communities',
    'market_data',
    'friends',
    'chat',
]
```

Each app is discovered by Django for models, migrations, admin registrations, template tags, and templates.

#### Middleware Pipeline

Middleware processes every request/response. Order matters:

1. `SecurityMiddleware` — HTTPS redirects, security headers
2. `SessionMiddleware` — Reads/writes session cookies
3. `CommonMiddleware` — URL normalization (trailing slashes)
4. `CsrfViewMiddleware` — CSRF token validation on POST
5. `AuthenticationMiddleware` — Sets `request.user`
6. `MessageMiddleware` — Flash messages
7. `XFrameOptionsMiddleware` — Clickjacking protection

#### Templates

```python
'DIRS': [BASE_DIR / 'templates'],  # Project-level (base.html lives here)
'APP_DIRS': True,                   # Also searches <app>/templates/
```

Context processors automatically inject `request`, `user`, `messages` into every template.

#### Auth Settings

```python
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'
```

`LOGIN_URL` is where `@login_required` redirects unauthenticated users.

---

## 5. URL Routing

### Root URL Config (`StockChat/urls.py`)

```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('Home.urls')),
    path('portfolio/', include('portfolio.urls')),
    path('communities/', include('communities.urls')),
    path('market-data/', include('market_data.urls')),
    path('friends/', include('friends.urls')),
    path('chat/', include('chat.urls')),
]
```

Each app is mounted at its own URL prefix. `include()` delegates URL resolution to the app's own `urls.py`.

### Complete URL Map

| URL | App | View | Method | Auth |
|-----|-----|------|--------|------|
| `/` | Home | `home` | GET | No |
| `/about/` | Home | `about` | GET | No |
| `/contact/` | Home | `contact` | GET, POST | No |
| `/signup/` | Home | `signup_view` | GET, POST | No |
| `/login/` | Home | `login_view` | GET, POST | No |
| `/logout/` | Home | `logout_view` | POST | No |
| `/portfolio/` | portfolio | `portfolio_view` | GET, POST | Yes |
| `/portfolio/delete/<pk>/` | portfolio | `portfolio_delete` | POST | Yes |
| `/communities/` | communities | `post_list` | GET | Yes |
| `/communities/new/` | communities | `post_create` | GET, POST | Yes |
| `/communities/<pk>/` | communities | `post_detail` | GET | Yes |
| `/communities/<pk>/vote/` | communities | `post_vote` | POST | Yes |
| `/communities/<pk>/comment/` | communities | `post_comment` | POST | Yes |
| `/communities/<pk>/delete/` | communities | `post_delete` | POST | Yes |
| `/friends/` | friends | `friends_list` | GET | Yes |
| `/friends/search/` | friends | `search_users` | GET | Yes |
| `/friends/request/<id>/` | friends | `send_request` | POST | Yes |
| `/friends/accept/<pk>/` | friends | `accept_request` | POST | Yes |
| `/friends/decline/<pk>/` | friends | `decline_request` | POST | Yes |
| `/friends/cancel/<pk>/` | friends | `cancel_request` | POST | Yes |
| `/friends/unfriend/<id>/` | friends | `unfriend` | POST | Yes |
| `/chat/` | chat | `inbox` | GET | Yes |
| `/chat/<user_id>/` | chat | `conversation` | GET | Yes |
| `/chat/<user_id>/send/` | chat | `send_message` | POST | Yes |
| `/chat/<user_id>/poll/` | chat | `poll_messages` | GET | Yes |
| `/chat/unread/` | chat | `unread_count` | GET | Yes |
| `/market-data/` | market_data | `market_data_view` | GET | Yes |

---

## 6. Home App — Core Pages & Auth

### Models (`Home/models.py`)

#### Contact

Stores contact form submissions.

| Field | Type | Notes |
|-------|------|-------|
| `name` | CharField(100) | |
| `email` | EmailField | Validates email format |
| `phone` | CharField(15) | |
| `content` | TextField | Unlimited-length message |
| `dob` | DateField | Optional (`blank=True, null=True`) |
| `created_at` | DateTimeField | `auto_now_add=True` |

### Forms (`Home/forms.py`)

**`ContactForm`** — A `ModelForm` generated from the Contact model. Overrides widgets to add Bootstrap classes. Custom `clean_*` methods validate minimum lengths for name (3), phone (10), and content (3).

### Views (`Home/views.py`)

- **`home`** / **`about`** — Simple template renders.
- **`contact`** — Standard Django form pattern: GET shows empty form, POST validates and saves, redirects on success (PRG pattern).
- **`signup_view`** — Uses Django's `UserCreationForm`. Creates user and immediately logs them in with `login(request, user)`.
- **`login_view`** — Uses `AuthenticationForm`. Honors `?next=` parameter with **open redirect protection** via `url_has_allowed_host_and_scheme()`.
- **`logout_view`** — `@require_POST` to prevent CSRF logout attacks via `<img src="/logout/">`.

---

## 7. Portfolio App — Holdings Tracker

### Model (`portfolio/models.py`)

#### Portfolio

| Field | Type | Notes |
|-------|------|-------|
| `user` | ForeignKey(User) | `CASCADE` delete, `related_name='portfolios'` |
| `ticker` | CharField(20) | Stock symbol (e.g., "AAPL") |
| `stock_name` | CharField(100) | Company name |
| `quantity` | PositiveIntegerField | Number of shares |
| `invested` | DecimalField(12,2) | Total invested amount. `DecimalField` avoids float rounding errors with money |
| `added_at` | DateTimeField | `auto_now_add=True` |

- **`UniqueConstraint(fields=['user', 'ticker'])`** — One entry per ticker per user.
- **`db_table = 'Home_portfolio'`** — Points to the original table from when this model lived in the Home app. Avoids data loss during the app migration.
- **`avg_price` property** — Computed: `invested / quantity`. Guards against `ZeroDivisionError`.

### Views (`portfolio/views.py`)

**`portfolio_view`** (GET + POST):

POST uses an **update-or-create pattern**:

```python
updated = Portfolio.objects.filter(user=request.user, ticker=ticker).update(
    quantity=F("quantity") + quantity,
    invested=F("invested") + invested,
)
if not updated:
    Portfolio.objects.create(...)
```

**`F()` expressions** generate SQL that operates on column values directly in the database, preventing race conditions when concurrent requests update the same row.

GET uses **`aggregate(Sum(...))`** to compute totals in a single SQL query rather than loading all rows into Python.

**`portfolio_delete`** — Uses `get_object_or_404(Portfolio, pk=pk, user=request.user)` to ensure users can only delete their own holdings.

---

## 8. Communities App — Reddit-Style Posts

### Models (`communities/models.py`)

#### Post

| Field | Type | Notes |
|-------|------|-------|
| `author` | ForeignKey(User) | |
| `title` | CharField(300) | |
| `body` | TextField | |
| `created_at` | DateTimeField | `auto_now_add=True` |
| `updated_at` | DateTimeField | `auto_now=True` |

- `score` property — Computes `upvotes - downvotes` from related Vote objects.
- `comment_count` property — Counts related Comment objects.
- Default ordering: `-created_at` (newest first).

#### Vote

| Field | Type | Notes |
|-------|------|-------|
| `user` | ForeignKey(User) | |
| `post` | ForeignKey(Post) | `related_name='votes'` |
| `value` | SmallIntegerField | `1` (upvote) or `-1` (downvote) |

- **`UniqueConstraint(fields=['user', 'post'])`** — One vote per user per post.

#### Comment

| Field | Type | Notes |
|-------|------|-------|
| `author` | ForeignKey(User) | |
| `post` | ForeignKey(Post) | `related_name='comments'` |
| `parent` | ForeignKey('self') | Nullable. Enables one level of reply threading. |
| `body` | TextField | |
| `created_at` | DateTimeField | |

### Views (`communities/views.py`)

- **`post_list`** — Annotates posts with `net_score` (via `Sum('votes__value')`) and `num_comments`. Supports sort by `new` or `top`. Fetches user's votes in a single query for highlighting.

- **`post_vote`** — Toggle logic:
  - First vote: creates Vote
  - Same vote again: deletes (un-vote)
  - Opposite vote: switches
  - Returns JSON for AJAX callers, or redirects for standard form submissions.

- **`post_comment`** — Accepts optional `parent` field for reply threading.

- **`post_delete`** — Only the post author can delete (`author=request.user`).

### Template Tags (`communities/templatetags/community_tags.py`)

**`get_vote` filter** — Looks up a post's vote value from the `user_votes` dictionary in templates:
```django
{% with uv=user_votes|get_vote:post.pk %}
```
Needed because Django templates can't do dictionary lookups with variable keys natively.

---

## 9. Friends App — Social Connections

### Model (`friends/models.py`)

#### Friendship

| Field | Type | Notes |
|-------|------|-------|
| `sender` | ForeignKey(User) | Who sent the request |
| `receiver` | ForeignKey(User) | Who received it |
| `status` | CharField(10) | `'pending'` or `'accepted'` |
| `created_at` | DateTimeField | |
| `updated_at` | DateTimeField | |

- **`UniqueConstraint(fields=['sender', 'receiver'])`** — Prevents duplicate requests.

### Views (`friends/views.py`)

**Helper: `_get_friends(user)`** — Queries both directions of the Friendship table (user could be sender or receiver) for accepted friendships. Returns a User queryset.

- **`friends_list`** — Three sections: incoming pending requests, outgoing pending requests, accepted friends.
- **`search_users`** — Searches by username (`icontains`). Builds a status lookup (`friends`/`sent`/`received`/`none`) for each result to show the appropriate button.
- **`send_request`** — Checks both directions for existing relationships before creating. Prevents self-friending.
- **`accept_request`** / **`decline_request`** — Only the receiver can act. Accept flips status to `accepted`; decline deletes the row.
- **`cancel_request`** — Only the sender can cancel their pending request.
- **`unfriend`** — Deletes the accepted Friendship in either direction.

### Template Tags (`friends/templatetags/friend_tags.py`)

**`get_status` filter** — Same pattern as communities: dict lookup by user ID for rendering the correct button in search results.

---

## 10. Chat App — Direct Messaging

### Model (`chat/models.py`)

#### Message

| Field | Type | Notes |
|-------|------|-------|
| `sender` | ForeignKey(User) | `related_name='sent_messages'` |
| `receiver` | ForeignKey(User) | `related_name='received_messages'` |
| `body` | TextField | |
| `created_at` | DateTimeField | `auto_now_add=True` |
| `is_read` | BooleanField | Default `False`. Set to `True` when receiver opens the conversation. |

### Views (`chat/views.py`)

**Helper: `_are_friends(user, other)`** — Checks if an accepted Friendship exists. All chat endpoints enforce this — only friends can message each other.

- **`inbox`** — Lists all friends with their latest message and unread count. Sorted by most recent message.

- **`conversation`** — Shows message history with a specific friend. Marks unread messages as read on open. Loads last 200 messages.

- **`send_message`** — AJAX endpoint (POST). Validates friendship and non-empty body. Returns JSON with the new message data.

- **`poll_messages`** — AJAX endpoint (GET). Returns new messages since a given `after` ID. The frontend polls this every 3 seconds. Marks received messages as read.

- **`unread_count`** — Returns total unread count as JSON. Can be used for sidebar badges.

### Frontend Chat Architecture

The conversation template uses vanilla JavaScript (no framework):

1. **Send** — `fetch()` POST to `/chat/<id>/send/` with CSRF token. Appends the message bubble to the DOM immediately.
2. **Poll** — `setInterval(poll, 3000)` calls `/chat/<id>/poll/?after=<lastMsgId>`. Appends any new messages from the other user.
3. **Scroll** — Auto-scrolls to bottom on new messages.
4. **Enter key** sends messages (no Shift+Enter for newlines in this simple version).

All message text is escaped via `textContent` assignment before inserting into the DOM, preventing XSS.

---

## 11. Market Data App — Placeholder

Currently a placeholder page. Will eventually integrate with a stock price API to show real-time quotes, charts, and market trends.

---

## 12. Templates & UI Architecture

### Base Template (`templates/base.html`)

Every page extends `base.html`, which provides:

```
┌─────────────────────────────────────────────┐
│ Navbar (sc-navbar)                           │
│   [Toggle] StockChat    Home About Contact   │
├──────┬──────────────────────────────────────┤
│      │                                       │
│  S   │  Main Content                         │
│  i   │  ┌─ pre_content block ──────────────┐│
│  d   │  │ (page headers)                    ││
│  e   │  ├──────────────────────────────────┤│
│  b   │  │ Flash messages                    ││
│  a   │  ├──────────────────────────────────┤│
│  r   │  │ content block                     ││
│      │  │ (main page content)               ││
│      │  └──────────────────────────────────┘│
├──────┴──────────────────────────────────────┤
│ Footer                                       │
└─────────────────────────────────────────────┘
```

### Sidebar

- Only shown for authenticated users.
- Grouped into **Invest** (Portfolio, Market Data) and **Social** (Communities, Friends, Chat) sections.
- Fully collapsible to `width: 0` via toggle button. State persisted in `localStorage`.
- On mobile (<768px): slides in as a fixed overlay with backdrop.
- Active state determined by `request.path` prefix matching.

### Design System

| CSS Variable | Value | Usage |
|-------------|-------|-------|
| `--sc-dark` | `#0a1628` | Navbar, sidebar, footer background |
| `--sc-mid` | `#132743` | Gradients, avatars |
| `--sc-accent` | `#2563eb` | Buttons, active states, links |
| `--sc-surface` | `#f8fafc` | Page background |
| `--sc-border` | `#e2e8f0` | Card borders |
| `--sc-text` | `#1e293b` | Primary text |
| `--sc-text-muted` | `#64748b` | Secondary text |

The UI uses Bootstrap Icons (not emojis) throughout for a professional financial aesthetic.

### Template Blocks

| Block | Purpose |
|-------|---------|
| `title` | Page `<title>` |
| `extra_head` | Per-page CSS |
| `pre_content` | Page headers (portfolio stats header, etc.) |
| `content` | Main page body |
| `extra_scripts` | Per-page JavaScript |

---

## 13. Migrations

### Migration Strategy for App Split

The Portfolio model was moved from the `Home` app to the `portfolio` app. This required a careful two-step migration using `SeparateDatabaseAndState`:

1. **`Home/0005_remove_portfolio_model.py`** — Removes Portfolio from Django's state only (no SQL). The database table stays as-is.
2. **`portfolio/0001_initial.py`** — Creates Portfolio in Django's state only (no SQL). Points to the existing `Home_portfolio` table via `db_table`.

This approach preserves all existing data while cleanly moving the model between apps.

### Migration Files by App

| App | Migrations | Key Operations |
|-----|-----------|----------------|
| Home | 0001-0005 | Contact table, Portfolio table (created then removed from state) |
| portfolio | 0001 | Portfolio model (state-only, reuses Home_portfolio table) |
| communities | 0001 | Post, Vote (with unique constraint), Comment (with self-FK) |
| friends | 0001 | Friendship (with unique constraint) |
| chat | 0001 | Message |

---

## 14. Request Lifecycle

Here's the journey of a POST to `/communities/3/vote/` (upvoting a post):

```
1. Browser sends POST with form data + CSRF token + session cookie

2. MIDDLEWARE PIPELINE (top to bottom):
   ├─ SecurityMiddleware       → security headers
   ├─ SessionMiddleware        → loads session from cookie
   ├─ CommonMiddleware         → URL normalization
   ├─ CsrfViewMiddleware      → validates CSRF token
   ├─ AuthenticationMiddleware → sets request.user from session
   ├─ MessageMiddleware        → enables flash messages
   └─ XFrameOptionsMiddleware  → X-Frame-Options header

3. URL RESOLUTION:
   ├─ StockChat/urls.py: path('communities/', include('communities.urls'))
   └─ communities/urls.py: path('<int:pk>/vote/', views.post_vote) → pk=3

4. DECORATORS:
   ├─ @login_required → user is authenticated? Yes → proceed
   └─ @require_POST → method is POST? Yes → proceed

5. VIEW: post_vote(request, pk=3)
   ├─ get_object_or_404(Post, pk=3) → loads the post
   ├─ value = int(request.POST['value']) → 1 (upvote)
   ├─ Vote.objects.get_or_create(user=request.user, post=post)
   │   └─ SQL: SELECT ... WHERE user_id=1 AND post_id=3
   │   └─ Not found → INSERT INTO communities_vote (user_id, post_id, value) VALUES (1, 3, 1)
   ├─ Recompute score: SELECT SUM(value) FROM communities_vote WHERE post_id=3
   ├─ Check X-Requested-With header → not AJAX
   └─ return redirect('post_detail', pk=3)

6. MIDDLEWARE PIPELINE (bottom to top):
   ├─ SessionMiddleware → writes session, sets cookie
   └─ SecurityMiddleware → adds headers

7. Browser follows HTTP 302 → GET /communities/3/

8. The GET request flows through the same pipeline, loading the post detail page
   with the updated vote count and the user's vote highlighted.
```

This illustrates the separation of concerns: middleware handles cross-cutting concerns, URL routing dispatches to the right app, decorators enforce access control, views contain business logic, the ORM handles database operations, and templates produce HTML.
