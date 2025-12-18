# FastAPI with Cassandra Database

This project demonstrates how to integrate Apache Cassandra with FastAPI.

## Installation & Running the Application

1. All you need to do is this command:
```bash
./start
```

The API will be available at: http://127.0.0.1:8000

## API Documentation

Once running, visit:
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## Authentication

1. Copy `.env.example` to `.env` and set `SECRET_KEY` to a secure random value.
2. Endpoints:
	- `POST /auth/register` — register a new user (body: `username`, `email`, `password`).
	- `POST /auth/login` — obtain an access token using form data (`username`, `password`).
	- `GET /auth/me` — get current user, requires `Authorization: Bearer <token>` header.

The project uses JWT for tokens and `passlib` for password hashing. See `.env.example` for settings.