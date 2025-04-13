from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel
import logging
import traceback
import os
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import secrets
from datetime import datetime, timedelta
import requests
import time

from app.auth.dependencies import get_current_user
from app.models.user import User
from app.db.session import get_db
from app.services.credential import generate_session_token_for_question
from app.models.interview import Interview
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Twilio credentials from environment variables
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/turn-credentials")
async def get_turn_credentials(current_user: User = Depends(get_current_user)):
    """
    Get TURN server credentials from Twilio for WebRTC connections.
    Returns a token that can be used to connect to Twilio's TURN servers.
    """
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
        logger.error("Twilio credentials not configured")
        raise HTTPException(
            status_code=500,
            detail="Twilio credentials not configured"
        )
        
    try:
        logger.info(f"Generating TURN credentials for user ID: {current_user.id}")
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        token = client.tokens.create()
        
        logger.info("TURN credentials generated successfully")
        return {
            "iceServers": token.ice_servers,
            "ttl": token.ttl
        }
        
    except TwilioRestException as e:
        error_detail = f"Failed to get TURN credentials: {str(e)}"
        logger.error(error_detail)
        raise HTTPException(
            status_code=500,
            detail=error_detail
        )
    except Exception as e:
        error_detail = f"Unexpected error: {str(e)}"
        logger.error(f"{error_detail}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=error_detail
        )

class EphemeralKeyRequest(BaseModel):
    interview_id: UUID
    question_number: int

@router.post("/openai-ephemeral-key")
def get_openai_ephemeral_key(
    request: EphemeralKeyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate an ephemeral key/session token for OpenAI Realtime API
    
    Args:
        request: Request body containing interview_id and question_number
        
    Returns:
        Dictionary containing session token information
    """
    try:
        logger.info(f"Processing ephemeral key request for user ID: {current_user.id}, interview: {request.interview_id}, question: {request.question_number}")
        
        # Verify that the interview exists
        interview = db.query(Interview).filter(Interview.id == request.interview_id).first()
        if not interview:
            logger.warning(f"Interview not found: {request.interview_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview not found"
            )
        
        # Check user authorization (the user must be the owner of the interview)
        if interview.user_id != current_user.id:
            logger.warning(f"User {current_user.id} not authorized to access interview {request.interview_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this interview"
            )
        
        # Validate question number
        if request.question_number < 1 or request.question_number > 4:
            logger.warning(f"Invalid question number: {request.question_number}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Question number must be between 1 and 4"
            )
        
        # Generate the session token - this now handles its own errors internally
        logger.info(f"Calling generate_session_token_for_question")
        try:
            session_token = generate_session_token_for_question(
                db=db,
                interview_id=request.interview_id,
                user_id=current_user.id,
                question_number=request.question_number
            )
            logger.info(f"OpenAI ephemeral key generated successfully")
            return session_token
        except Exception as e:
            logger.error(f"Error in session token generation: {str(e)}", exc_info=True)
            # Use a simplified fallback token if the normal generation fails
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if not openai_api_key:
                logger.error("OpenAI API key not found in environment variables")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="OpenAI API key not configured"
                )
            
            # Try to generate an ephemeral key directly from the endpoint
            try:
                url = "https://api.openai.com/v1/realtime/sessions"
                headers = {
                    "Authorization": f"Bearer {openai_api_key}",
                    "Content-Type": "application/json"
                }
                
                instructions = f"You are an assistant for interview question {request.question_number}. Help the candidate with their case interview."
                ttl = 3600
                
                # Prepare the payload
                payload = {
                    "model": "gpt-4o-mini-realtime-preview",
                    "modalities": ["audio", "text"],
                    "instructions": instructions,
                    "voice": "alloy",
                    "temperature": 0.8,
                    "input_audio_format": "pcm16",
                    "output_audio_format": "pcm16",
                    "max_response_output_tokens": "inf",
                    "turn_detection": {
                        "type": "server_vad",
                        "threshold": 0.5,
                        "prefix_padding_ms": 300,
                        "silence_duration_ms": 200
                    }
                }
                
                response = requests.post(url, headers=headers, json=payload)
                
                if response.status_code == 200:
                    ephemeral_key = response.json()
                    
                    # Return success with ephemeral key
                    return {
                        "id": f"fallback_sess_{request.interview_id}_{current_user.id}_{request.question_number}",
                        "interviewId": str(request.interview_id),
                        "userId": str(current_user.id),
                        "questionNumber": request.question_number,
                        "expiresAt": datetime.fromtimestamp(int(time.time()) + ttl).isoformat(),
                        "ttl": ttl,
                        "instructions": instructions,
                        "realtimeSession": ephemeral_key
                    }
            except Exception as e:
                logger.error(f"Error in fallback ephemeral key generation: {str(e)}", exc_info=True)
                # Continue to the basic fallback below
                
            # Generate a token and expiration time    
            token = secrets.token_hex(32)
            expiration = datetime.utcnow() + timedelta(hours=1)
            expiration_timestamp = int(expiration.timestamp())
                
            # Last resort fallback
            return {
                "id": f"fallback_sess_{request.interview_id}_{current_user.id}_{request.question_number}",
                "apiKey": openai_api_key,
                "instructions": f"You are an assistant for interview question {request.question_number}. Help the candidate with their case interview.",
                "interviewId": str(request.interview_id),
                "userId": str(current_user.id),
                "questionNumber": request.question_number,
                "expiresAt": expiration.isoformat(),
                "ttl": 3600,
                "client_secret": {
                    "value": token,
                    "expires_at": expiration_timestamp
                }
            }
            
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        error_detail = f"Failed to generate OpenAI ephemeral key: {str(e)}"
        logger.error(f"{error_detail}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail
        ) 