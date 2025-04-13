from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, get_subscription_active
from app.db.session import get_db
from app.models.user import User
from app.schemas.interview import Interview, InterviewCreate, InterviewUpdate, InterviewWithTemplate
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

@router.get("/history", response_model=List[Dict[str, Any]])
def read_interview_history(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = Query(None),
) -> Any:
    """
    Retrieve user's interview history with detailed progress information
    
    Optional status filter can be "completed", "in-progress", or left empty for all interviews
    """
    # Check if user is not admin, then verify subscription
    if not current_user.is_admin:
        get_subscription_active(current_user=current_user, db=db)
    
    # Get interviews for the current user with optional status filter
    filters = {"user_id": current_user.id}
    if status:
        filters["status"] = status
    
    interviews = interview_service.get_interviews(
        db=db, skip=skip, limit=limit, filters=filters
    )
    
    # Get template information for each interview
    result = []
    for interview in interviews:
        template = template_service.get_template_by_id(db=db, template_id=interview.template_id)
        
        # Skip if template doesn't exist (shouldn't happen but for safety)
        if not template:
            continue
            
        # Build response with interview, progress, and template details
        interview_data = {
            "id": str(interview.id),
            "template_id": str(interview.template_id),
            "template_title": template.title or f"{template.case_type} - {template.company or template.industry}",
            "template_info": {
                "case_type": template.case_type,
                "lead_type": template.lead_type,
                "difficulty": template.difficulty,
                "company": template.company,
                "industry": template.industry,
            },
            "status": interview.status,
            "started_at": interview.started_at,
            "completed_at": interview.completed_at,
            "progress_data": interview.progress_data or {},
            "questions_completed": len(interview.progress_data.get("questions_completed", [])) if interview.progress_data else 0,
            "total_questions": 4,  # Hardcoded as templates have 4 questions per the schema
        }
        
        result.append(interview_data)
    
    return result

@router.post("/", response_model=Interview)
def create_interview(
    *,
    db: Session = Depends(get_db),
    interview_in: InterviewCreate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Create new interview session or retrieve existing in-progress interview
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
    
    # Check if there's an existing in-progress interview for this template
    existing_interview = interview_service.get_in_progress_interview_by_template(
        db=db, user_id=current_user.id, template_id=interview_in.template_id
    )
    
    if existing_interview:
        # Return the existing interview instead of creating a new one
        return existing_interview
    
    # If no existing interview, create a new one
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

@router.post("/{interview_id}/questions/{question_number}/complete", response_model=Interview)
def complete_question(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    interview_id: UUID = Path(...),
    question_number: int = Path(..., ge=1, le=4),
) -> Any:
    """
    Mark a question as complete and advance to the next question
    
    Args:
        interview_id: The ID of the interview
        question_number: The question number to mark as complete (1-4)
    
    Returns:
        Updated interview object with the new current question
    """
    # Check if user is not admin, then verify subscription
    if not current_user.is_admin:
        get_subscription_active(current_user=current_user, db=db)
    
    # Get the interview
    interview = interview_service.get_interview_by_id(db, interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    # Verify user owns the interview or is admin
    if not current_user.is_admin and interview.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this interview")
    
    # Check if interview is in progress
    if interview.status != "in-progress":
        raise HTTPException(status_code=400, detail="Interview is not in progress")
    
    # Get progress data (initialize if not existing)
    progress_data = interview.progress_data or {"current_question": 1, "questions_completed": []}
    current_question = progress_data.get("current_question", 1)
    questions_completed = progress_data.get("questions_completed", [])
    
    # Validate the question number
    if question_number != current_question:
        raise HTTPException(status_code=400, detail="Can only complete the current question")
    
    # Mark current question as complete
    if question_number not in questions_completed:
        questions_completed.append(question_number)
    
    # Advance to next question or mark as completed if all questions are done
    next_question = question_number + 1
    
    # Update the progress data
    new_progress_data = {
        "current_question": next_question if next_question <= 4 else 4,
        "questions_completed": questions_completed
    }
    
    # If all questions are completed (there are 4 questions), update status
    interview_update = InterviewUpdate(progress_data=new_progress_data)
    if len(questions_completed) >= 4 and all(q in questions_completed for q in range(1, 5)):
        interview_update.status = "completed"
    
    # Update the interview
    updated_interview = interview_service.update_interview(
        db=db, db_interview=interview, interview_in=interview_update
    )
    
    return updated_interview

@router.get("/template/{template_id}", response_model=Interview)
def get_interview_by_template(
    *,
    db: Session = Depends(get_db),
    template_id: UUID = Path(...),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get existing in-progress interview by template ID or create new one
    """
    # Check if user is not admin, then verify subscription
    if not current_user.is_admin:
        get_subscription_active(current_user=current_user, db=db)
    
    # Verify that the template exists
    template = template_service.get_template_by_id(db=db, template_id=template_id)
    if not template:
        raise HTTPException(
            status_code=404,
            detail="Template not found",
        )
    
    # Check if there's an existing in-progress interview for this template
    existing_interview = interview_service.get_in_progress_interview_by_template(
        db=db, user_id=current_user.id, template_id=template_id
    )
    
    if existing_interview:
        # Return the existing interview
        return existing_interview
    
    # If no existing interview, create a new one
    interview_in = InterviewCreate(template_id=template_id)
    interview = interview_service.create_interview(
        db=db, interview_in=interview_in, user_id=current_user.id
    )
    return interview

@router.get("/{interview_id}/with-template", response_model=InterviewWithTemplate)
def read_interview_with_template(
    *,
    db: Session = Depends(get_db),
    interview_id: UUID = Path(...),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get interview by ID with its full template data
    """
    # Check if user is not admin, then verify subscription
    if not current_user.is_admin:
        get_subscription_active(current_user=current_user, db=db)
    
    # Get the interview
    interview = interview_service.get_interview_by_id(db=db, interview_id=interview_id)
    if not interview:
        raise HTTPException(
            status_code=404,
            detail="Interview not found",
        )
    
    # Ensure user can only access their own interviews unless they're an admin
    if interview.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to access this interview")
    
    # Get the template
    template = template_service.get_template_by_id(db=db, template_id=interview.template_id)
    if not template:
        raise HTTPException(
            status_code=404,
            detail="Interview template not found",
        )
    
    # Create a clean dictionary from the interview
    interview_dict = {
        "id": interview.id,
        "user_id": interview.user_id,
        "template_id": interview.template_id,
        "status": interview.status,
        "progress_data": interview.progress_data,
        "started_at": interview.started_at,
        "completed_at": interview.completed_at
    }
    
    # Create a clean dictionary from the template
    template_dict = {
        "id": template.id,
        "case_type": template.case_type,
        "lead_type": template.lead_type,
        "difficulty": template.difficulty,
        "company": template.company,
        "industry": template.industry,
        "prompt": template.prompt,
        "structure": template.structure,
        "image_url": template.image_url,
        "title": template.title,
        "description_short": template.description_short,
        "description_long": template.description_long,
        "duration": template.duration,
        "version": template.version,
        "created_at": template.created_at,
        "updated_at": template.updated_at
    }
    
    # Attach the template to the interview
    interview_dict["template"] = template_dict
    
    return interview_dict 