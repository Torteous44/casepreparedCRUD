from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, get_subscription_active
from app.db.session import get_db
from app.models.user import User
from app.schemas.interview import Interview, InterviewCreate, InterviewUpdate
from app.services import interview as interview_service
from app.services import interview_template as template_service
from app.services import credential as credential_service

router = APIRouter()

@router.get("/", response_model=List[Interview])
def read_interviews(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
) -> Any:
    """
    Retrieve interviews for the current user
    """
    # Check if user is not admin, then verify subscription
    if not current_user.is_admin:
        # Import here to avoid circular import
        from app.auth.dependencies import get_subscription_active
        get_subscription_active(current_user=current_user, db=db)
    
    # If admin and user_id specified, get that user's interviews
    if current_user.is_admin and user_id:
        filters = {"user_id": user_id}
    else:
        # Regular users can only get their own interviews
        filters = {"user_id": current_user.id}
        
    if status:
        filters["status"] = status
    
    interviews = interview_service.get_interviews(
        db=db, skip=skip, limit=limit, filters=filters
    )
    return interviews

@router.post("/", response_model=Interview)
def create_interview(
    *,
    db: Session = Depends(get_db),
    interview_in: InterviewCreate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Create new interview session
    """
    # Check if user is not admin, then verify subscription
    if not current_user.is_admin:
        # Import here to avoid circular import
        from app.auth.dependencies import get_subscription_active
        get_subscription_active(current_user=current_user, db=db)
    
    # Verify that the template exists
    template = template_service.get_template_by_id(db=db, template_id=interview_in.template_id)
    if not template:
        raise HTTPException(
            status_code=404,
            detail="Template not found",
        )
    
    interview = interview_service.create_interview(
        db=db, interview_in=interview_in, user_id=current_user.id
    )
    return interview

@router.get("/{interview_id}", response_model=Interview)
def read_interview(
    *,
    db: Session = Depends(get_db),
    interview_id: str,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get interview by ID
    """
    # Check if user is not admin, then verify subscription
    if not current_user.is_admin:
        # Import here to avoid circular import
        from app.auth.dependencies import get_subscription_active
        get_subscription_active(current_user=current_user, db=db)
    
    interview = interview_service.get_interview_by_id(db=db, interview_id=interview_id)
    if not interview:
        raise HTTPException(
            status_code=404,
            detail="Interview not found",
        )
    
    # Ensure user can only access their own interviews unless they're an admin
    if interview.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to access this interview")
    
    return interview

@router.patch("/{interview_id}", response_model=Interview)
def update_interview(
    *,
    db: Session = Depends(get_db),
    interview_id: str,
    interview_in: InterviewUpdate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Update interview status or metadata
    """
    # Check if user is not admin, then verify subscription
    if not current_user.is_admin:
        # Import here to avoid circular import
        from app.auth.dependencies import get_subscription_active
        get_subscription_active(current_user=current_user, db=db)
    
    interview = interview_service.get_interview_by_id(db=db, interview_id=interview_id)
    if not interview:
        raise HTTPException(
            status_code=404,
            detail="Interview not found",
        )
    
    # Ensure user can only update their own interviews unless they're an admin
    if interview.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to update this interview")
    
    interview = interview_service.update_interview(
        db=db, db_interview=interview, interview_in=interview_in
    )
    return interview

@router.post("/{interview_id}/credentials")
def generate_credentials(
    *,
    db: Session = Depends(get_db),
    interview_id: str,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Generate ephemeral session credentials for the interview
    """
    # Check if user is not admin, then verify subscription
    if not current_user.is_admin:
        # Import here to avoid circular import
        from app.auth.dependencies import get_subscription_active
        get_subscription_active(current_user=current_user, db=db)
    
    interview = interview_service.get_interview_by_id(db=db, interview_id=interview_id)
    if not interview:
        raise HTTPException(
            status_code=404,
            detail="Interview not found",
        )
    
    # Ensure user can only get credentials for their own interviews unless they're an admin
    if interview.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to access this interview")
    
    # Generate TURN credentials and session token
    turn_credentials = credential_service.generate_turn_credentials(
        username=str(current_user.id)
    )
    
    session_token = credential_service.generate_session_token(
        interview_id=str(interview.id),
        user_id=str(current_user.id)
    )
    
    return {
        "turn_credentials": turn_credentials,
        "session_token": session_token,
    }

@router.delete("/{interview_id}", status_code=204)
def delete_interview(
    *,
    db: Session = Depends(get_db),
    interview_id: str,
    current_user: User = Depends(get_current_user),
) -> None:
    """
    Delete an interview
    """
    interview = interview_service.get_interview_by_id(db=db, interview_id=interview_id)
    if not interview:
        raise HTTPException(
            status_code=404,
            detail="Interview not found",
        )
    
    # Ensure user can only delete their own interviews unless they're an admin
    if interview.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to delete this interview")
    
    interview_service.delete_interview(db=db, interview_id=interview_id)
    return None

@router.get("/{interview_id}/questions/{question_number}/token", response_model=Dict[str, Any])
def generate_question_session_token(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    interview_id: UUID = Path(...),
    question_number: int = Path(..., ge=1, le=4),
    ttl: int = Query(3600, ge=300, le=7200)
) -> Any:
    """
    Generate a realtime session token for a specific interview question
    
    Args:
        interview_id: The ID of the interview
        question_number: The question number (1-4)
        ttl: Time to live in seconds (default: 1 hour, min: 5 min, max: 2 hours)
    
    Returns:
        Session token object compatible with OpenAI's Realtime API
    """
    # Get the interview
    interview = interview_service.get_interview_by_id(db, interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    # Verify user owns the interview or is admin
    if not current_user.is_admin and interview.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this interview")
    
    # Check if user is not admin, then verify subscription
    if not current_user.is_admin:
        get_subscription_active(current_user=current_user, db=db)
    
    # Check if the interview is in progress
    if interview.status != "in-progress":
        raise HTTPException(status_code=400, detail="Interview is not in progress")
    
    # Get current question from progress data
    current_question = interview.progress_data.get("current_question", 1) if interview.progress_data else 1
    
    # Only allow access to current or previous questions
    if question_number > current_question:
        raise HTTPException(status_code=400, detail="Cannot access future questions")
    
    # Generate the session token
    try:
        session_token = credential_service.generate_session_token_for_question(
            db=db,
            interview_id=interview_id,
            user_id=current_user.id,
            question_number=question_number,
            ttl=ttl
        )
        return session_token
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) 