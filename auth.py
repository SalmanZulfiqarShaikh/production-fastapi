import secrets

from fastapi import Header, HTTPException, status

from config import settings


def verify_api_key(x_api_key: str | None = Header(default=None, alias="x-api-key")) -> str:
    """Reject the request unless the x-api-key header matches the configured key."""
    # The header is declared optional so a missing key returns the same 401 as a
    # wrong one. Marking it required would make FastAPI answer 422 instead, which
    # tells the caller their request shape is wrong rather than unauthenticated.
    #
    # compare_digest instead of != so the comparison takes the same time
    # regardless of how many leading characters match. Encoded to bytes because
    # compare_digest rejects non-ASCII str input, which a client could send.
    if x_api_key is None or not secrets.compare_digest(
        x_api_key.encode("utf-8"), settings.api_key.encode("utf-8")
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
    return x_api_key
