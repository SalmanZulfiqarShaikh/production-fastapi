from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from models.user import User


class Book(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True, min_length=1, max_length=200)
    author: str = Field(index=True, min_length=1, max_length=100)
    price: float = Field(gt=0)
    is_sold: bool = Field(default=False)
    user_id: int = Field(foreign_key="user.id", index=True)
    owner: Optional["User"] = Relationship(back_populates="books")


class BookCreate(SQLModel):
    title: str = Field(min_length=1, max_length=200)
    author: str = Field(min_length=1, max_length=100)
    price: float = Field(gt=0)
    user_id: int


class BookRead(SQLModel):
    id: int
    title: str
    author: str
    price: float
    is_sold: bool
    user_id: int
