from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserCreateOAuth, UserUpdate
from app.auth.password import get_password_hash, verify_password

def get_user_by_id(db: Session, user_id: UUID) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, user_in: UserCreate) -> User:
    db_user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        password_hash=get_password_hash(user_in.password),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_oauth_user(db: Session, user_in: UserCreateOAuth) -> User:
    db_user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        google_oauth_id=user_in.google_oauth_id,
        password_hash="", # OAuth users don't have a password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, db_user: User, user_in: UserUpdate) -> User:
    update_data = user_in.dict(exclude_unset=True)
    if update_data.get("password"):
        update_data["password_hash"] = get_password_hash(update_data.pop("password"))
    
    for field, value in update_data.items():
        setattr(db_user, field, value)
        
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(db, email=email)
    if not user or not user.password_hash:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user

def delete_user(db: Session, user_id: UUID) -> bool:
    user = get_user_by_id(db, user_id)
    if user:
        db.delete(user)
        db.commit()
        return True
    return False 