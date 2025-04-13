# Transcript Analysis Endpoint Documentation

## Overview

The Transcript Analysis endpoint provides AI-powered feedback on interview transcripts. It uses OpenAI's GPT-4o-mini model to analyze the interview transcript text and generate structured feedback in five key categories essential for consulting interview performance.

## Endpoint Details

- **URL**: `/api/v1/transcript-analysis/`
- **Method**: `POST`
- **Authentication**: Required (JWT Token)
- **Subscription**: Required (Active subscription needed)

## Request Format

```json
{
  "transcript": "Full transcript text of the interview goes here..."
}
```

### Request Parameters

| Parameter  | Type   | Required | Description                           |
|------------|--------|----------|---------------------------------------|
| transcript | string | Yes      | The complete text of the interview transcript to analyze |

## Response Format

```json
{
  "structure": {
    "title": "Clear Framework with Missing Quantification",
    "description": "You demonstrated a good problem-solving approach by using a structured framework to break down the issue. However, your analysis lacked quantitative elements which would have strengthened your conclusions."
  },
  "communication": {
    "title": "Confident Delivery but Technical Jargon Heavy",
    "description": "Your communication style was confident and articulate. However, you relied too heavily on technical jargon which might confuse clients. Try simplifying complex concepts for better clarity."
  },
  "hypothesis_driven_approach": {
    "title": "Strong Initial Hypotheses Formation",
    "description": "You excellently formed early hypotheses about potential causes and tested them systematically. This demonstrated strong strategic thinking and allowed you to narrow down possibilities efficiently."
  },
  "qualitative_analysis": {
    "title": "Insightful Business Context Missing Market Trends",
    "description": "Your qualitative analysis showed good business judgment in understanding internal factors, but lacked consideration of broader market trends and competitive dynamics that would impact decision-making."
  },
  "adaptability": {
    "title": "Receptive to Feedback but Slow to Pivot",
    "description": "You were open to feedback and incorporated suggestions, but sometimes hesitated to change direction when new information contradicted your initial approach. Faster pivoting would improve your adaptability."
  }
}
```

### Response Fields

| Field                     | Type   | Description                                                            |
|---------------------------|--------|------------------------------------------------------------------------|
| structure                 | object | Feedback on problem-solving approach and structure                     |
| structure.title           | string | Concise summary of structure strengths/weaknesses                      |
| structure.description     | string | Detailed analysis of problem-solving approach                          |
| communication             | object | Feedback on presence, clarity and impact                               |
| communication.title       | string | Concise summary of communication strengths/weaknesses                  |
| communication.description | string | Detailed analysis of communication skills                              |
| hypothesis_driven_approach| object | Feedback on early structuring and hypothesis formation                 |
| hypothesis_driven_approach.title | string | Concise summary of hypothesis approach strengths/weaknesses     |
| hypothesis_driven_approach.description | string | Detailed analysis of hypothesis formation and testing     |
| qualitative_analysis      | object | Feedback on business judgment and thinking                             |
| qualitative_analysis.title | string | Concise summary of business analysis strengths/weaknesses             |
| qualitative_analysis.description | string | Detailed assessment of business judgment                        |
| adaptability              | object | Feedback on responding to information and guidance                     |
| adaptability.title        | string | Concise summary of adaptability strengths/weaknesses                   |
| adaptability.description  | string | Detailed analysis of adaptability during the interview                 |

## Error Responses

| Status Code | Description                                    | Possible Solution                                 |
|-------------|------------------------------------------------|--------------------------------------------------|
| 401         | Unauthorized - Missing or invalid token        | Ensure valid authentication token is provided     |
| 403         | Forbidden - Subscription inactive              | Verify user has an active subscription            |
| 500         | Internal Server Error - Analysis failed        | Check server logs for OpenAI API error details    |

## Usage Example

### cURL

```bash
curl -X POST "https://api.caseprepared.com/api/v1/transcript-analysis/" \
     -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     -H "Content-Type: application/json" \
     -d '{
           "transcript": "Interviewer: So today we're going to discuss a case about a retail company experiencing declining sales...[full transcript]"
         }'
```

### JavaScript (Fetch)

```javascript
const analyzeTranscript = async (token, transcript) => {
  try {
    const response = await fetch('https://api.caseprepared.com/api/v1/transcript-analysis/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ transcript }),
    });
    
    if (!response.ok) {
      throw new Error(`Error: ${response.status}`);
    }
    
    const analysisData = await response.json();
    return analysisData;
  } catch (error) {
    console.error('Failed to analyze transcript:', error);
    throw error;
  }
};
```

## Notes

- The analysis is performed using OpenAI's GPT-4o-mini model
- Each analysis generates new feedback based on the specific transcript content
- Longer or more complex transcripts may take more processing time
- The API has rate limits based on your subscription tier 