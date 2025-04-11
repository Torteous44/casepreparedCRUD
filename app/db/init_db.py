from sqlalchemy.orm import Session

from app.db.session import Base, engine
from app.models import User, Subscription, InterviewTemplate, Interview
from app.services import user as user_service
from app.schemas.user import UserCreate

def init_db(db: Session) -> None:
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create initial data if needed
    # For example, create an admin user
    admin = user_service.get_user_by_email(db, email="admin@example.com")
    if not admin:
        user_in = UserCreate(
            email="admin@example.com",
            password="changeme",
            full_name="Administrator",
        )
        user_service.create_user(db, user_in=user_in) 