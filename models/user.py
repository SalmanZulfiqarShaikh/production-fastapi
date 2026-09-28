from sqlmodel import Field, SQLModel, Relationship
from typing import Optional
import models.book as book_model
#Database model for the User table


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    email: str = Field(unique=True)
    college: str


    #Relationship to the Book model
    books: list["book_model.Book"] = Relationship(back_populates="owner")
