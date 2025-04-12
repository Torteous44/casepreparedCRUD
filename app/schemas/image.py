from pydantic import BaseModel
from typing import Optional

class ImageUploadResponse(BaseModel):
    """
    Schema for the image upload response
    """
    url: str
    public_id: str
    secure_url: str
    format: str
    width: int
    height: int
    resource_type: str
    created_at: str
    bytes: int
    original_filename: Optional[str] = None 