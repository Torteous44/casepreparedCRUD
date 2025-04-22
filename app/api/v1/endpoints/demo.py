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

# Common prompt components that can be reused
PROMPT_TEMPLATES = {
    "opening_steps": """
1) Restate the prompt to ensure alignment
2) Add colors (optional): Quick thoughts demonstrating business acumen
3) Ask 2-3 clarifying questions about: geography, financial goals, business model
4) Ask for a moment to structure approach
""",
    "structure_steps": """
1) Give a 15-second big-picture overview
2) Cover key points for this case type
3) Add stories/insights (optional)
4) Finish with a prioritization question
""",
    "brainstorm_steps": """
1) Optional: Present a horizontal structure
2) Provide at least 4 ideas
3) Add contextual color (optional)
"""
}

# Hardcoded demo interview templates with more concise prompts
DEMO_TEMPLATES = {
    "market-entry": {
        "id": "11111111-1111-1111-1111-111111111111",
        "case_type": "Market Entry",
        "lead_type": "Interviewer-led",
        "difficulty": "Medium",
        "company": "McKinsey",
        "industry": "Oil & Gas",
        "title": "Premier Oil Profitability Improvement",
        "description_short": "Design a profitability improvement plan for Premier Oil, a major UK-based offshore oil producer affected by pandemic-induced price collapse.",
        "description_long": "The pandemic-induced collapse in oil prices sharply reduced profitability of Premier Oil, a major UK-based offshore upstream oil and gas producer. Premier Oil operates rigs in seven areas in the North Sea. The CEO has brought your team in to design a profitability improvement plan.",
        "image_url": "https://images.unsplash.com/photo-1509042239860-f550ce710b93?q=80&w=1974&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
        "duration": 30,
        "questions": [
		{
			"number": 1,
			"title": "Opening",
			"prompt": """<prompt>
You are an interviewer for McKinsey conducting a case interview, for an AI service to help candidates prepare for their case interviews.
Read: "I am an interviewer from McKinsey, welcome to your case interview. Here is the case prompt: The pandemic-induced collapse in oil prices sharply reduced profitability of Premier Oil, a major UK-based offshore upstream oil and gas producer. Premier Oil operates rigs in seven areas in the North Sea. The CEO has brought your team in to design a profitability improvement plan."

Answer clarifying questions using this information, do NOT make up information:
• Client has assets only in the North Sea and doesn't plan to adjust its portfolio
• Profitability for 2020 was -12% (losses), common in the industry that year
• No specific profitability improvement goal
• Client is an independent oil and gas company owned by various strategic investors
</prompt>"""
		},
		{
			"number": 2,
			"title": "Initial Structuring",
			"prompt": """<prompt>
You are an interviewer for McKinsey conducting a case interview, for an AI service to help candidates prepare for their case interviews.
Ask: "What factors would you consider to work on this problem? Feel free to take your time before answering the question."

Candidate should:
1) Give a brief overview
2) Cover: profitability analysis, business model, external factors
3) Add industry insights (optional)
4) Finish with a question

Guide them to consider:
• Industry benchmarks & trends
• Client's portfolio & operations
• Financial analysis (revenue/cost)
• Profitability improvement opportunities
</prompt>"""
		},
		{
			"number": 3,
			"title": "Cost Breakdown",
			"prompt": """<prompt>
You are an interviewer for McKinsey conducting a case interview.
Ask: "Given there is not much Premier Oil can do to increase sales, the manager wants us to focus on costs. To begin with, what are Premier Oil's major expenses?"

Candidate should provide at least 4 cost categories.

Key costs include:
• Fixed: Maintenance, R&D, Overhead, Energy
• Variable: Labor, Platform supplies, Extraction supplies, Transportation
</prompt>"""
		},
		{
			"number": 4,
			"title": "Maintenance Cost Drivers",
			"prompt": """<prompt>
You are an interviewer for McKinsey conducting a case interview.
Ask: "Let's talk about maintenance costs. We've learned they have been increasing for Premier Oil's offshore platforms. What might be the reasons behind it?. Feel free to take your time before answering the question."

Candidate should provide at least 4 reasons.

Potential reasons:
• Aging equipment requiring more frequent maintenance
• Stricter environmental regulations
• Rising costs of parts and labor
• Emergency repairs due to equipment failures
• Transportation costs for parts/technicians
</prompt>"""
		}
	]
    },
    "profitability": {
        "id": "22222222-2222-2222-2222-222222222222",
        "case_type": "Profitability",
        "lead_type": "Candidate-led",
        "difficulty": "Hard",
        "company": "Bain",
        "industry": "Industrial Equipment",
        "title": "Henderson Electric Software Revenue Growth",
        "description_short": "Design a revenue growth plan to boost sales of Henderson Electric's IoT-enabled software for industrial air conditioning systems.",
        "description_long": "Henderson Electric offers industrial air conditioning units, maintenance services and Internet-of-Things (IoT) enabled software to monitor system functionality in real-time. The overall sales are $1B, however the software revenue remains low. The CEO has hired your team to design a revenue growth plan to boost sales of their IoT-enabled software.",
        "image_url": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
        "duration": 35,
        "questions": [
		{
			"number": 1,
			"title": "Opening",
			"prompt": """<prompt>
You are an interviewer for Bain conducting a case interview, for an AI service to help candidates prepare for their case interviews.
Read: "I am an interviewer from Bain and Company, welcome to your case interview. Here is the case prompt: Henderson Electric offers industrial air conditioning units, maintenance services and Internet-of-Things (IoT) enabled software to monitor system functionality in real-time. The overall sales are $1B, however the software revenue remains low. The CEO has hired your team to design a revenue growth plan to boost sales of their IoT-enabled software."

Provide these details when asked:
• Client offers various air conditioning units and cooling equipment
• Software alerts customers on system issues and maintenance needs
• Software works with equipment from other manufacturers
• No specific revenue goals
• Client serves diverse facilities: food processing, medicine production, computer chip manufacturing, etc.
</prompt>"""
		},
		{
			"number": 2,
			"title": "Structuring Low Software Sales Analysis",
			"prompt": """<prompt>
You are an interviewer for Bain conducting a case interview.
Ask: "How would you approach analyzing the low sales of the client's software and developing recommendations? Feel free to take time to structure your response."

Candidate should:
1) Present a structured approach
2) Cover: market analysis, business model, sales analysis, growth strategies

Guide them to consider:
• Software market: growth, competitors, trends
• Henderson's software: differentiators, target clients, sales team
• Sales analysis: pricing model, client growth, revenue structure
• Growth strategies: marketing, pricing, distribution, value proposition
</prompt>"""
		},
		{
			"number": 3,
			"title": "Growth Strategy Brainstorm",
			"prompt": """<prompt>
You are an interviewer for Bain conducting a case interview.
Ask: "Any ideas on how to help Henderson Electric increase the sales of their monitoring software? Feel free to take time to structure your response."

Candidate should provide at least 4 growth strategies.

Potential strategies:
• Marketing: Events, reports, campaigns
• Pricing: Adjust levels, bundling, different models (tiers, trials)
• Distribution: Improve sales training, address objections
• Value proposition: Customize features, add support, improve quality
</prompt>"""
		},
		{
			"number": 4,
			"title": "Understanding Market Adoption Gap",
			"prompt": """<prompt>
You are an interviewer for Bain conducting a case interview.
Ask: "Out of 16k large manufacturing facilities in the U.S. only 4k have adopted the software to monitor their air conditioning units. Why don't the rest 12k do the same?  Feel free to take time to structure your response."

Candidate should provide at least 4 reasons.

Factors to consider:
• Financial: High price, IT burden, unclear ROI
• Low perceived value: Lack of awareness, manual systems working adequately
• Risks: Locked-in contracts, bugs, implementation disruptions, security concerns
</prompt>"""
		}
	]
    },
    "merger": {
        "id": "33333333-3333-3333-3333-333333333333",
        "case_type": "Merger & Acquisition",
        "lead_type": "Interviewer-led",
        "difficulty": "Medium",
        "company": "BCG",
        "industry": "Electronics Manufacturing",
        "title": "Betacer Video Game Market Entry",
        "description_short": "Evaluate whether Betacer, a major U.S. electronics manufacturer, should enter the U.S. video-game market given low growth in other segments.",
        "description_long": "Betacer is a major U.S. electronics manufacturer that offers laptop and desktop PCs, tablets, smartphones, monitors, projectors and cloud solutions. Given low growth in various electronics segments, Betacer is considering entering the U.S. video-game market. They've reached out for advice on whether this is wise.",
        "image_url": "https://images.unsplash.com/photo-1576091160550-2173dba999ef?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
        "duration": 30,
        "questions": [
		{
			"number": 1,
			"title": "Opening",
			"prompt": """<prompt>
You are an interviewer for BCG conducting a case interview, for an AI service that helps candidates prepare for their case interviews.
Read: "I am an interviewer from BCG and I am here to conduct your case interview. Here is your case prompt: Betacer is a major U.S. electronics manufacturer that offers laptop and desktop PCs, tablets, smartphones, monitors, projectors and cloud solutions. Given low growth in various electronics segments, Betacer is considering entering the U.S. video-game market. They've reached out for advice on whether this is wise."

Provide these details when asked:
• Betacer wants payback within 2 years after market entry
• They plan to target the mass market, not hardcore gamers
• Focus is on the U.S. video-game market ($41B in 2020)
• Global market is $175B and grew rapidly in 2020
• The market is fragmented with many major players
</prompt>"""
		},
		{
			"number": 2,
			"title": "Market Entry Assessment",
			"prompt": """<prompt>
You are an interviewer for BCG conducting a case interview.
Ask: "What factors would you consider to suggest whether Betacer should enter the video-game market? Feel free to take some time to structure your response"

Candidate should:
1) Give a structured overview
2) Cover: market assessment, business model, financial analysis, risks

Guide them to consider:
• Video game market: size, growth, competition, profitability
• Betacer's approach: target segments, offerings, distribution
• Financial assessment: profitability, costs, capex, payback period
• Entry risks: market, financial, operational
</prompt>"""
		},
		{
			"number": 3,
			"title": "Customer Adoption Drivers",
			"prompt": """<prompt>
You are an interviewer for BCG conducting a case interview.
Ask: "What factors would you consider to suggest whether Betacer should enter the video-game market? Feel free to take some time to structure your response"

Candidate should provide at least 4 factors driving customer adoption.

Key drivers include:
• Brand perception: awareness, recommendations, ratings
• Pricing: trials, affordability, compatibility with existing devices
• Distribution: easy access through app stores
• Value proposition: popular genres, platform compatibility, social features
</prompt>"""
		},
		{
			"number": 4,
			"title": "Synergy Opportunities",
			"prompt": """<prompt>
You are an interviewer for BCG conducting a case interview.
Ask: "What synergies might Betacer capture by entering the video-game market? Feel free to take some time to structure your response"

Candidate should identify both revenue and cost synergies.

Potential synergies:
• Revenue: Leverage distribution, bundle hardware and games, co-marketing
• Cost: Shared overhead, volume discounts with sales partners
</prompt>"""
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
def get_demo_turn_credentials(ttl: int = Query(86400, ge=300, le=604800, description="Token time-to-live in seconds")) -> Any:
    """
    Get TURN server credentials for WebRTC in demo mode
    
    Args:
        ttl: Time to live in seconds (default: 24 hours, min: 5 minutes, max: 7 days)
        
    Returns:
        Dictionary containing TURN server credentials
    """
    logger.info(f"Generating demo TURN credentials with TTL: {ttl}")
    
    try:
        # Create a guest username for the demo
        username = f"demo-user-{secrets.token_hex(4)}"
        
        # First try to use the credential service
        logger.info(f"Attempting to use credential service with username: {username}")
        try:
            return credential_service.generate_turn_credentials(username=username, ttl=ttl)
        except Exception as svc_error:
            logger.error(f"Error using credential service: {str(svc_error)}")
            # Continue to fallback method
        
        # Try direct Twilio API call if credential service fails
        try:
            # Get Twilio credentials from environment variables
            account_sid = os.getenv("TWILIO_ACCOUNT_SID")
            auth_token = os.getenv("TWILIO_AUTH_TOKEN")
            
            if account_sid and auth_token:
                logger.info(f"Using Twilio account SID: {account_sid[:6]}...{account_sid[-4:]}")
                
                # Twilio API endpoint for Network Traversal Service
                url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Tokens.json"
                
                # Set TTL for Twilio token (in seconds)
                data = {"Ttl": str(ttl)}
                
                # Make request to Twilio API
                import requests
                response = requests.post(url, data=data, auth=(account_sid, auth_token), timeout=10)
                
                # Check if request was successful
                if response.status_code in [200, 201]:
                    token_data = response.json()
                    
                    # Extract TURN/STUN server information
                    ice_servers = token_data.get("ice_servers", [])
                    
                    if ice_servers:
                        logger.info(f"Successfully generated Twilio TURN credentials with {len(ice_servers)} ice servers")
                        
                        # Return formatted credentials
                        return {
                            "username": token_data.get("username", username),
                            "password": token_data.get("password", ""),
                            "ttl": int(token_data.get("ttl", ttl)),
                            "expiration": int(time.time()) + ttl,
                            "ice_servers": ice_servers
                        }
            else:
                logger.warning("Twilio credentials not found in environment variables")
        except Exception as twilio_error:
            logger.error(f"Error making direct Twilio API call: {str(twilio_error)}")
            # Continue to fallback
        
        # Provide fallback TURN credentials that can work in many scenarios
        logger.info("Using fallback TURN/STUN credentials")
        current_time = int(time.time())
        expiration = current_time + ttl
        
        # Return a comprehensive fallback that works in most scenarios
        return {
            "username": username,
            "password": "demo_credential",
            "ttl": ttl,
            "expiration": expiration,
            "urls": [
                "stun:stun.l.google.com:19302",
                "stun:stun1.l.google.com:19302",
                "stun:stun2.l.google.com:19302"
            ],
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
    except Exception as e:
        logger.error(f"Unhandled error generating demo TURN credentials: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate TURN credentials"
        )

def build_interview_instructions(template, question_number):
    """
    Helper function to build concise interview instructions
    """
    total_questions = len(template['questions'])
    question = template["questions"][question_number - 1]
    
    # Create streamlined instructions
    instructions = f"""You are an interviewer for a {template['case_type']} case interview about {template['company']} in the {template['industry']} industry.

CASE: {template['description_long']}

QUESTION {question_number}/{total_questions}: {question['title']}
Immediately say “Welcome to your interview, I am an interviewer from {template['company']}. Here is the case prompt for the interview:
{question['prompt']}

GUIDELINES:
• Guide professionally
• Provide hints only when needed
• Let candidate work independently
• Give constructive feedback
• Keep questions concise and to the point
• Keep answers concise and to the point
"
"""
    return instructions, question

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
        question_index = question_number - 1
        if question_index >= len(template["questions"]):
            raise IndexError(f"Question number {question_number} not found")
    except IndexError:
        raise HTTPException(
            status_code=404,
            detail=f"Question number {question_number} not found"
        )
    
    # Build instructions using helper function
    instructions, _ = build_interview_instructions(template, question_number)
    
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
            voice="echo"  # Using a consistent voice for demos
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
                "voice": "echo",
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
    
    # Special handling for invalid case types - map them to "market-entry"
    if case_type not in DEMO_TEMPLATES:
        logger.warning(f"Invalid case type '{case_type}' requested, falling back to 'market-entry'")
        case_type = "market-entry"
    
    template = DEMO_TEMPLATES[case_type]
    interview_id = DEMO_INTERVIEWS[case_type]
    
    # Build instructions using helper function
    instructions, question = build_interview_instructions(template, min(question_number, 4))
    logger.info(f"Using question: {question['title']}")
    
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
            "voice": "echo",
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