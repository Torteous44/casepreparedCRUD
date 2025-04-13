from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, get_subscription_active, get_admin_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.interview_template import (
    InterviewTemplateCreate,
    InterviewTemplateList,
    InterviewTemplateUpdate,
    InterviewTemplate,
    InterviewTemplateWithProgress,
)
from app.services import interview_template as template_service
from app.services import interview as interview_service

router = APIRouter()

@router.get("/", response_model=List[InterviewTemplateList])
def read_templates(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    case_type: Optional[str] = Query(None),
    lead_type: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    company: Optional[str] = Query(None),
    industry: Optional[str] = Query(None),
) -> Any:
    """
    Retrieve templates with optional filtering
    """
    # Check if user is not admin, then verify subscription
    if not current_user.is_admin:
        # Import here to avoid circular import
        from app.auth.dependencies import get_subscription_active
        get_subscription_active(current_user=current_user, db=db)
        
    filters = {}
    if case_type:
        filters["case_type"] = case_type
    if lead_type:
        filters["lead_type"] = lead_type
    if difficulty:
        filters["difficulty"] = difficulty
    if company:
        filters["company"] = company
    if industry:
        filters["industry"] = industry
    
    templates = template_service.get_templates(
        db=db, skip=skip, limit=limit, filters=filters
    )
    return templates

@router.get("/with-progress", response_model=List[InterviewTemplateWithProgress])
def read_templates_with_progress(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    case_type: Optional[str] = Query(None),
    lead_type: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    company: Optional[str] = Query(None),
    industry: Optional[str] = Query(None),
) -> Any:
    """
    Retrieve templates with user's progress data
    
    Returns a list of interview templates enriched with the user's progress
    if they have started or completed any interviews for each template.
    """
    # Check if user is not admin, then verify subscription
    if not current_user.is_admin:
        get_subscription_active(current_user=current_user, db=db)
    
    # Get templates with filtering
    filters = {}
    if case_type:
        filters["case_type"] = case_type
    if lead_type:
        filters["lead_type"] = lead_type
    if difficulty:
        filters["difficulty"] = difficulty
    if company:
        filters["company"] = company
    if industry:
        filters["industry"] = industry
    
    templates = template_service.get_templates(
        db=db, skip=skip, limit=limit, filters=filters
    )
    
    # Get all interviews for the current user
    interviews = interview_service.get_interviews_by_user_id(
        db=db, user_id=current_user.id
    )
    
    # Create a lookup dictionary of interviews by template_id
    # If multiple interviews exist for a template, use the most recent one
    interview_lookup = {}
    for interview in interviews:
        template_id = str(interview.template_id)
        # Only add to lookup if this is the first time seeing this template_id
        # or if this interview is more recent than the one already in the lookup
        if (template_id not in interview_lookup or
            interview.started_at > interview_lookup[template_id].started_at):
            interview_lookup[template_id] = interview
    
    # Enrich templates with interview progress data
    result = []
    for template in templates:
        template_dict = template.__dict__
        template_id = str(template.id)
        
        # Add progress data if this template has an interview
        if template_id in interview_lookup:
            interview = interview_lookup[template_id]
            progress_data = interview.progress_data or {}
            questions_completed = len(progress_data.get("questions_completed", [])) if progress_data else 0
            
            template_dict.update({
                "progress_status": interview.status,
                "progress_data": progress_data,
                "interview_id": interview.id,
                "started_at": interview.started_at,
                "completed_at": interview.completed_at,
                "questions_completed": questions_completed,
                "total_questions": 4,  # Hardcoded as templates have 4 questions per the schema
            })
        else:
            # No interview found for this template
            template_dict.update({
                "progress_status": None,
                "progress_data": None,
                "interview_id": None,
                "started_at": None,
                "completed_at": None,
                "questions_completed": 0,
                "total_questions": 4,
            })
        
        # Use InterviewTemplateWithProgress schema
        result.append(template_dict)
    
    return result

@router.get("/{template_id}", response_model=InterviewTemplate)
def read_template(
    *,
    db: Session = Depends(get_db),
    template_id: str,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get template by ID
    """
    # Check if user is not admin, then verify subscription
    if not current_user.is_admin:
        # Import here to avoid circular import
        from app.auth.dependencies import get_subscription_active
        get_subscription_active(current_user=current_user, db=db)
        
    template = template_service.get_template_by_id(db=db, template_id=template_id)
    if not template:
        raise HTTPException(
            status_code=404,
            detail="Template not found",
        )
    return template

@router.post("/", response_model=InterviewTemplate)
def create_template(
    *,
    db: Session = Depends(get_db),
    template_in: InterviewTemplateCreate,
    admin_user: User = Depends(get_admin_user),  # Only admins can create templates
) -> Any:
    """
    Create new template (admin only)
    """
    template = template_service.create_template(db=db, template_in=template_in)
    return template

@router.put("/{template_id}", response_model=InterviewTemplate)
def update_template(
    *,
    db: Session = Depends(get_db),
    template_id: str,
    template_in: InterviewTemplateUpdate,
    admin_user: User = Depends(get_admin_user),  # Only admins can update templates
) -> Any:
    """
    Update a template (admin only)
    """
    template = template_service.get_template_by_id(db=db, template_id=template_id)
    if not template:
        raise HTTPException(
            status_code=404,
            detail="Template not found",
        )
    
    template = template_service.update_template(
        db=db, db_template=template, template_in=template_in
    )
    return template

@router.delete("/{template_id}", status_code=204)
def delete_template(
    *,
    db: Session = Depends(get_db),
    template_id: str,
    admin_user: User = Depends(get_admin_user),  # Only admins can delete templates
) -> None:
    """
    Delete a template (admin only)
    """
    template = template_service.get_template_by_id(db=db, template_id=template_id)
    if not template:
        raise HTTPException(
            status_code=404,
            detail="Template not found",
        )
    
    success = template_service.delete_template(db=db, template_id=template_id)
    if not success:
        raise HTTPException(
            status_code=400,
            detail="Unable to delete template. It may be referenced by existing interviews."
        )
    return None 