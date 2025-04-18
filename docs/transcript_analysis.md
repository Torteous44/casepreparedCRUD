# Transcript Analysis API

## Endpoint

```
POST /api/v1/transcript-analysis/
```

## Description

Analyzes an interview transcript and provides structured feedback using OpenAI's GPT-4o-mini model.

## Authentication

Requires authentication. Non-admin users must have an active subscription.

## Request Body

```json
{
  "transcript": "The interview transcript text to analyze"
}
```

## Response

```json
{
  "structure": {
    "title": "Title summarizing structure strengths/weaknesses",
    "description": "Detailed structure analysis"
  },
  "communication": {
    "title": "Title summarizing communication strengths/weaknesses",
    "description": "Detailed communication analysis"
  },
  "hypothesis_driven_approach": {
    "title": "Title summarizing hypothesis approach strengths/weaknesses",
    "description": "Detailed hypothesis approach analysis"
  },
  "qualitative_analysis": {
    "title": "Title summarizing qualitative analysis strengths/weaknesses",
    "description": "Detailed qualitative analysis assessment"
  },
  "adaptability": {
    "title": "Title summarizing adaptability strengths/weaknesses",
    "description": "Detailed adaptability analysis"
  }
}
```

## Analysis Categories

1. **Structure**: Evaluation of problem-solving approach
2. **Communication**: Assessment of presence, clarity, and impact
3. **Hypothesis-Driven Approach**: Evaluation of early structuring
4. **Qualitative Analysis**: Assessment of business judgment and thinking
5. **Adaptability**: Evaluation of response to information and guidance

## Error Handling

- `500 Internal Server Error`: If there's an error with the OpenAI API or analysis process
- `403 Forbidden`: If the user doesn't have an active subscription (non-admin users)

## Example Usage

```python
import requests

url = "http://localhost:8000/api/v1/etc etc"
headers = {
    "Authorization": "Bearer YOUR_ACCESS_TOKEN",
    "Content-Type": "application/json"
}
data = {
    "transcript": "Your interview transcript text here..."
}

response = requests.post(url, json=data, headers=headers)
analysis = response.json()
``` 