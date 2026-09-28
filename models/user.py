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

# avoid circular import issues by using string annotations for the relationship fields. This allows SQLModel to resolve the relationships correctly without needing to import the related models directly at the top of the file.

User.model_rebuild()  