from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, get_subscription_active, get_admin_user, get_admin_with_subscription
from app.db.session import get_db
from app.models.user import User
from app.schemas.interview_template import (
    InterviewTemplate,
    InterviewTemplateCreate,
    InterviewTemplateList,
    InterviewTemplateUpdate,
    Question,
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
    current_user: User = Depends(get_admin_user),
    _: bool = Depends(get_admin_with_subscription),
) -> Any:
    """
    Create new template (admin only)
    Admin endpoint protected with admin password
    """
    template = template_service.create_template(db=db, template_in=template_in)
    return template

@router.post("/admin", response_model=InterviewTemplate)
def create_template_admin(
    *,
    db: Session = Depends(get_db),
    case_type: str = Body(...),
    lead_type: str = Body(...),
    difficulty: str = Body(...),
    company: Optional[str] = Body(None),
    industry: Optional[str] = Body(None),
    prompt: str = Body(...),
    image_url: Optional[str] = Body(None),
    version: Optional[str] = Body("1.0"),
    question1: Question = Body(...),
    question2: Question = Body(...),
    question3: Question = Body(...),
    question4: Question = Body(...),
    current_user: User = Depends(get_admin_user),
    _: bool = Depends(get_admin_with_subscription),
) -> Any:
    """
    Admin endpoint for creating a new template with structured questions
    Admin endpoint protected with admin password
    """
    # Construct the template structure
    structure = {
        "question1": {
            "question": question1.question,
            "context": question1.context
        },
        "question2": {
            "question": question2.question,
            "context": question2.context
        },
        "question3": {
            "question": question3.question,
            "context": question3.context
        },
        "question4": {
            "question": question4.question,
            "context": question4.context
        }
    }
    
    # Create the template
    template_in = InterviewTemplateCreate(
        case_type=case_type,
        lead_type=lead_type,
        difficulty=difficulty,
        company=company,
        industry=industry,
        prompt=prompt,
        image_url=image_url,
        structure=structure,
        version=version or "1.0"
    )
    
    template = template_service.create_template(db=db, template_in=template_in)
    return template

@router.put("/{template_id}", response_model=InterviewTemplate)
def update_template(
    *,
    db: Session = Depends(get_db),
    template_id: str,
    template_in: InterviewTemplateUpdate,
    current_user: User = Depends(get_admin_user),
    _: bool = Depends(get_admin_with_subscription),
) -> Any:
    """
    Update a template (admin only)
    Admin endpoint protected with admin password
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

@router.delete("/{template_id}", response_model=Dict[str, bool])
def delete_template(
    *,
    db: Session = Depends(get_db),
    template_id: str,
    current_user: User = Depends(get_admin_user),
    _: bool = Depends(get_admin_with_subscription),
) -> Any:
    """
    Delete a template (admin only)
    Admin endpoint protected with admin password
    """
    template = template_service.get_template_by_id(db=db, template_id=template_id)
    if not template:
        raise HTTPException(
            status_code=404,
            detail="Template not found",
        )
    
    success = template_service.delete_template(db=db, template_id=template_id)
    return {"success": success} 