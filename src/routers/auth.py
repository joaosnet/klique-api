from fastapi import APIRouter, Form
from fastapi import Depends, HTTPException, status

from ..services.mongodb import get_users_collection
from .depends import (
    Token,
    User,
    get_current_active_user,
    create_access_token,
    authenticate_user,
    get_password_hash,
)
from datetime import timedelta
from typing import Annotated

from fastapi.security import OAuth2PasswordRequestForm
from ..config import ACCESS_TOKEN_EXPIRE_MINUTES
router = APIRouter()


@router.post("/register")
async def register_user(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...)
):
    users_collection = get_users_collection()
    if username in users_collection:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    
    hashed_password = get_password_hash(password)
    new_user = {
        "username": username,
        "hashed_password": hashed_password,
        "email": email,
        "full_name": "",
        "disabled": False,
    }
    users_collection[username] = new_user
    
    return {"message": "User registered successfully"}

@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = authenticate_user(get_users_collection(), form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@router.get("/users/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user


@router.get("/users/me/items/")
async def read_own_items(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return [{"item_id": "Foo", "owner": current_user.username}]