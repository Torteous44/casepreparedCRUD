from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.interview import Interview
from app.schemas.interview import InterviewCreate, InterviewUpdate

def get_interview_by_id(db: Session, interview_id: UUID) -> Optional[Interview]:
    return db.query(Interview).filter(Interview.id == interview_id).first()

def get_interviews_by_user_id(
    db: Session, user_id: UUID, skip: int = 0, limit: int = 100
) -> List[Interview]:
    return db.query(Interview).filter(Interview.user_id == user_id).offset(skip).limit(limit).all()

def get_interviews(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    filters: Optional[Dict[str, Any]] = None
) -> List[Interview]:
    query = db.query(Interview)
    
    if filters:
        if filters.get("user_id"):
            query = query.filter(Interview.user_id == filters["user_id"])
        if filters.get("template_id"):
            query = query.filter(Interview.template_id == filters["template_id"])
        if filters.get("status"):
            query = query.filter(Interview.status == filters["status"])
    
    return query.offset(skip).limit(limit).all()

def create_interview(db: Session, interview_in: InterviewCreate, user_id: UUID) -> Interview:
    db_interview = Interview(
        user_id=user_id,
        template_id=interview_in.template_id,
        status="in-progress",
        progress_data={"current_question": 1, "questions_completed": []},
    )
    db.add(db_interview)
    db.commit()
    db.refresh(db_interview)
    return db_interview

def update_interview(
    db: Session, db_interview: Interview, interview_in: InterviewUpdate
) -> Interview:
    update_data = interview_in.dict(exclude_unset=True)
    
    # If we're completing the interview, set the completed_at timestamp
    if update_data.get("status") == "completed" and not db_interview.completed_at:
        update_data["completed_at"] = datetime.utcnow()
    
    for field, value in update_data.items():
        setattr(db_interview, field, value)
    
    db.add(db_interview)
    db.commit()
    db.refresh(db_interview)
    return db_interview

def delete_interview(db: Session, interview_id: UUID) -> bool:
    interview = get_interview_by_id(db, interview_id)
    if interview:
        db.delete(interview)
        db.commit()
        return True
    return False

def get_in_progress_interview_by_template(
    db: Session, user_id: UUID, template_id: UUID
) -> Optional[Interview]:
    """
    Get the most recent in-progress interview for a specific user and template
    """
    return db.query(Interview).filter(
        Interview.user_id == user_id,
        Interview.template_id == template_id,
        Interview.status == "in-progress"
    ).order_by(Interview.started_at.desc()).first() 