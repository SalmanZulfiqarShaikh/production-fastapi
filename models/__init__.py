"""Importing both modules here guarantees every table is registered on
SQLModel.metadata before create_all() runs, and that relationship targets
resolve regardless of which module gets imported first."""

from models.book import Book, BookCreate, BookRead
from models.user import User, UserCreate, UserRead

__all__ = [
    "Book",
    "BookCreate",
    "BookRead",
    "User",
    "UserCreate",
    "UserRead",
]
