"""Application settings, loaded from the environment (and .env for local dev)."""

import os

from dotenv import load_dotenv

# Must run before we read any os.getenv below, otherwise a local .env is ignored.
load_dotenv()


def _as_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


class Settings:
    api_key: str = os.getenv("X_API_KEY", "")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///kitaab.db")
    sql_echo: bool = _as_bool(os.getenv("SQL_ECHO", "false"))
    # Comma-separated list. Defaults to local-only because "*" with credentials
    # is the classic way an API ends up wide open.
    cors_origins: list[str] = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
        ).split(",")
        if origin.strip()
    ]


settings = Settings()

if not settings.api_key:
    raise RuntimeError(
        "X_API_KEY is not set. Copy .env.example to .env and give it a value."
    )
