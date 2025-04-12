from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.user import User
from app.schemas.token import TokenPayload

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")
http_bearer = HTTPBearer()

def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = db.query(User).filter(User.id == token_data.sub).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def get_admin_user(
    credentials: HTTPAuthorizationCredentials = Security(http_bearer),
    db: Session = Depends(get_db)
) -> User:
    """
    For admin access using a direct password from environment variables.
    If admin password matches, returns the first user or creates an admin user.
    """
    from app.models.user import User
    import uuid
    
    token = credentials.credentials
    
    # Check if the token matches the admin password
    admin_password = settings.ADMIN_PASSWORD
    if not admin_password or token != admin_password:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid admin credentials",
        )
    
    # Get the first user or create an admin user if none exists
    user = db.query(User).first()
    if not user:
        # If no users exist, create an admin user
        admin_user = User(
            id=uuid.uuid4(),
            email="admin@caseprepared.com",
            full_name="Admin User",
            password_hash="",  # No password hash as admin uses direct token
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        user = admin_user
    
    return user

def get_subscription_active(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> bool:
    """
    Verify that the user has an active subscription
    """
    from app.models.subscription import Subscription
    
    subscription = db.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.status.in_(["active", "trial"])
    ).first()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Active subscription required",
        )
    return True

def get_admin_with_subscription(
    admin_user: User = Depends(get_admin_user),
) -> bool:
    """
    For admin endpoints, bypass the subscription check
    """
    return True 