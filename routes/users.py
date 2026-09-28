from db import get_session
from fastapi import APIRouter, Depends, HTTPException
from users import User, UserCreate, UserRead
from sqlmodel import Session,select


from auth import verify_api_key


router = APIRouter('/users', tags=['Users'])

router.post('/', response_model=UserRead, dependencies=[Depends(verify_api_key)])
def register_user(user: UserCreate, session: Session = Depends(get_session)):
    # Check if the email already exists
    existing_user = session.exec(select(User).where(User.email == user.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = User.from_orm(user)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user