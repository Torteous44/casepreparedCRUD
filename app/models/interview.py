import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.db.session import Base

class Interview(Base):
    __tablename__ = "interviews"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    template_id = Column(UUID(as_uuid=True), ForeignKey("interview_templates.id"), nullable=False)
    status = Column(String, default="in-progress")  # "in-progress", "completed", etc.
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    progress_data = Column(JSONB, nullable=True)  # Track minimal progress like current_question, etc.
    
    # Relationships
    user = relationship("User", backref="interviews")
    template = relationship("InterviewTemplate", back_populates="interviews") 