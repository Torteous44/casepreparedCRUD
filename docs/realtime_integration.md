# OpenAI Realtime API Integration

## Overview

CasePrepared integrates with OpenAI's Realtime API to provide dynamic, interactive interview experiences. This document explains how our backend generates and manages ephemeral session tokens for secure, context-aware interactions with OpenAI's GPT-4o Realtime model.

## Architecture

The integration follows a per-question architecture:

1. Each interview question is treated as a separate ephemeral session
2. Session tokens are generated on-demand for each question
3. Tokens are short-lived by design (default: 1 hour)
4. Instructions are dynamically generated based on the specific question context

## Session Token Generation

### Endpoint

```
GET /api/v1/interviews/{interview_id}/questions/{question_number}/token
```

### Authentication

All requests require a valid JWT token in the `Authorization` header.

### Parameters

- `interview_id`: UUID of the interview
- `question_number`: Question number (1-4)
- `ttl`: Optional time-to-live in seconds (default: 3600, min: 300, max: 7200)

### Response

The endpoint returns a session token object compatible with OpenAI's Realtime API:

```json
{
  "id": "sess_interview123_user456_2",
  "object": "realtime.session",
  "model": "gpt-4o-realtime-preview",
  "modalities": ["audio", "text"],
  "instructions": "You are an expert case interview assistant...",
  "voice": "alloy",
  "input_audio_format": "pcm16",
  "output_audio_format": "pcm16",
  "input_audio_transcription": {
    "model": "whisper-1"
  },
  "turn_detection": {
    "type": "server_vad",
    "threshold": 0.5,
    "prefix_padding_ms": 300,
    "silence_duration_ms": 200
  },
  "tools": [],
  "tool_choice": "none",
  "temperature": 0.8,
  "max_response_output_tokens": "inf",
  "client_secret": {
    "value": "token123",
    "expires_at": 1744396800
  },
  "interview_id": "interview123",
  "user_id": "user456",
  "question_number": 2,
  "expires_at": "2025-04-10T12:00:00Z",
  "ttl": 3600
}
```

## Dynamic Instructions

The system generates tailored instructions for each question based on:

1. Case type (Market Entry, Profitability, etc.)
2. Lead type (Interviewer-led or Candidate-led)
3. Difficulty level
4. Industry context
5. Question-specific prompt and evaluator context

Example instruction format:

```
You are an expert case interview assistant for a Medium Market Entry case in the Technology industry.

CASE CONTEXT:
Your client is a technology company looking to enter the smart home market...

CURRENT QUESTION (2 of 4):
What are the key customer segments?

YOUR ROLE:
- You are assisting with question #2 only
- Provide thoughtful and structured guidance based on the question
- This is a Interviewer-led case, so help guide the candidate through the analysis
- Evaluator's expectations: Evaluate ability to identify different customer needs

Be concise, supportive, and focus on helping the candidate demonstrate structured thinking and business acumen.
```

## Client Implementation

To use the generated token in your frontend:

1. Obtain a question-specific session token from the endpoint
2. Extract the `client_secret.value` from the response
3. Use this value to authenticate with OpenAI's Realtime API
4. Establish a WebRTC or WebSocket connection using the token
5. Begin the realtime session with the configured parameters

Example frontend code:

```javascript
// Get session token for a specific question
async function getQuestionToken(interviewId, questionNumber) {
  const response = await fetch(
    `/api/v1/interviews/${interviewId}/questions/${questionNumber}/token`,
    {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    }
  );
  
  return await response.json();
}

// Use token to start realtime session
async function startRealtimeSession(sessionToken) {
  const clientSecret = sessionToken.client_secret.value;
  
  // Initialize OpenAI Realtime client
  const client = new OpenAIRealtimeClient({
    clientSecret,
    modalities: sessionToken.modalities,
    voice: sessionToken.voice,
    // Other parameters from session token...
  });
  
  await client.connect();
  
  // Now ready for realtime interaction
  return client;
}
```

## Security Considerations

- Tokens are ephemeral and tied to specific questions
- Each token has a limited TTL (default: 1 hour)
- Tokens can only be generated for current or previous questions
- User must own the interview or be an admin
- User must have an active subscription
- Interview must be in progress

## Error Handling

Common errors:

- `404 Not Found`: Interview not found
- `403 Forbidden`: Not authorized to access this interview
- `400 Bad Request`: Interview is not in progress
- `400 Bad Request`: Cannot access future questions 