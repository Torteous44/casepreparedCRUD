import secrets
import time
import hmac
import hashlib
from typing import Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from uuid import UUID

from app.models.interview import Interview
from app.models.interview_template import InterviewTemplate

# Simulated TURN server credentials
# In a real implementation, you would interact with a TURN/STUN server provider like Twilio or Cloudflare
def generate_turn_credentials(username: str, ttl: int = 86400) -> Dict[str, Any]:
    """
    Generate TURN server credentials
    
    Args:
        username: The username to generate credentials for
        ttl: Time to live in seconds (default: 24 hours)
        
    Returns:
        Dictionary containing TURN server credentials
    """
    # This is a placeholder for the actual implementation
    # You would typically use a provider's API to generate these credentials
    
    # Generate a timestamp for when the credentials will expire
    expiration = int(time.time()) + ttl
    
    # Generate a random password
    password = secrets.token_hex(16)
    
    # In a real system, you would sign these credentials with your TURN secret
    # Here we're just simulating it
    username_with_timestamp = f"{username}:{expiration}"
    
    return {
        "username": username_with_timestamp,
        "password": password,
        "ttl": ttl,
        "expiration": expiration,
        "urls": [
            "turn:turn.example.com:3478?transport=udp",
            "turn:turn.example.com:3478?transport=tcp",
            "turn:turn.example.com:443?transport=tcp",
            "stun:stun.example.com:3478"
        ]
    }

def generate_session_token(interview_id: str, user_id: str, ttl: int = 3600) -> Dict[str, Any]:
    """
    Generate a short-lived session token for the realtime interview session
    
    Args:
        interview_id: The ID of the interview
        user_id: The ID of the user
        ttl: Time to live in seconds (default: 1 hour)
        
    Returns:
        Dictionary containing session token information, structured like OpenAI's Realtime session object
    """
    # Generate a random token
    token = secrets.token_hex(32)
    
    # Calculate expiration time
    expiration = datetime.utcnow() + timedelta(seconds=ttl)
    expiration_timestamp = int(expiration.timestamp())
    
    return {
        "id": f"sess_{interview_id}_{user_id}",
        "object": "realtime.session",
        "model": "gpt-4o-realtime-preview",
        "modalities": ["audio", "text"],
        "instructions": f"You are an interview assistant for interview {interview_id}. Provide helpful responses to the candidate.",
        "voice": "alloy",
        "input_audio_format": "pcm16",
        "output_audio_format": "pcm16",
        "input_audio_transcription": {
            "model": "whisper-1"
        },
        "turn_detection": {
            "type": "server_vad",
            "threshold": 0.5,
            "prefix_padding_ms": 300,
            "silence_duration_ms": 200
        },
        "tools": [],
        "tool_choice": "none",
        "temperature": 0.8,
        "max_response_output_tokens": "inf",
        "client_secret": {
            "value": token,
            "expires_at": expiration_timestamp
        },
        "interview_id": interview_id,
        "user_id": user_id,
        "expires_at": expiration.isoformat(),
        "ttl": ttl
    }

def get_question_details(db: Session, interview_id: UUID, question_number: int) -> Dict[str, Any]:
    """
    Retrieve the details for a specific question in an interview
    
    Args:
        db: Database session
        interview_id: The ID of the interview
        question_number: The question number (1-4)
        
    Returns:
        Dictionary containing question details
    """
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise ValueError(f"Interview with ID {interview_id} not found")
    
    template = db.query(InterviewTemplate).filter(InterviewTemplate.id == interview.template_id).first()
    if not template:
        raise ValueError(f"Interview template with ID {interview.template_id} not found")
    
    question_key = f"question{question_number}"
    if question_key not in template.structure:
        raise ValueError(f"Question {question_number} not found in interview template")
    
    return {
        "question_number": question_number,
        "question_prompt": template.structure[question_key]["prompt"],
        "question_context": template.structure[question_key]["context"],
        "case_type": template.case_type,
        "lead_type": template.lead_type,
        "difficulty": template.difficulty,
        "company": template.company,
        "industry": template.industry,
        "case_prompt": template.prompt
    }

def build_interview_instructions(question_details: Dict[str, Any]) -> str:
    """
    Build instructions for the realtime session based on question details
    
    Args:
        question_details: Dictionary containing question details
        
    Returns:
        String containing instructions for the realtime session
    """
    instructions = f"""
You are an expert case interview assistant for a {question_details['difficulty']} {question_details['case_type']} case in the {question_details['industry']} industry.

CASE CONTEXT:
{question_details['case_prompt']}

CURRENT QUESTION ({question_details['question_number']} of 4):
{question_details['question_prompt']}

YOUR ROLE:
- You are assisting with question #{question_details['question_number']} only
- Provide thoughtful and structured guidance based on the question
- This is a {question_details['lead_type']} case, so {'wait for the candidate to drive the conversation' if question_details['lead_type'] == 'Candidate-led' else 'help guide the candidate through the analysis'}
- Evaluator's expectations: {question_details['question_context']}

Be concise, supportive, and focus on helping the candidate demonstrate structured thinking and business acumen.
"""
    return instructions.strip()

def generate_session_token_for_question(db: Session, interview_id: UUID, user_id: UUID, question_number: int, ttl: int = 3600) -> Dict[str, Any]:
    """
    Generate a short-lived session token for a specific interview question
    
    Args:
        db: Database session
        interview_id: The ID of the interview
        user_id: The ID of the user
        question_number: The question number (1-4)
        ttl: Time to live in seconds (default: 1 hour)
        
    Returns:
        Dictionary containing session token information, structured like OpenAI's Realtime session object
    """
    # Get question details
    question_details = get_question_details(db, interview_id, question_number)
    
    # Build instructions based on question details
    instructions = build_interview_instructions(question_details)
    
    # Generate a random token
    token = secrets.token_hex(32)
    
    # Calculate expiration time
    expiration = datetime.utcnow() + timedelta(seconds=ttl)
    expiration_timestamp = int(expiration.timestamp())
    
    return {
        "id": f"sess_{interview_id}_{user_id}_{question_number}",
        "object": "realtime.session",
        "model": "gpt-4o-realtime-preview",
        "modalities": ["audio", "text"],
        "instructions": instructions,
        "voice": "alloy",
        "input_audio_format": "pcm16",
        "output_audio_format": "pcm16",
        "input_audio_transcription": {
            "model": "whisper-1"
        },
        "turn_detection": {
            "type": "server_vad",
            "threshold": 0.5,
            "prefix_padding_ms": 300,
            "silence_duration_ms": 200
        },
        "tools": [],
        "tool_choice": "none",
        "temperature": 0.8,
        "max_response_output_tokens": "inf",
        "client_secret": {
            "value": token,
            "expires_at": expiration_timestamp
        },
        "interview_id": str(interview_id),
        "user_id": str(user_id),
        "question_number": question_number,
        "expires_at": expiration.isoformat(),
        "ttl": ttl
    } 