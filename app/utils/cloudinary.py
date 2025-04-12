import cloudinary
import cloudinary.uploader
import cloudinary.api
from fastapi import UploadFile
import uuid
from app.core.config import settings

# Initialize Cloudinary
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True
)

async def upload_image(file: UploadFile) -> dict:
    """
    Upload an image to Cloudinary
    
    Args:
        file: The file to upload
        
    Returns:
        dict: The upload response containing the image URL and other metadata
    """
    # Generate a unique public_id to avoid name conflicts
    public_id = f"case_prepared/{uuid.uuid4()}"
    
    # Read file content
    contents = await file.read()
    
    # Upload to cloudinary
    result = cloudinary.uploader.upload(
        contents,
        public_id=public_id,
        folder="case_prepared",
        overwrite=True,
        resource_type="image"
    )
    
    return result
    
def get_image_url(public_id: str) -> str:
    """
    Get the URL for an image from Cloudinary
    
    Args:
        public_id: The public ID of the image
        
    Returns:
        str: The image URL
    """
    return cloudinary.CloudinaryImage(public_id).build_url() 