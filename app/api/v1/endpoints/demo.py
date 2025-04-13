from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4
import secrets
import time
from datetime import datetime, timedelta
import os
import logging
from fastapi import APIRouter, Query, Path, HTTPException, status, Body
from pydantic import BaseModel

# We're not importing the authentication dependencies as these will be public endpoints
from app.db.session import get_db
from app.services import credential as credential_service

router = APIRouter()
logger = logging.getLogger(__name__)

# Hardcoded demo interview templates
DEMO_TEMPLATES = {
    "market-entry": {
        "id": "11111111-1111-1111-1111-111111111111",
        "case_type": "Market Entry",
        "lead_type": "Interviewer-led",
        "difficulty": "Medium",
        "company": "CoffeeChain",
        "industry": "Food & Beverage",
        "title": "CoffeeChain Market Entry Strategy",
        "description_short": "Help CoffeeChain decide if they should enter the European market with their premium coffee products.",
        "description_long": "CoffeeChain is a US-based premium coffee chain looking to expand internationally. They're considering entering the European market but are unsure about the market dynamics, competition, and potential profitability. Your task is to assess if this is a good strategic move.",
        "image_url": "https://images.unsplash.com/photo-1509042239860-f550ce710b93?q=80&w=1974&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
        "duration": 30,
        "questions": [
            {
                "number": 1,
                "title": "Market Analysis",
                "prompt": "What are the key factors CoffeeChain should consider when analyzing the European coffee market?"
            },
            {
                "number": 2,
                "title": "Competition Assessment",
                "prompt": "Who are the main competitors in the European premium coffee market, and what are their strengths and weaknesses?"
            },
            {
                "number": 3,
                "title": "Entry Strategy",
                "prompt": "What market entry strategy would you recommend for CoffeeChain?"
            },
            {
                "number": 4,
                "title": "Financial Analysis",
                "prompt": "What financial factors should CoffeeChain consider before making this investment?"
            }
        ]
    },
    "profitability": {
        "id": "22222222-2222-2222-2222-222222222222",
        "case_type": "Profitability",
        "lead_type": "Candidate-led",
        "difficulty": "Hard",
        "company": "TechNow",
        "industry": "Technology",
        "title": "TechNow Profitability Challenge",
        "description_short": "Help TechNow identify why their profits have declined by 30% over the past year.",
        "description_long": "TechNow is a leading technology retailer that has seen a 30% decline in profitability over the past year despite stable revenues. The CEO has hired you to diagnose the causes of this decline and recommend solutions to restore profitability.",
        "image_url": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
        "duration": 35,
        "questions": [
            {
                "number": 1,
                "title": "Problem Definition",
                "prompt": "How would you structure your approach to diagnose TechNow's profitability issue?"
            },
            {
                "number": 2,
                "title": "Cost Analysis",
                "prompt": "What cost factors might be contributing to TechNow's profit decline?"
            },
            {
                "number": 3,
                "title": "Revenue Analysis",
                "prompt": "Could there be revenue-related issues affecting profitability despite stable overall revenue?"
            },
            {
                "number": 4,
                "title": "Recommendations",
                "prompt": "What recommendations would you make to help TechNow return to previous profitability levels?"
            }
        ]
    },
    "merger": {
        "id": "33333333-3333-3333-3333-333333333333",
        "case_type": "Merger & Acquisition",
        "lead_type": "Interviewer-led",
        "difficulty": "Medium",
        "company": "HealthFirst",
        "industry": "Healthcare",
        "title": "HealthFirst Acquisition Decision",
        "description_short": "Help HealthFirst evaluate the potential acquisition of MediTech, a healthcare technology startup.",
        "description_long": "HealthFirst, a major healthcare provider, is considering acquiring MediTech, a promising healthcare technology startup with an innovative patient management platform. Your task is to evaluate whether this acquisition makes strategic and financial sense.",
        "image_url": "https://images.unsplash.com/photo-1576091160550-2173dba999ef?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
        "duration": 30,
        "questions": [
            {
                "number": 1,
                "title": "Strategic Fit",
                "prompt": "How well does MediTech's technology align with HealthFirst's strategic objectives?"
            },
            {
                "number": 2,
                "title": "Valuation",
                "prompt": "How would you approach valuing MediTech for this acquisition?"
            },
            {
                "number": 3,
                "title": "Integration Challenges",
                "prompt": "What integration challenges might arise if HealthFirst acquires MediTech?"
            },
            {
                "number": 4,
                "title": "Decision Recommendation",
                "prompt": "Based on your analysis, would you recommend that HealthFirst proceed with the acquisition?"
            }
        ]
    }
}

# Demo interview IDs for tracking "sessions"
DEMO_INTERVIEWS = {
    "market-entry": "44444444-4444-4444-4444-444444444444",
    "profitability": "55555555-5555-5555-5555-555555555555",
    "merger": "66666666-6666-6666-6666-666666666666"
}

# In-memory storage for demo session progress (this would be in a database in production)
# Format: {"interview_id": {"current_question": 1, "questions_completed": []}}
DEMO_PROGRESS = {}

@router.get("/templates", response_model=List[Dict[str, Any]])
def list_demo_templates() -> Any:
    """
    List all available demo interview templates
    """
    templates = []
    for case_type, template in DEMO_TEMPLATES.items():
        templates.append({
            "id": template["id"],
            "case_type": template["case_type"],
            "lead_type": template["lead_type"],
            "difficulty": template["difficulty"],
            "company": template["company"],
            "industry": template["industry"],
            "title": template["title"],
            "description_short": template["description_short"],
            "description_long": template["description_long"],
            "image_url": template["image_url"],
            "duration": template["duration"]
        })
    return templates

@router.get("/templates/{template_id}", response_model=Dict[str, Any])
def get_demo_template(template_id: str) -> Any:
    """
    Get a specific demo template by ID
    """
    for case_type, template in DEMO_TEMPLATES.items():
        if template["id"] == template_id:
            return template
    
    raise HTTPException(
        status_code=404,
        detail="Demo template not found"
    )

@router.get("/interviews/{case_type}", response_model=Dict[str, Any])
def get_demo_interview(case_type: str = Path(..., description="Demo case type: market-entry, profitability, or merger")) -> Any:
    """
    Get a demo interview by case type
    """
    if case_type not in DEMO_TEMPLATES:
        raise HTTPException(
            status_code=404,
            detail=f"Demo interview not found. Available options: {', '.join(DEMO_TEMPLATES.keys())}"
        )
    
    template = DEMO_TEMPLATES[case_type]
    interview_id = DEMO_INTERVIEWS[case_type]
    
    # Initialize or get progress data
    if interview_id not in DEMO_PROGRESS:
        DEMO_PROGRESS[interview_id] = {
            "current_question": 1,
            "questions_completed": [],
            "started_at": datetime.utcnow().isoformat(),
            "completed_at": None,
            "status": "in-progress"
        }
    
    return {
        "id": interview_id,
        "template_id": template["id"],
        "status": DEMO_PROGRESS[interview_id]["status"],
        "progress_data": {
            "current_question": DEMO_PROGRESS[interview_id]["current_question"],
            "questions_completed": DEMO_PROGRESS[interview_id]["questions_completed"]
        },
        "started_at": DEMO_PROGRESS[interview_id]["started_at"],
        "completed_at": DEMO_PROGRESS[interview_id]["completed_at"],
        "template": template
    }

@router.get("/turn-credentials", response_model=Dict[str, Any])
def get_demo_turn_credentials() -> Any:
    """
    Get TURN server credentials for WebRTC in demo mode
    """
    try:
        # Create a guest username for the demo
        username = f"demo-user-{secrets.token_hex(4)}"
        
        # Use the same credential generation as the main app but with the demo username
        return credential_service.generate_turn_credentials(username=username)
    except Exception as e:
        logger.error(f"Error generating demo TURN credentials: {str(e)}")
        
        # Provide fallback TURN credentials that can work in many scenarios
        # This is not ideal but allows the demo to function when Twilio is unavailable
        logger.info("Using fallback TURN credentials for demo")
        current_time = int(time.time())
        expiration = current_time + 86400  # 24 hours
        
        return {
            "username": username,
            "ttl": 86400,
            "expiration": expiration,
            "ice_servers": [
                {
                    "urls": [
                        "stun:stun.l.google.com:19302",
                        "stun:stun1.l.google.com:19302",
                        "stun:stun2.l.google.com:19302"
                    ]
                }
            ]
        }

@router.get("/interviews/{case_type}/questions/{question_number}/token", response_model=Dict[str, Any])
def get_demo_question_token(
    case_type: str = Path(..., description="Demo case type: market-entry, profitability, or merger"),
    question_number: int = Path(..., ge=1, le=4, description="Question number (1-4)"),
    ttl: int = Query(3600, ge=300, le=7200, description="Token time-to-live in seconds")
) -> Any:
    """
    Generate a token for a specific demo interview question
    """
    if case_type not in DEMO_TEMPLATES:
        raise HTTPException(
            status_code=404,
            detail=f"Demo interview not found. Available options: {', '.join(DEMO_TEMPLATES.keys())}"
        )
    
    template = DEMO_TEMPLATES[case_type]
    interview_id = DEMO_INTERVIEWS[case_type]
    
    # Initialize progress tracking if not exists
    if interview_id not in DEMO_PROGRESS:
        DEMO_PROGRESS[interview_id] = {
            "current_question": 1,
            "questions_completed": [],
            "started_at": datetime.utcnow().isoformat(),
            "completed_at": None,
            "status": "in-progress"
        }
    
    # Check if the interview is in progress
    if DEMO_PROGRESS[interview_id]["status"] != "in-progress":
        raise HTTPException(
            status_code=400,
            detail="Demo interview is not in progress"
        )
    
    # Check if the requested question is available
    current_question = DEMO_PROGRESS[interview_id]["current_question"]
    if question_number > current_question:
        raise HTTPException(
            status_code=400,
            detail="Cannot access future questions. Complete the current question first."
        )
    
    # Get the specific question
    try:
        question = template["questions"][question_number - 1]
    except IndexError:
        raise HTTPException(
            status_code=404,
            detail=f"Question number {question_number} not found"
        )
    
    # Create the ephemeral key for this session
    try:
        # Build customized instructions for this specific demo question
        instructions = f"""You are an interviewer for a {template['case_type']} case interview about {template['company']} in the {template['industry']} industry.
        
The case is: {template['description_long']}

Current question: {question['title']} - {question['prompt']}

You should act as a professional interviewer, guiding the candidate through this question. Provide hints when needed, but let the candidate work through the problem. Give constructive feedback on their approach.
"""
        
        # Get the OpenAI API key
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            logger.error("OpenAI API key not found in environment variables")
            raise HTTPException(
                status_code=500,
                detail="OpenAI API key not configured"
            )
        
        # Try to generate ephemeral key through the credential service first
        try:
            ephemeral_key = credential_service.generate_openai_ephemeral_key(
                instructions=instructions,
                ttl=ttl,
                voice="alloy"  # Using a consistent voice for demos
            )
            
            # Add custom metadata
            session_token = {
                "id": f"demo_sess_{interview_id}_{question_number}",
                "interviewId": str(interview_id),
                "userId": "demo-user",
                "questionNumber": question_number,
                "expiresAt": datetime.fromtimestamp(int(time.time()) + ttl).isoformat(),
                "ttl": ttl,
                "instructions": instructions,
                "realtimeSession": ephemeral_key
            }
            
            return session_token
            
        except Exception as e:
            logger.error(f"Error using credential service for ephemeral key: {str(e)}")
            logger.info("Trying direct OpenAI API call for ephemeral key")
            
            # Direct implementation of OpenAI realtime API call
            try:
                import requests
                
                url = "https://api.openai.com/v1/realtime/sessions"
                headers = {
                    "Authorization": f"Bearer {openai_api_key}",
                    "Content-Type": "application/json"
                }
                
                # Prepare the request payload
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
                
                # Make the API call
                response = requests.post(url, headers=headers, json=payload, timeout=10)
                
                # Check for success
                if response.status_code in [200, 201]:
                    ephemeral_key = response.json()
                    
                    # Return success with ephemeral key
                    return {
                        "id": f"demo_sess_{interview_id}_{question_number}",
                        "interviewId": str(interview_id),
                        "userId": "demo-user",
                        "questionNumber": question_number,
                        "expiresAt": datetime.fromtimestamp(int(time.time()) + ttl).isoformat(),
                        "ttl": ttl,
                        "instructions": instructions,
                        "realtimeSession": ephemeral_key
                    }
                else:
                    logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
                    raise Exception(f"OpenAI API error: {response.status_code}")
                    
            except Exception as api_error:
                logger.error(f"Direct OpenAI API call failed: {str(api_error)}")
                # Continue to use fallback below
            
            # Last resort fallback with direct API key
            token = secrets.token_hex(32)
            expiration = datetime.utcnow() + timedelta(seconds=ttl)
            expiration_timestamp = int(expiration.timestamp())
            
            return {
                "id": f"demo_sess_{interview_id}_{question_number}",
                "apiKey": openai_api_key,
                "instructions": instructions,
                "interviewId": str(interview_id),
                "userId": "demo-user",
                "questionNumber": question_number,
                "expiresAt": expiration.isoformat(),
                "ttl": ttl,
                "client_secret": {
                    "value": token,
                    "expires_at": expiration_timestamp
                }
            }
            
    except Exception as e:
        logger.error(f"Error generating demo question token: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate session token"
        )

class DemoQuestionComplete(BaseModel):
    case_type: str
    question_number: int

@router.post("/interviews/complete-question", response_model=Dict[str, Any])
def complete_demo_question(body: DemoQuestionComplete = Body(...)) -> Any:
    """
    Mark a demo question as complete and advance to the next question
    """
    case_type = body.case_type
    question_number = body.question_number
    
    if case_type not in DEMO_TEMPLATES:
        raise HTTPException(
            status_code=404,
            detail=f"Demo interview not found. Available options: {', '.join(DEMO_TEMPLATES.keys())}"
        )
    
    interview_id = DEMO_INTERVIEWS[case_type]
    
    # Initialize progress tracking if not exists
    if interview_id not in DEMO_PROGRESS:
        DEMO_PROGRESS[interview_id] = {
            "current_question": 1,
            "questions_completed": [],
            "started_at": datetime.utcnow().isoformat(),
            "completed_at": None,
            "status": "in-progress"
        }
    
    progress_data = DEMO_PROGRESS[interview_id]
    
    # Check if interview is in progress
    if progress_data["status"] != "in-progress":
        raise HTTPException(
            status_code=400,
            detail="Demo interview is not in progress"
        )
    
    # Validate that we're completing the current question
    if question_number != progress_data["current_question"]:
        raise HTTPException(
            status_code=400,
            detail="Can only complete the current question"
        )
    
    # Mark the question as completed
    if question_number not in progress_data["questions_completed"]:
        progress_data["questions_completed"].append(question_number)
    
    # Advance to next question
    next_question = question_number + 1
    progress_data["current_question"] = next_question if next_question <= 4 else 4
    
    # Check if all questions are completed
    if len(progress_data["questions_completed"]) >= 4 and all(q in progress_data["questions_completed"] for q in range(1, 5)):
        progress_data["status"] = "completed"
        progress_data["completed_at"] = datetime.utcnow().isoformat()
    
    # Save progress
    DEMO_PROGRESS[interview_id] = progress_data
    
    template = DEMO_TEMPLATES[case_type]
    
    # Return the updated interview
    return {
        "id": interview_id,
        "template_id": template["id"],
        "status": progress_data["status"],
        "progress_data": {
            "current_question": progress_data["current_question"],
            "questions_completed": progress_data["questions_completed"]
        },
        "started_at": progress_data["started_at"],
        "completed_at": progress_data["completed_at"],
        "template": template
    }

@router.post("/reset/{case_type}", response_model=Dict[str, Any])
def reset_demo_interview(case_type: str = Path(..., description="Demo case type to reset")) -> Any:
    """
    Reset a demo interview's progress
    """
    if case_type not in DEMO_TEMPLATES:
        raise HTTPException(
            status_code=404,
            detail=f"Demo interview not found. Available options: {', '.join(DEMO_TEMPLATES.keys())}"
        )
    
    interview_id = DEMO_INTERVIEWS[case_type]
    
    # Reset progress data
    DEMO_PROGRESS[interview_id] = {
        "current_question": 1,
        "questions_completed": [],
        "started_at": datetime.utcnow().isoformat(),
        "completed_at": None,
        "status": "in-progress"
    }
    
    template = DEMO_TEMPLATES[case_type]
    
    return {
        "id": interview_id,
        "template_id": template["id"],
        "status": "in-progress",
        "progress_data": {
            "current_question": 1,
            "questions_completed": []
        },
        "started_at": DEMO_PROGRESS[interview_id]["started_at"],
        "completed_at": None,
        "message": f"Demo interview {case_type} has been reset"
    }

@router.get("/direct-token/{case_type}/{question_number}", response_model=Dict[str, Any])
def get_direct_token(
    case_type: str = Path(..., description="Demo case type: market-entry, profitability, or merger"),
    question_number: int = Path(..., ge=1, le=4, description="Question number (1-4)"),
    ttl: int = Query(3600, ge=300, le=7200, description="Token time-to-live in seconds")
) -> Any:
    """
    Generate a direct OpenAI token with minimal processing - designed for frontend compatibility
    """
    logger.info(f"Direct token requested for case_type={case_type}, question={question_number}, ttl={ttl}")
    
    # Special handling for "442" and any invalid case types - map them to "market-entry"
    if case_type not in DEMO_TEMPLATES:
        logger.warning(f"Invalid case type '{case_type}' requested, falling back to 'market-entry'")
        case_type = "market-entry"
    
    template = DEMO_TEMPLATES[case_type]
    interview_id = DEMO_INTERVIEWS[case_type]
    
    # Get the specific question (with bounds checking)
    question_index = max(0, min(question_number - 1, len(template["questions"]) - 1))
    question = template["questions"][question_index]
    logger.info(f"Using question: {question['title']}")
    
    # Create simplified instructions
    instructions = f"""You are an interviewer for a {template['case_type']} case interview about {template['company']} in the {template['industry']} industry.
    
The case is: {template['description_long']}

Current question: {question['title']} - {question['prompt']}

You should act as a professional interviewer, guiding the candidate through this question. Provide hints when needed, but let the candidate work through the problem. Give constructive feedback on their approach.
"""
    
    # Get the OpenAI API key
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        logger.error("OpenAI API key not found in environment variables")
        raise HTTPException(
            status_code=500,
            detail="OpenAI API key not configured"
        )
    
    # Direct implementation of OpenAI realtime API call
    try:
        import requests
        
        url = "https://api.openai.com/v1/realtime/sessions"
        headers = {
            "Authorization": f"Bearer {openai_api_key}",
            "Content-Type": "application/json"
        }
        
        # Prepare the request payload
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
        
        # Make the API call
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        # Check for success
        if response.status_code in [200, 201]:
            session_data = response.json()
            
            # Create a token object that matches what the frontend expects
            token = session_data.get("client_secret", {}).get("value")
            if not token:
                logger.error(f"Unable to extract token from response: {session_data}")
                raise HTTPException(
                    status_code=500,
                    detail="Invalid response format from OpenAI"
                )
            
            # Return a simplified response with just the token
            return {
                "token": token,
                "expires_at": session_data.get("client_secret", {}).get("expires_at")
            }
        else:
            logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
            raise HTTPException(
                status_code=response.status_code,
                detail=f"OpenAI API error: {response.text}"
            )
            
    except Exception as e:
        logger.error(f"Error generating OpenAI token: {str(e)}")
        
        # Last resort fallback with direct API key
        logger.info("Using fallback token method")
        token = secrets.token_hex(32)
        expiration = int((datetime.utcnow() + timedelta(seconds=ttl)).timestamp())
        
        return {
            "token": token,
            "expires_at": expiration
        } 