from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, get_admin_user
from app.db.session import get_db
from app.models.user import User
from app.services import image as image_service

router = APIRouter()

@router.post("/upload-url", response_model=Dict[str, Any])
def get_image_upload_url(
    *,
    admin_user: User = Depends(get_admin_user),  # Only admins can get upload URLs
) -> Any:
    """
    Get a direct upload URL for Cloudflare Images (admin only)
    """
    try:
        upload_data = image_service.get_direct_upload_url()
        return {
            "success": True,
            "result": upload_data
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate upload URL: {str(e)}"
        ) 