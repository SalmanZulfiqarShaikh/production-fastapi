from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select

from auth import verify_api_key
from db import get_session
from models import Book, BookCreate, BookRead, User

router = APIRouter(
    prefix="/books",
    tags=["Books"],
    dependencies=[Depends(verify_api_key)],
)

@router.post("/", response_model=BookRead)
def create_book(book: BookCreate, session: Session = Depends(get_session)):
    if session.get(User, book.user_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {book.user_id} does not exist",
        )

    new_book = Book(**book.model_dump())
    session.add(new_book)
    session.commit()
    session.refresh(new_book)
    return new_book


@router.get("/", response_model=list[BookRead])
def get_books(
    session: Session = Depends(get_session),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
):
    return session.exec(select(Book).offset(offset).limit(limit)).all()
