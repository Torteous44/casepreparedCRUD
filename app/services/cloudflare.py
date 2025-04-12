import requests
import json
from typing import Optional, Dict, Any
from app.core.config import settings

def upload_image_to_cloudflare(
    image_file_bytes: bytes,
    file_name: str,
    content_type: str = "image/jpeg"
) -> Optional[str]:
    """
    Upload an image to Cloudflare Images and return the URL
    
    Args:
        image_file_bytes: The binary content of the image file
        file_name: Name of the file
        content_type: MIME type of the image (default: image/jpeg)
        
    Returns:
        URL of the uploaded image or None if the upload failed
    """
    try:
        # Cloudflare Images API endpoint
        url = "https://api.cloudflare.com/client/v4/accounts/{account_id}/images/v1"
        
        # Replace with your Cloudflare account ID
        account_id = settings.CLOUDFLARE_ACCOUNT_ID
        
        # Prepare the headers
        headers = {
            "Authorization": f"Bearer {settings.CLOUDFLARE_API_KEY}"
        }
        
        # Prepare the files
        files = {
            'file': (file_name, image_file_bytes, content_type)
        }
        
        # Upload the image
        response = requests.post(
            url.format(account_id=account_id),
            headers=headers,
            files=files
        )
        
        # Parse the response
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('result'):
                # Return the image URL
                return data['result']['variants'][0]  # Usually the first variant is the original image
        
        print(f"Error uploading image to Cloudflare: {response.text}")
        return None
    
    except Exception as e:
        print(f"Exception uploading image to Cloudflare: {str(e)}")
        return None

def get_cloudflare_direct_upload_url() -> Dict[str, Any]:
    """
    Get a direct upload URL from Cloudflare Images for client-side uploads
    
    Returns:
        Dictionary containing the upload URL and any required fields/parameters
    """
    try:
        # Cloudflare Images API endpoint for direct uploads
        url = "https://api.cloudflare.com/client/v4/accounts/{account_id}/images/v1/direct_upload"
        
        # Replace with your Cloudflare account ID
        account_id = settings.CLOUDFLARE_ACCOUNT_ID
        
        # Prepare the headers
        headers = {
            "Authorization": f"Bearer {settings.CLOUDFLARE_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Request a direct upload URL
        response = requests.post(
            url.format(account_id=account_id),
            headers=headers
        )
        
        # Parse the response
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('result'):
                return {
                    "upload_url": data['result']['uploadURL'],
                    "id": data['result']['id'],
                    "expires": data['result']['expiry']
                }
        
        print(f"Error getting Cloudflare direct upload URL: {response.text}")
        return {"error": "Failed to get upload URL"}
    
    except Exception as e:
        print(f"Exception getting Cloudflare direct upload URL: {str(e)}")
        return {"error": str(e)} 