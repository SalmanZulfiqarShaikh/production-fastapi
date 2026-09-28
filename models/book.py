from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
import models.user as user_model

class Book(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    owner: "user_model.User" = Relationship(back_populates="books")
    author: str = Field(index=True)
    price: float
    is_sold: bool = Field(default=False)

    #Foreign key to the User model
    user_id: int = Field(default=None, foreign_key="user.id")




class BookCreate(SQLModel):
    title: str
    author: str
    price: float
    user_id: int



class BookRead(SQLModel):
    id: int
    title: str
    author: str
    price: float
    is_sold: bool
    user_id: int


Book.model_rebuild()