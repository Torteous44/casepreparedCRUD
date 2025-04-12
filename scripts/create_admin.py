#!/usr/bin/env python
import sys
import os
from sqlalchemy.orm import Session

# Add the parent directory to the sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.session import get_db
from app.services import user as user_service
from app.schemas.user import UserCreate
from app.models.user import User
from app.core.config import settings

def create_admin_user(db: Session) -> User:
    """
    Create an admin user or promote an existing user to admin
    """
    # Check if admin email is provided in environment variables
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_name = os.getenv("ADMIN_NAME", "Administrator")
    admin_password = settings.ADMIN_PASSWORD
    
    if not admin_email:
        print("Error: ADMIN_EMAIL environment variable not set")
        sys.exit(1)
    
    if not admin_password:
        print("Error: ADMIN_PASSWORD environment variable not set")
        sys.exit(1)
    
    # Check if the user already exists
    user = user_service.get_user_by_email(db, email=admin_email)
    
    if user:
        print(f"User {admin_email} already exists - promoting to admin")
        # Set is_admin to True
        user.is_admin = True
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        print(f"Creating new admin user: {admin_email}")
        # Create a new user with admin privileges
        user_in = UserCreate(
            email=admin_email,
            full_name=admin_name,
            password=admin_password
        )
        user = user_service.create_user(db, user_in=user_in)
        
        # Set is_admin to True - have to do this separately due to the schema
        user.is_admin = True
        db.add(user)
        db.commit()
        db.refresh(user)
    
    print(f"Admin user {user.email} set up successfully")
    return user

if __name__ == "__main__":
    db = next(get_db())
    create_admin_user(db) 