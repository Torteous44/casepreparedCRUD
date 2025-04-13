from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class AnalysisCategory(BaseModel):
    """Category of analysis with title and description"""
    title: str = Field(..., description="Title/header of the analysis category")
    description: str = Field(..., description="Detailed description of the analysis")


class TranscriptAnalysisRequest(BaseModel):
    """Request model for transcript analysis"""
    transcript: str = Field(..., description="The transcript text to analyze")


class TranscriptAnalysisResponse(BaseModel):
    """Response model for transcript analysis results"""
    structure: AnalysisCategory = Field(..., description="Structure: Evaluated on problem solving approach")
    communication: AnalysisCategory = Field(..., description="Communication: Presence, clarity and impact")
    hypothesis_driven_approach: AnalysisCategory = Field(..., description="Hypothesis-Driven Approach: Early structuring")
    qualitative_analysis: AnalysisCategory = Field(..., description="Qualitative Analysis: Business judgment and thinking")
    adaptability: AnalysisCategory = Field(..., description="Adaptability: Responding to information and guidance") 