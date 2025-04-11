from datetime import timedelta
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth.jwt import create_access_token
from app.auth.oauth import verify_google_token
from app.core.config import settings
from app.db.session import get_db
from app.models.user import User
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserCreateOAuth
from app.services import user as user_service

router = APIRouter()

@router.post("/register", response_model=Token)
def register(user_in: UserCreate, db: Session = Depends(get_db)) -> Any:
    """
    Register a new user with email and password
    """
    user = user_service.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system",
        )
    user = user_service.create_user(db, user_in=user_in)
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=str(user.id), expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
def login_access_token(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = user_service.authenticate_user(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=str(user.id), expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/google-login", response_model=Token)
def login_google(*, db: Session = Depends(get_db), token: str) -> Any:
    """
    Google OAuth login
    """
    user_info = verify_google_token(token)
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google token",
        )
    
    email = user_info.get("email")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not get email from Google token",
        )
    
    user = user_service.get_user_by_email(db, email=email)
    if not user:
        # Create a new user
        user_in = UserCreateOAuth(
            email=email,
            full_name=user_info.get("name", ""),
            google_oauth_id=user_info.get("sub"),
        )
        user = user_service.create_oauth_user(db, user_in=user_in)
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=str(user.id), expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"} 