import logging
import sys

from app.db.session import SessionLocal
from app.services import user as user_service
from app.schemas.user import UserCreate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_superuser(email: str, password: str, full_name: str) -> None:
    db = SessionLocal()
    try:
        user = user_service.get_user_by_email(db, email=email)
        if user:
            logger.info(f"User with email {email} already exists")
            return
        
        user_in = UserCreate(
            email=email,
            password=password,
            full_name=full_name,
        )
        user = user_service.create_user(db, user_in=user_in)
        logger.info(f"Superuser {email} created successfully")
    except Exception as e:
        logger.error(f"Error creating superuser: {e}")
    finally:
        db.close()

def main() -> None:
    logger.info("Creating superuser")
    if len(sys.argv) < 4:
        logger.error("Usage: python -m scripts.create_superuser <email> <password> <full_name>")
        sys.exit(1)
    
    email = sys.argv[1]
    password = sys.argv[2]
    full_name = sys.argv[3]
    
    create_superuser(email=email, password=password, full_name=full_name)
    logger.info("Superuser created")

if __name__ == "__main__":
    main() 