# Kitaab API

A small REST API for tracking users and the books they own, built with **FastAPI**,
**SQLModel**, and header-based authentication.

## Features

* FastAPI with automatic OpenAPI docs at `/docs` and `/redoc`.
* Custom `x-api-key` header authentication, applied to every endpoint via a dependency.
* SQLModel/SQLAlchemy models with typed request and response schemas.
* Pagination on list endpoints.
* Test suite covering auth, validation, and persistence.

## Requirements

* Python 3.10+
* The packages in `requirements.txt`

## Setup

1. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate      # Windows
   source .venv/bin/activate   # macOS / Linux
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Create your `.env` and set an API key:

   ```bash
   cp .env.example .env
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

   Paste the output in as `X_API_KEY`. The app refuses to start without it, so a
   missing key fails loudly at boot instead of silently rejecting every request.

## Running

```bash
uvicorn main:app --reload
```

The API is at `http://127.0.0.1:8000`, with docs at `http://127.0.0.1:8000/docs`.

## Configuration

All settings come from the environment (and `.env` locally).

| Variable | Default | Notes |
| --- | --- | --- |
| `X_API_KEY` | *none* | **Required.** The value clients must send as `x-api-key`. |
| `DATABASE_URL` | `sqlite:///kitaab.db` | Any SQLAlchemy URL. |
| `SQL_ECHO` | `false` | Set to `true` to log every SQL statement. |
| `CORS_ORIGINS` | `http://localhost:3000,http://127.0.0.1:3000` | Comma-separated. |

## Authentication

Every endpoint except `/health` requires the key in a header:

```
x-api-key: <your key>
```

A missing key and a wrong key both return `401`. Comparison is constant-time.

## Endpoints

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/health` | Liveness probe. No auth. |
| `POST` | `/users/` | Register a user. `400` if the email is taken. |
| `GET` | `/users/` | List users. |
| `POST` | `/books/` | Create a book. `404` if `user_id` doesn't exist. |
| `GET` | `/books/` | List books. |

List endpoints accept `offset` (default `0`) and `limit` (default `20`, max `100`).

Emails are normalised to lowercase, so `Sam@x.com` and `sam@x.com` are the same account.

### Example

```bash
curl -X POST 'http://127.0.0.1:8000/users/' \
  -H 'Content-Type: application/json' \
  -H 'x-api-key: your-secret-token' \
  -d '{"name": "Salman", "email": "salman@example.com", "college": "KLS"}'
```

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

## Project layout

```
main.py            app instance, lifespan, router wiring
config.py          environment-backed settings
db.py              engine, session dependency, table creation
auth.py            x-api-key dependency
models/            SQLModel tables and request/response schemas
routes/            endpoint definitions
tests/             pytest suite
```

## Notes for production

* SQLite is the default for convenience. Point `DATABASE_URL` at Postgres for real
  deployments.
* Create tables with a migration tool (e.g. Alembic) rather than relying on
  `create_all()` at startup.
* Terminate TLS in front of the app, and keep `X_API_KEY` out of client-side code —
  a static shared key identifies the app, not the user. Add real user auth before
  this holds anything sensitive.
