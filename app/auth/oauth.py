import json
from typing import Optional
import requests

from app.core.config import settings

def verify_google_token(token: str) -> Optional[dict]:
    """
    Verify the Google OAuth token and return user info if valid
    """
    try:
        # Verify token with Google
        response = requests.get(
            f"https://oauth2.googleapis.com/tokeninfo?id_token={token}"
        )
        
        if response.status_code == 200:
            user_info = response.json()
            # Verify that the audience matches our client ID
            if user_info.get("aud") == settings.GOOGLE_CLIENT_ID:
                return user_info
        return None
    except Exception:
        return None 