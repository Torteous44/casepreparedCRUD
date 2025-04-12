import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.db.session import Base

class InterviewTemplate(Base):
    __tablename__ = "interview_templates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_type = Column(String, nullable=False)
    lead_type = Column(String, nullable=False)
    difficulty = Column(String, nullable=False)
    company = Column(String, nullable=True)
    industry = Column(String, nullable=True)
    prompt = Column(Text, nullable=False)
    structure = Column(JSONB, nullable=False)  # Contains question prompts and context for 4 questions
    image_url = Column(String, nullable=True)  # URL to an image for the template
    version = Column(String, default="1.0")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) 