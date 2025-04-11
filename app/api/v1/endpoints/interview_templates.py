from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, get_subscription_active
from app.db.session import get_db
from app.models.user import User
from app.schemas.interview_template import (
    InterviewTemplate,
    InterviewTemplateCreate,
    InterviewTemplateList,
    InterviewTemplateUpdate,
)
from app.services import interview_template as template_service

router = APIRouter()

@router.get("/", response_model=List[InterviewTemplateList])
def read_templates(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: bool = Depends(get_subscription_active),
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

@router.get("/{template_id}", response_model=InterviewTemplate)
def read_template(
    *,
    db: Session = Depends(get_db),
    template_id: str,
    current_user: User = Depends(get_current_user),
    _: bool = Depends(get_subscription_active),
) -> Any:
    """
    Get template by ID
    """
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
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Create new template (admin only in a real system)
    """
    # In a real system, you would check if the user is an admin
    template = template_service.create_template(db=db, template_in=template_in)
    return template

@router.put("/{template_id}", response_model=InterviewTemplate)
def update_template(
    *,
    db: Session = Depends(get_db),
    template_id: str,
    template_in: InterviewTemplateUpdate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Update a template (admin only in a real system)
    """
    template = template_service.get_template_by_id(db=db, template_id=template_id)
    if not template:
        raise HTTPException(
            status_code=404,
            detail="Template not found",
        )
    
    # In a real system, you would check if the user is an admin
    template = template_service.update_template(
        db=db, db_template=template, template_in=template_in
    )
    return template 