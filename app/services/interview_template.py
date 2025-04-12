from typing import List, Optional, Dict, Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.interview_template import InterviewTemplate
from app.schemas.interview_template import InterviewTemplateCreate, InterviewTemplateUpdate

def get_template_by_id(db: Session, template_id: UUID) -> Optional[InterviewTemplate]:
    return db.query(InterviewTemplate).filter(InterviewTemplate.id == template_id).first()

def get_templates(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    filters: Optional[Dict[str, Any]] = None
) -> List[InterviewTemplate]:
    query = db.query(InterviewTemplate)
    
    if filters:
        if filters.get("case_type"):
            query = query.filter(InterviewTemplate.case_type == filters["case_type"])
        if filters.get("lead_type"):
            query = query.filter(InterviewTemplate.lead_type == filters["lead_type"])
        if filters.get("difficulty"):
            query = query.filter(InterviewTemplate.difficulty == filters["difficulty"])
        if filters.get("company"):
            query = query.filter(InterviewTemplate.company == filters["company"])
        if filters.get("industry"):
            query = query.filter(InterviewTemplate.industry == filters["industry"])
    
    return query.offset(skip).limit(limit).all()

def create_template(db: Session, template_in: InterviewTemplateCreate) -> InterviewTemplate:
    db_template = InterviewTemplate(
        case_type=template_in.case_type,
        lead_type=template_in.lead_type,
        difficulty=template_in.difficulty,
        company=template_in.company,
        industry=template_in.industry,
        prompt=template_in.prompt,
        image_url=template_in.image_url,
        structure=template_in.structure,
        version=template_in.version,
    )
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template

def update_template(
    db: Session, db_template: InterviewTemplate, template_in: InterviewTemplateUpdate
) -> InterviewTemplate:
    update_data = template_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_template, field, value)
    
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template

def delete_template(db: Session, template_id: UUID) -> bool:
    template = get_template_by_id(db, template_id)
    if template:
        db.delete(template)
        db.commit()
        return True
    return False 