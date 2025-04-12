import json
import time
import requests
from typing import Optional
from uuid import uuid4

from app.core.config import settings


def get_direct_upload_url() -> dict:
    """
    Generate a one-time direct upload URL from Cloudflare Images.
    This URL can be used by the frontend to upload an image directly to Cloudflare.
    """
    if not settings.CLOUDFLARE_ACCOUNT_ID or not settings.CLOUDFLARE_API_TOKEN:
        raise ValueError("Cloudflare credentials not configured")
    
    # Generate a unique ID for the image
    image_id = str(uuid4())
    
    # Create a one-time upload URL that's valid for 30 minutes
    url = f"https://api.cloudflare.com/client/v4/accounts/{settings.CLOUDFLARE_ACCOUNT_ID}/images/v1/direct_upload"
    
    headers = {
        "Authorization": f"Bearer {settings.CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "id": image_id,
        "metadata": {
            "uploaded_by": "case_prepared_admin",
            "upload_timestamp": int(time.time())
        },
        "requireSignedURLs": False,
        "expiry": int(time.time()) + 1800  # 30 minutes from now
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        return response.json()["result"]
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to generate Cloudflare upload URL: {str(e)}")


def get_image_url(image_id: str) -> Optional[str]:
    """
    Get the delivery URL for an image stored in Cloudflare Images
    """
    if not settings.CLOUDFLARE_IMAGES_DELIVERY_URL:
        raise ValueError("Cloudflare Images delivery URL not configured")
    
    # Construct the delivery URL
    return f"{settings.CLOUDFLARE_IMAGES_DELIVERY_URL}/{image_id}"


def delete_image(image_id: str) -> bool:
    """
    Delete an image from Cloudflare Images
    """
    if not settings.CLOUDFLARE_ACCOUNT_ID or not settings.CLOUDFLARE_API_TOKEN:
        raise ValueError("Cloudflare credentials not configured")
    
    url = f"https://api.cloudflare.com/client/v4/accounts/{settings.CLOUDFLARE_ACCOUNT_ID}/images/v1/{image_id}"
    
    headers = {
        "Authorization": f"Bearer {settings.CLOUDFLARE_API_TOKEN}"
    }
    
    try:
        response = requests.delete(url, headers=headers)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException:
        return False 