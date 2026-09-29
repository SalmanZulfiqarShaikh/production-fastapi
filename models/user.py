from typing import TYPE_CHECKING, Annotated, Optional

from pydantic import AfterValidator, EmailStr
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from models.book import Book


def _lowercase(value: str) -> str:
    return value.lower()

Email = Annotated[EmailStr, AfterValidator(_lowercase)]


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, min_length=1, max_length=100)
    email: Email = Field(unique=True, index=True)
    college: str = Field(min_length=1, max_length=200)
    books: list["Book"] = Relationship(back_populates="owner")


class UserCreate(SQLModel):
    name: str = Field(min_length=1, max_length=100)
    email: Email
    college: str = Field(min_length=1, max_length=200)


class UserRead(SQLModel):
    id: int
    name: str
    email: Email
    college: str
