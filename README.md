# StockChat

A Django web application for stock market investors — discuss trade ideas, track portfolios, and chat with friends. Built with Django 5.2 and Bootstrap 5.

## Features

- **User Authentication** — Sign up, log in, log out with Django's built-in auth (session-based, CSRF-protected)
- **Portfolio Tracker** — Add/remove stock holdings, track shares, invested amount, and average cost
- **Communities** — Reddit-style post feed with upvote/downvote, comments with nested replies, sort by New/Top
- **Friends** — Send/accept/decline friend requests, search users, manage your connections
- **Chat** — Real-time direct messaging with friends (AJAX polling), unread indicators, message history
- **Sidebar Navigation** — Collapsible sidebar for authenticated users with section grouping
- **Responsive UI** — Mobile-friendly design using Bootstrap 5.3 and Inter font family

## Tech Stack

| Layer     | Technology              |
|-----------|-------------------------|
| Backend   | Python 3.13, Django 5.2 |
| Frontend  | Bootstrap 5.3, Bootstrap Icons, HTML5 |
| Database  | SQLite3 (dev), PostgreSQL (production) |

## Project Structure

```
StockChat/
├── manage.py
├── db.sqlite3
├── requirements.txt
├── StockChat/                 # Project config
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── templates/
│   └── base.html              # Base template (navbar, sidebar, footer)
├── Home/                      # Core: landing, about, contact, auth
│   ├── models.py              # Contact model
│   ├── views.py               # Home, about, contact, signup, login, logout
│   ├── forms.py               # ContactForm
│   ├── urls.py
│   └── templates/Home/
├── portfolio/                 # Portfolio tracker
│   ├── models.py              # Portfolio model
│   ├── views.py               # Add/view/delete holdings
│   ├── forms.py               # PortfolioAddForm
│   ├── urls.py
│   └── templates/portfolio/
├── communities/               # Reddit-style posts
│   ├── models.py              # Post, Vote, Comment
│   ├── views.py               # Feed, create, detail, vote, comment
│   ├── forms.py               # PostForm, CommentForm
│   ├── templatetags/          # community_tags (get_vote filter)
│   ├── urls.py
│   └── templates/communities/
├── friends/                   # Friend system
│   ├── models.py              # Friendship model
│   ├── views.py               # List, search, send/accept/decline/unfriend
│   ├── templatetags/          # friend_tags (get_status filter)
│   ├── urls.py
│   └── templates/friends/
└── chat/                      # Direct messaging
    ├── models.py              # Message model
    ├── views.py               # Inbox, conversation, send, poll
    ├── urls.py
    └── templates/chat/
```

## Routes

### Core (Home app)

| URL         | Method    | Description          |
|-------------|-----------|----------------------|
| `/`         | GET       | Landing page         |
| `/about/`   | GET       | About page           |
| `/contact/` | GET, POST | Contact form         |
| `/signup/`  | GET, POST | User registration    |
| `/login/`   | GET, POST | User login           |
| `/logout/`  | POST      | User logout          |

### Portfolio

| URL                          | Method | Description            |
|------------------------------|--------|------------------------|
| `/portfolio/`                | GET, POST | View/add holdings   |
| `/portfolio/delete/<id>/`    | POST   | Remove a holding       |

### Communities

| URL                             | Method | Description                |
|---------------------------------|--------|----------------------------|
| `/communities/`                 | GET    | Post feed (sort: new/top)  |
| `/communities/new/`             | GET, POST | Create a post           |
| `/communities/<id>/`            | GET    | Post detail + comments     |
| `/communities/<id>/vote/`       | POST   | Upvote/downvote            |
| `/communities/<id>/comment/`    | POST   | Add comment/reply          |
| `/communities/<id>/delete/`     | POST   | Delete own post            |

### Friends

| URL                          | Method | Description               |
|------------------------------|--------|---------------------------|
| `/friends/`                  | GET    | Friends list + requests    |
| `/friends/search/`           | GET    | Search users               |
| `/friends/request/<id>/`     | POST   | Send friend request        |
| `/friends/accept/<id>/`      | POST   | Accept request             |
| `/friends/decline/<id>/`     | POST   | Decline request            |
| `/friends/cancel/<id>/`      | POST   | Cancel sent request        |
| `/friends/unfriend/<id>/`    | POST   | Remove friend              |

### Chat

| URL                       | Method | Description                  |
|---------------------------|--------|------------------------------|
| `/chat/`                  | GET    | Inbox (conversation list)    |
| `/chat/<user_id>/`        | GET    | Chat window with user        |
| `/chat/<user_id>/send/`   | POST   | Send message (AJAX)          |
| `/chat/<user_id>/poll/`   | GET    | Poll new messages (AJAX)     |
| `/chat/unread/`           | GET    | Unread count (JSON)          |

## Database Models

### Contact (Home)
Stores contact form submissions.

### Portfolio (portfolio)
Tracks stock holdings per user — ticker, stock name, quantity, invested amount. Unique constraint on (user, ticker).

### Post, Vote, Comment (communities)
Reddit-style posts with upvote/downvote voting (one vote per user per post, toggle/switch). Comments support one level of nesting via parent FK.

### Friendship (friends)
Sender/receiver relationship with status (pending/accepted). Unique constraint prevents duplicate requests.

### Message (chat)
Direct messages between users with read/unread tracking. Only friends can exchange messages.

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

## Running Tests

```bash
python manage.py test
```
