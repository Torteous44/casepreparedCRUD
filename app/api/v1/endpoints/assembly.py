from fastapi import APIRouter, Depends, HTTPException
import httpx
from app.core.config import settings
from app.models.user import User
from app.auth.dependencies import get_current_user

router = APIRouter()

@router.get("/token", response_model=dict)
async def get_assembly_token(
    current_user: User = Depends(get_current_user)
):
    """
    Get a temporary AssemblyAI token for real-time transcription.
    Protected by user authentication.
    """
    if not settings.ASSEMBLY_AI_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="AssemblyAI API key not configured"
        )

    # Define the URL for AssemblyAI's temporary token endpoint
    assembly_url = "https://api.assemblyai.com/v2/realtime/token"

    # Define the JSON payload with the expiration time in seconds (1 hour)
    payload = {"expires_in": 3600}

    headers = {
        "Authorization": settings.ASSEMBLY_AI_API_KEY,
        "Content-Type": "application/json"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(assembly_url, json=payload, headers=headers)

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code, 
                detail=f"AssemblyAI error: {response.text}"
            )

        # Parse the response JSON to extract the temporary token
        token_data = response.json()
        temporary_token = token_data.get("token")
        
        if not temporary_token:
            raise HTTPException(
                status_code=500, 
                detail="Failed to retrieve temporary token from AssemblyAI"
            )

        return {"token": temporary_token}
        
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error connecting to AssemblyAI: {str(e)}"
        ) 