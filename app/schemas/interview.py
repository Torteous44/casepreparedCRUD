from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, ConfigDict

# Shared properties
class InterviewBase(BaseModel):
    user_id: UUID
    template_id: UUID
    status: str = "in-progress"
    progress_data: Optional[Dict[str, Any]] = None

# Properties to receive via API on creation
class InterviewCreate(BaseModel):
    template_id: UUID

# Properties to receive via API on update
class InterviewUpdate(BaseModel):
    status: Optional[str] = None
    progress_data: Optional[Dict[str, Any]] = None
    completed_at: Optional[datetime] = None

# Properties shared by models stored in DB
class InterviewInDBBase(InterviewBase):
    id: UUID
    started_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

# Properties to return to client
class Interview(InterviewInDBBase):
    pass

# Properties stored in DB
class InterviewInDB(InterviewInDBBase):
    pass

# Interview with Template Data
class InterviewWithTemplate(Interview):
    template: Dict[str, Any] = None 