"""Each test here pins down one of the bugs found in review."""


def test_openapi_schema_builds(client):
    """Guards the APIRouter(prefix=...) and dependencies=[Depends(...)] fixes.

    Both were TypeErrors raised while the routers were being constructed, so a
    schema that renders at all proves the routers assembled.
    """
    schema = client.get("/openapi.json").json()
    assert "/users/" in schema["paths"]
    assert "/books/" in schema["paths"]


def test_health_needs_no_key(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_missing_key_is_401(client):
    # Not 422: a missing credential is an auth failure, not a bad request body.
    assert client.get("/users/").status_code == 401


def test_wrong_key_is_401(client):
    response = client.get("/users/", headers={"x-api-key": "wrong"})
    assert response.status_code == 401


def test_key_is_required_on_reads_too(client, auth):
    """GET /books/ used to be open while POST /books/ was protected."""
    assert client.get("/books/").status_code == 401
    assert client.get("/books/", headers=auth).status_code == 200


def test_register_user(client, auth):
    response = client.post(
        "/users/",
        json={"name": "Salman", "email": "Salman@Example.com", "college": "KLS"},
        headers=auth,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "salman@example.com", "email should be normalised"


def test_duplicate_email_is_400_not_500(client, auth, user):
    response = client.post(
        "/users/",
        json={"name": "Other", "email": "salman@example.com", "college": "KLS"},
        headers=auth,
    )
    assert response.status_code == 400


def test_duplicate_email_is_case_insensitive(client, auth, user):
    response = client.post(
        "/users/",
        json={"name": "Other", "email": "SALMAN@EXAMPLE.COM", "college": "KLS"},
        headers=auth,
    )
    assert response.status_code == 400


def test_rejects_malformed_email(client, auth):
    response = client.post(
        "/users/",
        json={"name": "X", "email": "not-an-email", "college": "KLS"},
        headers=auth,
    )
    assert response.status_code == 422


def test_rejects_blank_name(client, auth):
    response = client.post(
        "/users/",
        json={"name": "", "email": "blank@example.com", "college": "KLS"},
        headers=auth,
    )
    assert response.status_code == 422


def test_create_book(client, auth, user):
    response = client.post(
        "/books/",
        json={"title": "Dune", "author": "Herbert", "price": 9.99, "user_id": user["id"]},
        headers=auth,
    )
    assert response.status_code == 200
    assert response.json()["is_sold"] is False


def test_rejects_negative_price(client, auth, user):
    response = client.post(
        "/books/",
        json={"title": "Dune", "author": "Herbert", "price": -5, "user_id": user["id"]},
        headers=auth,
    )
    assert response.status_code == 422


def test_book_for_unknown_user_is_404(client, auth):
    response = client.post(
        "/books/",
        json={"title": "Dune", "author": "Herbert", "price": 5, "user_id": 9999},
        headers=auth,
    )
    assert response.status_code == 404


def test_relationship_resolves_both_ways(client, auth, user):
    """The original 'book_model.Book' string broke SQLAlchemy mapper config."""
    from sqlmodel import Session, select

    from db import engine
    from models import Book, User

    client.post(
        "/books/",
        json={"title": "Dune", "author": "Herbert", "price": 9.99, "user_id": user["id"]},
        headers=auth,
    )

    with Session(engine) as session:
        owner = session.get(User, user["id"])
        assert [book.title for book in owner.books] == ["Dune"]
        book = session.exec(select(Book)).one()
        assert book.owner.email == "salman@example.com"


def test_pagination(client, auth):
    for index in range(5):
        client.post(
            "/users/",
            json={
                "name": f"User {index}",
                "email": f"user{index}@example.com",
                "college": "KLS",
            },
            headers=auth,
        )

    page = client.get("/users/?offset=1&limit=2", headers=auth).json()
    assert [user["name"] for user in page] == ["User 1", "User 2"]

    assert client.get("/users/?limit=0", headers=auth).status_code == 422
    assert client.get("/users/?limit=500", headers=auth).status_code == 422
