# Bookify - Library Book Rental Management System

## Overview

Bookify is a library book rental management system built with FastAPI, PostgreSQL, SQLAlchemy, Jinja2, and Docker. Users can browse books, submit rental requests, pay a security deposit, and track issued books. Admins manage inventory, approve requests, issue/return books, and view rental history.

---

## Features

### User Module
- Registration and login (JWT cookie auth)
- Browse available books and submit rental requests
- Pay security deposit (simulated) and view receipt
- View active issued books, requests, and rental history

### Admin Module
- Dashboard with library statistics
- Book and category management (CRUD)
- Approve/reject rental requests
- Issue and return books with late fine calculation
- Rental return history

---

## Technology Stack

- **Backend:** FastAPI, SQLAlchemy, Alembic
- **Database:** PostgreSQL 15
- **Frontend:** HTML, Bootstrap 5, Jinja2 templates
- **Auth:** JWT (httponly cookie) + CSRF protection on forms
- **DevOps:** Docker, Docker Compose

---

## Project Structure

```text
bookify/
├── app/
│   ├── main.py              # App entry, routers, middleware
│   ├── config.py            # Paths, SECRET_KEY
│   ├── database.py          # SQLAlchemy engine + session
│   ├── db_init.py           # Startup DB + Alembic sync
│   ├── core/
│   │   ├── csrf.py          # CSRF token helpers
│   │   ├── dependencies.py  # Auth guards
│   │   ├── security.py      # Password hashing
│   │   └── templates.py     # Jinja2 render helper
│   ├── models/
│   ├── routes/
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── payment.py
│   │   └── admin/
│   ├── services/fine.py
│   ├── static/css/
│   └── templates/
├── alembic/
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

---

## Installation

### Clone and set up Python environment

```bash
git clone https://github.com/YOUR_USERNAME/bookify.git
cd bookify
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Environment variables

| Variable | Description | Default (Docker) |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:postgres@db:5432/bookify_db` |
| `SECRET_KEY` | JWT + session signing key | Set in `docker-compose.yml` |

---

## Run with Docker (recommended)

```bash
docker compose up --build
```

| Service | URL |
|---|---|
| App | http://127.0.0.1:8000 |
| Login | http://127.0.0.1:8000/login |
| API docs | http://127.0.0.1:8000/docs |
| PostgreSQL (host) | `localhost:5433` |

Connect to the database from your machine:

```bash
docker exec -it bookify_db psql -U postgres -d bookify_db
```

---

## Run locally (without Docker)

1. Start PostgreSQL and create `bookify_db`
2. Set `DATABASE_URL` in a `.env` file:

```text
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/bookify_db
SECRET_KEY=your-secret-key-here
```

3. Run migrations / startup and start the server:

```bash
uvicorn app.main:app --reload
```

---

## Database migrations

Schema changes are managed with Alembic:

```bash
alembic upgrade head
```

On app startup, `db_init.py` ensures tables exist and applies pending migrations.

---

## Future Enhancements

- Real payment gateway integration
- Email notifications
- PDF receipt export
- Advanced search and filters
- User management UI for admins
