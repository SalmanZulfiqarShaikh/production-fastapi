from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
import models.user as user_model

class Book(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    owner: "user_model.User" = Relationship(back_populates="books")