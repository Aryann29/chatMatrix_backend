from fastapi import APIRouter, Depends, HTTPException, status
from datetime import timedelta
from typing import Annotated
from auth.models.token import Token
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from auth.services.auth_service import authenticate_user, create_access_token,get_current_user
from core.database import get_db
from user.models.user import User as DBUser
auth_router = APIRouter(
    prefix='/auth',
    tags=['Auth'],
)


@auth_router.post('/token')
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
) -> Token:
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=1440)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    return Token(access_token=access_token, token_type="bearer")


@auth_router.get("/validate")
async def validate_token_endpoint(
    current_user: DBUser = Depends(get_current_user) # Use the get_current_user from auth_utils.py
):
    """
    Validates the current user's token and returns basic user information.
    This endpoint is called by the frontend after receiving a token to confirm its validity.
    """
    # If get_current_user does not raise an HTTPException, the token is valid.
    # Return basic user info that the frontend might need.
    return {
        "message": "Token is valid",
        "user_email": current_user.email,
        "user_username": current_user.username,
        "user_id": current_user.id
    }
