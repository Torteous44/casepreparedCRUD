from typing import Any, List

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import User as UserSchema, UserUpdate
from app.services import user as user_service

router = APIRouter()

@router.get("/me", response_model=UserSchema)
def read_user_me(current_user: User = Depends(get_current_user)) -> Any:
    """
    Get current user
    """
    return current_user

@router.patch("/me", response_model=UserSchema)
def update_user_me(
    *,
    db: Session = Depends(get_db),
    user_in: UserUpdate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Update own user
    """
    user = user_service.update_user(db, db_user=current_user, user_in=user_in)
    return user

@router.get("/{user_id}", response_model=UserSchema)
def read_user_by_id(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """
    Get a specific user by id
    """
    user = user_service.get_user_by_id(db, user_id=user_id)
    if user == current_user:
        return user
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this ID does not exist in the system",
        )
    return user 