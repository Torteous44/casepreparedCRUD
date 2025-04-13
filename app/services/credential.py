import secrets
import time
import hmac
import hashlib
import os
import logging
import random
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from uuid import UUID
import requests
from dotenv import load_dotenv

from app.models.interview import Interview
from app.models.interview_template import InterviewTemplate

# Load environment variables
load_dotenv()

class APIKeyManager:
    def __init__(self, api_keys: List[str]):
        self.api_keys = [key for key in api_keys if key]  # Filter out empty keys
        self.current_index = 0
        self.usage_counts = {key: 0 for key in self.api_keys}

    def get_next_key(self) -> str:
        """
        Returns the next API key using a round-robin approach with
        basic error handling and usage tracking
        """
        if not self.api_keys:
            raise ValueError("No API keys available")

        # Get key with least usage
        selected_key = min(self.usage_counts.items(), key=lambda x: x[1])[0]
        self.usage_counts[selected_key] += 1
        
        return selected_key

    def mark_key_error(self, key: str) -> None:
        """
        Mark a key as having an error - could implement cooldown/removal logic here
        """
        if key in self.usage_counts:
            self.usage_counts[key] += 100  # Penalize this key temporarily

# Initialize the key manager with multiple API keys
api_key_manager = APIKeyManager([
    os.getenv("OPENAI_API_KEY"),
    os.getenv("OPENAI_API_KEY_BACKUP_1"),
    os.getenv("OPENAI_API_KEY_BACKUP_2"),
])

def get_voice_for_persona(persona: str = "interviewer") -> str:
    """
    Maps interview personas to specific OpenAI voices.
    
    :param persona: The interview persona type
    :return: The corresponding OpenAI voice ID
    """
    voice_mapping = {
        "friendly": "shimmer",
        "analytical": "onyx",
        "challenging": "fable",
        "interviewer": "alloy",
        "consultant": "nova"
    }
    
    return voice_mapping.get(persona.lower(), "alloy")  # Default to alloy if not found

def generate_turn_credentials(username: str, ttl: int = 86400) -> Dict[str, Any]:
    """
    Generate TURN server credentials using Twilio
    
    Args:
        username: The username to generate credentials for
        ttl: Time to live in seconds (default: 24 hours)
        
    Returns:
        Dictionary containing TURN server credentials
    """
    logger = logging.getLogger(__name__)
    
    try:
        # Get Twilio credentials from environment variables
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        
        if not account_sid or not auth_token:
            logger.error("Twilio credentials not found in environment variables")
            raise ValueError("Twilio credentials not found in environment variables")
        
        logger.info(f"Using Twilio account SID: {account_sid[:6]}...{account_sid[-4:]}")
        
        # Twilio API endpoint for Network Traversal Service
        url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Tokens.json"
        
        # Set TTL for Twilio token (in seconds)
        data = {"Ttl": str(ttl)}
        
        logger.info(f"Making request to Twilio API: {url}")
        
        # Make request to Twilio API
        response = requests.post(url, data=data, auth=(account_sid, auth_token), timeout=10)
        
        # Log response status
        logger.info(f"Twilio API response status: {response.status_code}")
        
        # Check if request was successful
        if response.status_code != 200:
            error_msg = f"Failed to get Twilio token: Status code {response.status_code}, Response: {response.text}"
            logger.error(error_msg)
            raise Exception(error_msg)
        
        # Parse response JSON
        token_data = response.json()
        logger.debug(f"Twilio response: {token_data}")
        
        # If we don't have ice_servers in the response, we'll use fallback values
        if "ice_servers" not in token_data:
            logger.warning("No ice_servers in Twilio response, using fallback values")
            return {
                "username": username,
                "password": "twilio_fallback_credential",
                "ttl": ttl,
                "expiration": int(time.time()) + ttl,
                "urls": [
                    "turn:global.turn.twilio.com:3478?transport=udp",
                    "turn:global.turn.twilio.com:3478?transport=tcp",
                    "turn:global.turn.twilio.com:443?transport=tcp",
                    "stun:global.stun.twilio.com:3478"
                ]
            }
        
        # Extract TURN/STUN server information
        ice_servers = token_data.get("ice_servers", [])
        urls = []
        username = token_data.get("username", "")
        password = token_data.get("password", "")
        
        for server in ice_servers:
            if "urls" in server:
                urls.append(server["urls"])
            elif "url" in server:
                urls.append(server["url"])
        
        logger.info(f"Successfully generated TURN credentials with {len(urls)} URLs")
        
        # Return formatted credentials
        return {
            "username": username,
            "password": password,
            "ttl": int(token_data.get("ttl", ttl)),
            "expiration": int(time.time()) + ttl,
            "urls": urls,
            "ice_servers": ice_servers  # Include the original ice_servers for full compatibility
        }
    except Exception as e:
        import traceback
        logger.error(f"Error generating TURN credentials: {str(e)}\n{traceback.format_exc()}")
        raise

def generate_session_token(interview_id: str, user_id: str, ttl: int = 3600) -> Dict[str, Any]:
    """
    Generate a short-lived session token for the realtime interview session
    
    Args:
        interview_id: The ID of the interview
        user_id: The ID of the user
        ttl: Time to live in seconds (default: 1 hour)
        
    Returns:
        Dictionary containing session token information with OpenAI ephemeral key
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Generating session token for interview {interview_id}, user {user_id}")
    
    # Create general instructions
    instructions = f"You are an interview assistant for interview {interview_id}. Provide helpful responses to the candidate."
    voice = "alloy"  # Default voice
    
    try:
        # Generate ephemeral key from OpenAI
        ephemeral_key = generate_openai_ephemeral_key(
            instructions=instructions, 
            ttl=ttl,
            voice=voice
        )
        
        # Add custom metadata to the response
        session_data = {
            "id": f"sess_{interview_id}_{user_id}",
            "interviewId": interview_id,
            "userId": user_id,
            "expiresAt": datetime.fromtimestamp(int(time.time()) + ttl).isoformat(),
            "ttl": ttl,
            "instructions": instructions,
            "realtimeSession": ephemeral_key
        }
        
        logger.info(f"Successfully generated session token with OpenAI ephemeral key")
        return session_data
    except Exception as e:
        logger.error(f"Error generating OpenAI ephemeral key: {str(e)}", exc_info=True)
        
        # Fallback with direct API key if ephemeral key generation fails
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            logger.error("OpenAI API key not found in environment variables")
            raise ValueError("OpenAI API key not configured")
            
        # Generate a random token
        token = secrets.token_hex(32)
        # Calculate expiration time
        expiration = datetime.utcnow() + timedelta(seconds=ttl)
        expiration_timestamp = int(expiration.timestamp())
        
        # Return a fallback format
        return {
            "id": f"sess_{interview_id}_{user_id}",
            "apiKey": openai_api_key,
            "instructions": instructions,
            "interviewId": interview_id,
            "userId": user_id,
            "expiresAt": expiration.isoformat(),
            "ttl": ttl,
            "client_secret": {
                "value": token,
                "expires_at": expiration_timestamp
            }
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
    logger = logging.getLogger(__name__)
    logger.info(f"Getting question details for interview {interview_id}, question {question_number}")
    
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        logger.error(f"Interview with ID {interview_id} not found")
        raise ValueError(f"Interview with ID {interview_id} not found")
    
    logger.info(f"Found interview. Template ID: {interview.template_id}")
    
    template = db.query(InterviewTemplate).filter(InterviewTemplate.id == interview.template_id).first()
    if not template:
        logger.error(f"Interview template with ID {interview.template_id} not found")
        raise ValueError(f"Interview template with ID {interview.template_id} not found")
    
    logger.info(f"Found template. Structure keys: {list(template.structure.keys()) if template.structure else 'None'}")
    
    question_key = f"question{question_number}"
    if not template.structure:
        logger.error(f"Template structure is None or empty")
        raise ValueError(f"Template structure is empty or not properly formatted")
    
    if question_key not in template.structure:
        logger.error(f"Question {question_number} not found in template structure")
        raise ValueError(f"Question {question_number} not found in interview template")
    
    logger.info(f"Found question details for {question_key}")
    
    try:
        question_data = template.structure[question_key]
        
        # Check if the required keys exist
        if "prompt" not in question_data or "context" not in question_data:
            logger.error(f"Question data missing required keys. Found keys: {list(question_data.keys())}")
            # Use default values if not found
            question_prompt = question_data.get("prompt", "No prompt available")
            question_context = question_data.get("context", "No context available")
        else:
            question_prompt = question_data["prompt"]
            question_context = question_data["context"]
        
        return {
            "question_number": question_number,
            "question_prompt": question_prompt,
            "question_context": question_context,
            "case_type": template.case_type,
            "lead_type": template.lead_type,
            "difficulty": template.difficulty,
            "company": template.company or "Unknown company",
            "industry": template.industry or "Unknown industry",
            "case_prompt": template.prompt
        }
    except Exception as e:
        logger.error(f"Error extracting question data: {str(e)}")
        # Return fallback data
        return {
            "question_number": question_number,
            "question_prompt": "Default question prompt for a case interview",
            "question_context": "Evaluate the candidate's structured thinking and problem-solving approach",
            "case_type": template.case_type,
            "lead_type": template.lead_type,
            "difficulty": template.difficulty,
            "company": template.company or "Unknown company",
            "industry": template.industry or "Unknown industry",
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

def generate_openai_ephemeral_key(
    instructions: str, 
    model: str = "gpt-4o-mini-realtime-preview",
    modalities: List[str] = ["audio", "text"],
    ttl: int = 3600,
    voice: Optional[str] = "alloy",
    temperature: float = 0.8,
) -> Dict[str, Any]:
    """
    Generate an ephemeral key from OpenAI for Realtime sessions
    
    Args:
        instructions: The instructions for the assistant
        model: The model to use
        modalities: Which modalities to enable
        ttl: Time to live in seconds
        voice: Voice to use for audio output
        temperature: Sampling temperature
        
    Returns:
        Dictionary containing the ephemeral key response from OpenAI
    """
    logger = logging.getLogger(__name__)
    
    # Prepare the payload
    payload = {
        "model": model,
        "modalities": modalities,
        "instructions": instructions,
        "voice": voice,
        "temperature": temperature,
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
    
    logger.info(f"Generating OpenAI ephemeral key with TTL: {ttl}")
    
    # Try keys until one works
    last_error = None
    for _ in range(len(api_key_manager.api_keys)):
        try:
            current_key = api_key_manager.get_next_key()
            headers = {
                "Authorization": f"Bearer {current_key}",
                "Content-Type": "application/json",
            }
            
            url = "https://api.openai.com/v1/realtime/sessions"
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            
            if response.status_code != 200:
                logger.error(f"Failed to generate ephemeral key with key {current_key[:8]}...: Status {response.status_code}, Response: {response.text}")
                api_key_manager.mark_key_error(current_key)
                last_error = f"Status {response.status_code}: {response.text}"
                continue
            
            ephemeral_key = response.json()
            logger.info(f"Successfully generated ephemeral key with key {current_key[:8]}...")
            
            return ephemeral_key
        except Exception as e:
            logger.error(f"Error generating ephemeral key with key {current_key[:8]}...: {str(e)}")
            api_key_manager.mark_key_error(current_key)
            last_error = str(e)
            continue
    
    # If we get here, all keys failed
    raise Exception(f"All API keys failed. Last error: {last_error}")

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
        Dictionary containing session token information with OpenAI ephemeral key
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Generating session token for interview {interview_id}, user {user_id}, question {question_number}")
    
    try:
        # Get question details
        question_details = get_question_details(db, interview_id, question_number)
        logger.info(f"Successfully retrieved question details")
        
        # Build instructions based on question details
        instructions = build_interview_instructions(question_details)
        logger.info(f"Generated instructions of length {len(instructions)}")
        
        # Determine persona and voice based on question details
        persona = question_details.get("lead_type", "interviewer")
        voice = get_voice_for_persona(persona)
    except Exception as e:
        logger.error(f"Error getting question details: {str(e)}. Using fallback instructions.", exc_info=True)
        # Fallback instructions
        instructions = f"""
You are an expert case interview assistant.

CURRENT QUESTION ({question_number} of 4):
Please help the candidate with this case interview question.

YOUR ROLE:
- You are assisting with question #{question_number} only
- Provide thoughtful and structured guidance
- Help the candidate demonstrate structured thinking and business acumen
- Be concise, clear, and supportive

Be patient and helpful with the candidate.
"""
        voice = "alloy"  # Default voice
        
    try:
        # Generate ephemeral key from OpenAI
        ephemeral_key = generate_openai_ephemeral_key(
            instructions=instructions, 
            ttl=ttl,
            voice=voice
        )
        
        # Add custom metadata to the response
        session_data = {
            "id": f"sess_{interview_id}_{user_id}_{question_number}",
            "interviewId": str(interview_id),
            "userId": str(user_id),
            "questionNumber": question_number,
            "expiresAt": datetime.fromtimestamp(int(time.time()) + ttl).isoformat(),
            "ttl": ttl,
            "instructions": instructions,
            "realtimeSession": ephemeral_key
        }
        
        logger.info(f"Successfully generated session token with OpenAI ephemeral key")
        return session_data
    except Exception as e:
        logger.error(f"Error generating OpenAI ephemeral key: {str(e)}", exc_info=True)
        
        # Fallback with direct API key if ephemeral key generation fails
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            logger.error("OpenAI API key not found in environment variables")
            raise ValueError("OpenAI API key not configured")
            
        # Generate a random token
        token = secrets.token_hex(32)
        # Calculate expiration time
        expiration = datetime.utcnow() + timedelta(seconds=ttl)
        expiration_timestamp = int(expiration.timestamp())
        
        # Return a fallback format
        return {
            "id": f"sess_{interview_id}_{user_id}_{question_number}",
            "apiKey": openai_api_key,
            "instructions": instructions,
            "interviewId": str(interview_id),
            "userId": str(user_id),
            "questionNumber": question_number,
            "expiresAt": expiration.isoformat(),
            "ttl": ttl,
            "client_secret": {
                "value": token,
                "expires_at": expiration_timestamp
            }
        } 