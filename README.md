# Catering Business Management System

A full-stack Catering Business Management System built with **FastAPI + SQLite + SQLAlchemy + Bootstrap**.

## Features

- JWT authentication (register/login/logout)
- Roles: Admin and Customer
- Admin dashboard:
  - Manage menu items (CRUD)
  - View all orders and update status
  - View customers and analytics (orders, revenue)
- Customer flow:
  - Browse menu with search/filter
  - Add to cart
  - Event-based checkout (Wedding/Party/Corporate)
  - Order history and invoice endpoint
- Dockerized deployment support

## Project Structure

```text
.
├── main.py
├── models.py
├── schemas.py
├── database.py
├── auth_utils.py
├── deps.py
├── routers/
│   ├── auth.py
│   ├── menu.py
│   ├── orders.py
│   └── users.py
├── templates/
├── static/
├── requirements.txt
├── Dockerfile
└── README.md
```

## API Endpoints

- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/logout`
- `GET|POST|PUT|DELETE /menu`
- `POST|GET /orders`
- `PUT /orders/{order_id}`
- `GET /orders/{order_id}/invoice`
- `GET /users`
- `GET /users/me`
- `GET /users/analytics/summary`

## Run Locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Open: `http://127.0.0.1:8000`

## Create an Admin User

By default, registrations create `customer` users. To promote one user to admin in SQLite:

```bash
python - <<'PY'
import sqlite3
conn = sqlite3.connect('catering.db')
conn.execute("UPDATE users SET role='admin' WHERE email='admin@example.com'")
conn.commit()
conn.close()
print('Updated role to admin')
PY
```


## Password Length Note (bcrypt)

This project safely truncates passwords to **72 bytes** before bcrypt hashing/verification (bcrypt backend limit), preventing the common runtime error on very long passwords.

## Docker Deployment

Build and run:

```bash
docker build -t catering-system .
docker run -p 8000:8000 catering-system
```

Then visit: `http://localhost:8000`

## Portfolio Notes

- Clean modular router structure
- ORM-driven schema and relationships
- Ready to extend with payments, email notifications, and admin reporting
