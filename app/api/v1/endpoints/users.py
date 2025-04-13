from typing import Any, List, Dict

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import User as UserSchema, UserUpdate
from app.services import user as user_service
from app.services import subscription as subscription_service

router = APIRouter()

@router.get("/me", response_model=Dict[str, Any])
def read_user_me(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get current user with subscription status
    """
    # Check if user has an active subscription
    has_active_subscription = subscription_service.has_active_subscription(
        db=db, 
        user_id=current_user.id
    )
    
    # Get user's subscription details if available
    subscription_details = None
    if has_active_subscription:
        subscription = subscription_service.get_subscription_by_user_id(
            db=db, 
            user_id=current_user.id
        )
        if subscription:
            subscription_details = {
                "id": str(subscription.id),
                "plan": subscription.plan,
                "status": subscription.status,
                "created_at": subscription.created_at,
                "stripe_subscription_id": subscription.stripe_subscription_id
            }
    
    # Convert the user model to dict and add subscription info
    user_data = {
        "id": str(current_user.id),
        "email": current_user.email,
        "is_admin": current_user.is_admin,
        "full_name": current_user.full_name,
        "created_at": current_user.created_at,
        "updated_at": current_user.updated_at,
        "subscription": {
            "is_active": has_active_subscription,
            "details": subscription_details
        }
    }
    
    return user_data

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