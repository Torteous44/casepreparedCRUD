from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict

# Shared properties
class InterviewTemplateBase(BaseModel):
    case_type: str
    lead_type: str
    difficulty: str
    company: Optional[str] = None
    industry: Optional[str] = None
    prompt: str
    structure: Dict[str, Any]
    image_url: Optional[str] = None
    version: str = "1.0"

# Properties to receive via API on creation
class InterviewTemplateCreate(InterviewTemplateBase):
    pass

# Properties to receive via API on update
class InterviewTemplateUpdate(BaseModel):
    case_type: Optional[str] = None
    lead_type: Optional[str] = None
    difficulty: Optional[str] = None
    company: Optional[str] = None
    industry: Optional[str] = None
    prompt: Optional[str] = None
    structure: Optional[Dict[str, Any]] = None
    image_url: Optional[str] = None
    version: Optional[str] = None

# Properties shared by models stored in DB
class InterviewTemplateInDBBase(InterviewTemplateBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Properties to return to client
class InterviewTemplate(InterviewTemplateInDBBase):
    pass

# Properties stored in DB
class InterviewTemplateInDB(InterviewTemplateInDBBase):
    pass

# Properties for template list with minimal data
class InterviewTemplateList(BaseModel):
    id: UUID
    case_type: str
    lead_type: str
    difficulty: str
    company: Optional[str] = None
    industry: Optional[str] = None
    image_url: Optional[str] = None
    version: str

    model_config = ConfigDict(from_attributes=True) 