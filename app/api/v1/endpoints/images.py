from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, get_subscription_active
from app.db.session import get_db
from app.models.user import User
from app.services import cloudflare as cloudflare_service

router = APIRouter()

@router.post("/upload-url", response_model=Dict[str, Any])
def get_upload_url(
    current_user: User = Depends(get_current_user),
    is_subscribed: bool = Depends(get_subscription_active),
) -> Any:
    """
    Get a direct upload URL for Cloudflare Images (client-side upload)
    """
    upload_url_data = cloudflare_service.get_cloudflare_direct_upload_url()
    
    if "error" in upload_url_data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get upload URL: {upload_url_data['error']}",
        )
    
    return upload_url_data

@router.post("/upload", response_model=Dict[str, Any])
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    is_subscribed: bool = Depends(get_subscription_active),
    db: Session = Depends(get_db),
) -> Any:
    """
    Upload an image to Cloudflare Images (server-side upload)
    """
    try:
        content = await file.read()
        image_url = cloudflare_service.upload_image_to_cloudflare(
            image_file_bytes=content,
            file_name=file.filename,
            content_type=file.content_type or "image/jpeg"
        )
        
        if not image_url:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload image to Cloudflare",
            )
        
        return {"image_url": image_url}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading image: {str(e)}",
        ) 