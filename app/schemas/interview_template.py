from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict, validator

# Question structure
class Question(BaseModel):
    question: str
    context: str

# Structure for 4 questions
class TemplateStructure(BaseModel):
    question1: Question
    question2: Question
    question3: Question
    question4: Question

# Shared properties
class InterviewTemplateBase(BaseModel):
    case_type: str
    lead_type: str
    difficulty: str
    company: Optional[str] = None
    industry: Optional[str] = None
    prompt: str
    image_url: Optional[str] = None
    structure: Dict[str, Any]
    version: str = "1.0"
    
    @validator('structure')
    def validate_structure(cls, v):
        """Validate that the structure contains 4 questions with context"""
        try:
            # Try to parse the structure with our Question model
            for q_num in range(1, 5):
                q_key = f"question{q_num}"
                if q_key not in v:
                    raise ValueError(f"Missing {q_key} in structure")
                
                question_data = v[q_key]
                if not isinstance(question_data, dict):
                    raise ValueError(f"{q_key} must be an object")
                
                if "question" not in question_data:
                    raise ValueError(f"Missing 'question' in {q_key}")
                
                if "context" not in question_data:
                    raise ValueError(f"Missing 'context' in {q_key}")
                
        except Exception as e:
            raise ValueError(f"Invalid structure format: {str(e)}")
        
        return v

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
    image_url: Optional[str] = None
    structure: Optional[Dict[str, Any]] = None
    version: Optional[str] = None
    
    @validator('structure')
    def validate_structure(cls, v):
        if v is None:
            return v
            
        try:
            # Try to parse the structure with our Question model
            for q_num in range(1, 5):
                q_key = f"question{q_num}"
                if q_key not in v:
                    raise ValueError(f"Missing {q_key} in structure")
                
                question_data = v[q_key]
                if not isinstance(question_data, dict):
                    raise ValueError(f"{q_key} must be an object")
                
                if "question" not in question_data:
                    raise ValueError(f"Missing 'question' in {q_key}")
                
                if "context" not in question_data:
                    raise ValueError(f"Missing 'context' in {q_key}")
                
        except Exception as e:
            raise ValueError(f"Invalid structure format: {str(e)}")
        
        return v

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