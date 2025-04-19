# Demo API Endpoints Documentation

This document provides an overview of the demo endpoints available in the API. These endpoints allow users to access and interact with demo interview case studies.

## Available Demo Case Types

The API supports three types of demo case interviews:
- `market-entry`: CoffeeChain Market Entry Strategy
- `profitability`: TechNow Profitability Challenge
- `merger`: HealthFirst Acquisition Decision

## Endpoints

### List Demo Templates

```
GET /api/v1/demo/templates
```

Returns a list of all available demo interview templates with basic information.

**Response**: Array of template objects containing ID, case type, title, description, etc.

### Get Specific Template

```
GET /api/v1/demo/templates/{template_id}
```

Returns detailed information about a specific template by ID.

**Parameters**:
- `template_id`: UUID of the template

**Response**: Complete template object with all details including questions.

### Get Demo Interview

```
GET /api/v1/demo/interviews/{case_type}
```

Gets or initializes a demo interview session by case type.

**Parameters**:
- `case_type`: Type of case (market-entry, profitability, or merger)

**Response**: Interview object with progress tracking and template info.

### Get TURN Credentials

```
GET /api/v1/demo/turn-credentials
```

Gets TURN server credentials for WebRTC in demo mode, used for real-time audio/video communication.

**Response**: Credentials object with username, TTL, and ICE servers.

### Get Question Token

```
GET /api/v1/demo/interviews/{case_type}/questions/{question_number}/token
```

Generates a token for accessing a specific interview question.

**Parameters**:
- `case_type`: Type of case
- `question_number`: Question number (1-4)
- `ttl`: Optional token time-to-live in seconds (default: 3600)

**Response**: Session token object for authenticating with the interviewer AI.

### Complete Question

```
POST /api/v1/demo/interviews/complete-question
```

Marks a question as complete and advances to the next question.

**Request Body**:
```json
{
  "case_type": "string",
  "question_number": integer
}
```

**Response**: Updated interview object with new progress status.

### Reset Interview

```
POST /api/v1/demo/reset/{case_type}
```

Resets progress for a specific interview case type.

**Parameters**:
- `case_type`: Type of case to reset

**Response**: Reset interview object with initial progress state.

### Get Direct Token

```
GET /api/v1/demo/direct-token/{case_type}/{question_number}
```

Generates a direct OpenAI token with minimal processing for frontend compatibility.

**Parameters**:
- `case_type`: Type of case
- `question_number`: Question number (1-4)
- `ttl`: Optional token time-to-live in seconds (default: 3600)

**Response**: Simplified token object containing just the token and expiration.

## Data Structures

### Demo Templates

Each demo template includes:
- Basic metadata (ID, title, description, etc.)
- Case information (type, difficulty, industry)
- A set of 4 interview questions with prompts

### Interview Progress Tracking

The API tracks interview progress with these fields:
- `current_question`: The current question number (1-4)
- `questions_completed`: Array of completed question numbers
- `status`: Interview status (in-progress or completed)
- `started_at`: Timestamp when the interview started
- `completed_at`: Timestamp when the interview was completed (if applicable)

## Example Flow

1. Fetch available templates with `GET /api/v1/demo/templates`
2. Initialize interview with `GET /api/v1/demo/interviews/{case_type}`
3. Get TURN credentials with `GET /api/v1/demo/turn-credentials`
4. Get token for question 1 with `GET /api/v1/demo/interviews/{case_type}/questions/1/token`
5. Complete question 1 with `POST /api/v1/demo/interviews/complete-question`
6. Continue with questions 2-4
7. Reset progress if needed with `POST /api/v1/demo/reset/{case_type}` 