from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, get_subscription_active
from app.db.session import get_db
from app.models.user import User
from app.schemas.transcript_analysis import TranscriptAnalysisRequest, TranscriptAnalysisResponse
from app.services import transcript_analysis as analysis_service

router = APIRouter()

@router.post("/", response_model=TranscriptAnalysisResponse)
def analyze_transcript(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    analysis_in: TranscriptAnalysisRequest
) -> Any:
    """
    Analyze an interview transcript and return structured feedback
    
    This endpoint takes a transcript text and uses OpenAI's GPT-4o-mini model to generate 
    feedback in five categories:
    - Structure: Evaluation of problem-solving approach
    - Communication: Assessment of presence, clarity, and impact
    - Hypothesis-Driven Approach: Evaluation of early structuring
    - Qualitative Analysis: Assessment of business judgment and thinking
    - Adaptability: Evaluation of response to information and guidance
    """
    # Check if user is not admin, then verify subscription
    if not current_user.is_admin:
        get_subscription_active(current_user=current_user, db=db)
    
    try:
        # Call the analysis service
        analysis_result = analysis_service.analyze_transcript(transcript=analysis_in.transcript)
        return analysis_result
    except analysis_service.AnalysisError as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        ) 