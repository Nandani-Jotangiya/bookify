# 📚 Bookify - Library Book Rental Management System

## Overview

Bookify is a Library Book Rental Management System that allows users to browse, rent, and manage books while providing administrators with tools to manage inventory, rentals, payments, and user requests.

The system is built using FastAPI, PostgreSQL, SQLAlchemy, HTML, CSS, JavaScript, and Docker.

---

## Features

### User Module
- User Registration and Login
- Browse Available Books
- View Book Details
- Submit Rental Requests
- Online Payment for Security Deposit
- View Rental History
- Chat with Admin
- Receive Notifications

### Admin Module
- Dashboard Management
- Book Management (CRUD)
- Category Management
- Rental Request Approval/Rejection
- Payment Tracking
- User Management
- Rental History Monitoring
- Notification Management

---

## Technology Stack

### ⚙️ Backend
- FastAPI
- SQLAlchemy

### 🗄️ Database
- PostgreSQL

### Frontend
- HTML
- CSS
- JavaScript
- Jinja2 Templates

### DevOps
- Docker
- Docker Compose
- Git & GitHub

---

## Project Structure

```text
bookify/
│
├── admin/
├── auth/
├── user/
├── routes/
│   ├── admin.py
│   ├── auth.py
│   ├── books.py
│   ├── category.py
│   ├── payment.py
│   └── rental.py
│
├── app/
│   ├── main.py
│   ├── database.py
│   └── models.py
│
├── static/
│   ├── style.css
│   └── script.js
│
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
└── .gitignore
```

---

## ⚡ Installation

### 1️⃣ Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/bookify.git
cd bookify
```

### 2️⃣ Create Virtual Environment

```bash
python3 -m venv .venv
```

### Activate Environment

**Linux / Mac**

```bash
source .venv/bin/activate
```

**Windows**

```bash
.venv\Scripts\activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🐘 PostgreSQL Setup

Create a PostgreSQL database:

```sql
CREATE DATABASE bookify_db;
```

Update database configuration in:

```text
app/database.py
```

Example:

```python
DATABASE_URL = "postgresql://postgres:password@localhost/bookify_db"
```

---

## Run Application Locally

```bash
uvicorn app.main:app --reload
```

### 🌐 Application URL

```text
http://127.0.0.1:8000
```

### 📄 Swagger Documentation

```text
http://127.0.0.1:8000/docs
```

---

## 🐳 Docker Setup

### Build Docker Image

```bash
docker build -t bookify-app .
```

### Run Docker Container

```bash
docker run -p 8000:8000 bookify-app
```

---

## 🐳 Docker Compose Setup

### Start Application and Database

```bash
docker compose up --build
```

### Run in Background

```bash
docker compose up -d
```

### Stop Services

```bash
docker compose down
```

### Remove Containers and Volumes

```bash
docker compose down -v
```

---

## Git Workflow

### Create Development Branch

```bash
git checkout -b develop
```

### Commit Changes

```bash
git add .
git commit -m "Your commit message"
```

### Push Changes

```bash
git push origin develop
```

---

## Future Enhancements

- JWT Authentication
- Role-Based Access Control
- Email Notifications
- PDF Receipt Generation
- Recommendation System
- Advanced Search & Filters
- Payment Gateway Integration
- Dockerized Production Deployment

---
