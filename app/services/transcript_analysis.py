import json
from typing import Dict, Any
import os
import logging
from openai import OpenAI

from app.schemas.transcript_analysis import TranscriptAnalysisResponse, AnalysisCategory

# Set up logging
logger = logging.getLogger(__name__)

class AnalysisError(Exception):
    """Exception raised for errors in the analysis process."""
    pass

def analyze_transcript(transcript: str) -> TranscriptAnalysisResponse:
    """
    Analyze an interview transcript using OpenAI.
    
    Args:
        transcript: The interview transcript text
        
    Returns:
        TranscriptAnalysisResponse object with analysis categories
    
    Raises:
        AnalysisError: If there's an error calling the OpenAI API
    """
    # Initialize OpenAI client with API key
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise AnalysisError("OpenAI API key not found in environment variables")
    
    client = OpenAI(api_key=api_key)
    
    # Create prompt for analysis
    prompt = f"""
    Analyze the following interview transcript and provide feedback in these five categories:
    
    1. Structure: Evaluate the problem-solving approach
    2. Communication: Assess presence, clarity and impact
    3. Hypothesis-Driven Approach: Evaluate early structuring and hypothesis formation
    4. Qualitative Analysis: Assess business judgment and thinking
    5. Adaptability: Evaluate how they respond to information and guidance
    
    For each category, provide:
    - A title/header that summarizes what they did well or need to improve
    - A detailed description of your analysis
    
    Transcript:
    {transcript}
    
    Format your response as a JSON object with the following structure:
    {{
        "structure": {{
            "title": "Title summarizing structure strengths/weaknesses",
            "description": "Detailed structure analysis"
        }},
        "communication": {{
            "title": "Title summarizing communication strengths/weaknesses",
            "description": "Detailed communication analysis"
        }},
        "hypothesis_driven_approach": {{
            "title": "Title summarizing hypothesis approach strengths/weaknesses",
            "description": "Detailed hypothesis approach analysis"
        }},
        "qualitative_analysis": {{
            "title": "Title summarizing qualitative analysis strengths/weaknesses",
            "description": "Detailed qualitative analysis assessment"
        }},
        "adaptability": {{
            "title": "Title summarizing adaptability strengths/weaknesses",
            "description": "Detailed adaptability analysis"
        }}
    }}
    
    Ensure you provide specific, actionable feedback for each category.
    """
    
    try:
        # Call OpenAI API with GPT-4o-mini
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "You are an expert interview coach that provides detailed, structured feedback on interview performance."},
                {"role": "user", "content": prompt}
            ]
        )
        
        # Extract JSON content from the response
        analysis_text = response.choices[0].message.content
        analysis_data = json.loads(analysis_text)
        
        # Parse the data into our Pydantic model
        return TranscriptAnalysisResponse(
            structure=AnalysisCategory(
                title=analysis_data["structure"]["title"],
                description=analysis_data["structure"]["description"]
            ),
            communication=AnalysisCategory(
                title=analysis_data["communication"]["title"],
                description=analysis_data["communication"]["description"]
            ),
            hypothesis_driven_approach=AnalysisCategory(
                title=analysis_data["hypothesis_driven_approach"]["title"],
                description=analysis_data["hypothesis_driven_approach"]["description"]
            ),
            qualitative_analysis=AnalysisCategory(
                title=analysis_data["qualitative_analysis"]["title"],
                description=analysis_data["qualitative_analysis"]["description"]
            ),
            adaptability=AnalysisCategory(
                title=analysis_data["adaptability"]["title"],
                description=analysis_data["adaptability"]["description"]
            )
        )
        
    except Exception as e:
        logger.error(f"Error analyzing transcript: {str(e)}")
        raise AnalysisError(f"Error analyzing transcript: {str(e)}") 