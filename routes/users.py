from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from auth import verify_api_key
from db import get_session
from models import User, UserCreate, UserRead

# Auth lives on the router so no endpoint can forget it. prefix/tags are
# keyword-only on APIRouter — passing them positionally raises TypeError.
router = APIRouter(
    prefix="/users",
    tags=["Users"],
    dependencies=[Depends(verify_api_key)],
)


@router.post("/", response_model=UserRead)
def register_user(user: UserCreate, session: Session = Depends(get_session)):
    existing_user = session.exec(select(User).where(User.email == user.email)).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    new_user = User(**user.model_dump())
    session.add(new_user)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        ) from None

    session.refresh(new_user)
    return new_user


@router.get("/", response_model=list[UserRead])
def get_users(
    session: Session = Depends(get_session),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
):
    return session.exec(select(User).offset(offset).limit(limit)).all()
