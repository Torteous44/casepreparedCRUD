from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.schemas.image import ImageUploadResponse
from app.utils.cloudinary import upload_image

router = APIRouter()

@router.post("/upload", response_model=ImageUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_image_endpoint(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload an image to Cloudinary
    """
    # Check file type
    content_type = file.content_type
    if not content_type or not content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )
        
    try:
        # Upload image to Cloudinary
        result = await upload_image(file)
        
        # Return the image URL and other details
        return ImageUploadResponse(
            url=result.get("url", ""),
            public_id=result.get("public_id", ""),
            secure_url=result.get("secure_url", ""),
            format=result.get("format", ""),
            width=result.get("width", 0),
            height=result.get("height", 0),
            resource_type=result.get("resource_type", ""),
            created_at=result.get("created_at", ""),
            bytes=result.get("bytes", 0),
            original_filename=file.filename
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image upload failed: {str(e)}"
        ) 