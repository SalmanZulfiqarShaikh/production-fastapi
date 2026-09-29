import os
import tempfile
from pathlib import Path

import pytest

# config.py reads the environment at import time (and refuses to start without
# an API key), so the environment has to be set before any project module loads.
os.environ.setdefault("X_API_KEY", "test-key")
os.environ["DATABASE_URL"] = f"sqlite:///{Path(tempfile.mkdtemp()) / 'test.db'}"
os.environ["SQL_ECHO"] = "false"

from fastapi.testclient import TestClient  # noqa: E402
from sqlmodel import SQLModel  # noqa: E402

import models  # noqa: E402,F401  (registers the tables on SQLModel.metadata)
from db import engine  # noqa: E402
from main import app  # noqa: E402

API_KEY = os.environ["X_API_KEY"]


@pytest.fixture
def client():
    """Fresh schema per test so ordering never matters."""
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def auth():
    return {"x-api-key": API_KEY}


@pytest.fixture
def user(client, auth):
    """A registered user, for tests that need an existing owner."""
    response = client.post(
        "/users/",
        json={"name": "Salman", "email": "salman@example.com", "college": "KLS"},
        headers=auth,
    )
    assert response.status_code == 200
    return response.json()
