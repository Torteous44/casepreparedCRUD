# Demo Interview API Documentation

This document describes the unprotected demo API endpoints for trying out the case interview feature without authentication or subscription.

## Demo Templates and Interviews

The demo provides 3 hardcoded case interview templates covering different business scenarios:

1. **Market Entry** - CoffeeChain Market Entry Strategy
2. **Profitability** - TechNow Profitability Challenge 
3. **Merger & Acquisition** - HealthFirst Acquisition Decision

## API Endpoints

### List Demo Templates

```
GET /api/v1/demo/templates
```

Returns a list of all available demo interview templates.

### Get Demo Template

```
GET /api/v1/demo/templates/{template_id}
```

Returns a specific demo template by ID.

### Get Demo Interview

```
GET /api/v1/demo/interviews/{case_type}
```

Get or initialize a demo interview for a specific case type (market-entry, profitability, or merger).

### Get TURN Credentials (WebRTC)

```
GET /api/v1/demo/turn-credentials
```

Get TURN server credentials for WebRTC connections in demo mode (no authentication required).

### Get Question Session Token

```
GET /api/v1/demo/interviews/{case_type}/questions/{question_number}/token?ttl=3600
```

Generate a session token for a specific demo interview question. This token can be used to connect to OpenAI's realtime API.

Parameters:
- `case_type`: The demo case type (market-entry, profitability, or merger)
- `question_number`: The question number (1-4)
- `ttl`: Token time-to-live in seconds (default: 3600, min: 300, max: 7200)

### Complete Question

```
POST /api/v1/demo/interviews/complete-question
```

Mark a question as complete and advance to the next question. This will update the interview progress.

Request body:
```json
{
  "case_type": "market-entry",
  "question_number": 1
}
```

### Reset Demo Interview

```
POST /api/v1/demo/reset/{case_type}
```

Reset progress for a specific demo interview.

## Example Usage Flow

1. Get the list of available templates: `GET /api/v1/demo/templates`
2. Choose a template and start an interview: `GET /api/v1/demo/interviews/market-entry`
3. Get TURN credentials for WebRTC: `GET /api/v1/demo/turn-credentials`
4. Get a session token for the first question: `GET /api/v1/demo/interviews/market-entry/questions/1/token`
5. After completing the question, mark it as complete: `POST /api/v1/demo/interviews/complete-question` with appropriate body
6. Continue with the next question: `GET /api/v1/demo/interviews/market-entry/questions/2/token`
7. Repeat until all questions are completed
8. If needed, reset the interview: `POST /api/v1/demo/reset/market-entry`

## Notes

- Demo interviews maintain their progress state in memory, which will be lost on server restart
- All demo endpoints are unprotected and do not require authentication or subscription
- Each demo template has exactly 4 questions 