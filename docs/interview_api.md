# Interview API Documentation

## Overview

The Interview API provides endpoints to manage interview sessions, including creation, retrieval, updates, and realtime session token generation. The API supports both regular interview management and features for realtime interactions with AI assistants during interview sessions.

## Authentication

All endpoints require authentication with a valid JWT token. Include the token in the `Authorization` header:

```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

## Base URL

All API endpoints are prefixed with `/api/v1/interviews`.

## Endpoints

### List Interviews

Retrieves a list of interviews for the current user.

**Endpoint:** `GET /api/v1/interviews/`

**Authentication Required:** Yes

**Query Parameters:**
- `skip`: Number of records to skip (pagination)
- `limit`: Maximum number of records to return (default: 100)
- `status`: Filter by status (e.g., "in-progress", "completed")
- `user_id`: Filter by specific user (admin only)

**Response:**
```json
[
  {
    "id": "5fa85f64-5717-4562-b3fc-2c963f66afa8",
    "user_id": "2fa85f64-5717-4562-b3fc-2c963f66afa9",
    "template_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "status": "in-progress",
    "started_at": "2023-01-01T12:00:00Z",
    "completed_at": null,
    "progress_data": {
      "current_question": 2,
      "questions_completed": [1]
    }
  },
  // Additional interviews...
]
```

### Create Interview

Creates a new interview session.

**Endpoint:** `POST /api/v1/interviews/`

**Authentication Required:** Yes

**Request Body:**
```json
{
  "template_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
}
```

**Response:**
```json
{
  "id": "5fa85f64-5717-4562-b3fc-2c963f66afa8",
  "user_id": "2fa85f64-5717-4562-b3fc-2c963f66afa9",
  "template_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "status": "in-progress",
  "started_at": "2023-01-01T12:00:00Z",
  "completed_at": null,
  "progress_data": {
    "current_question": 1,
    "questions_completed": []
  }
}
```

### Get Interview by ID

Retrieves a specific interview by its ID.

**Endpoint:** `GET /api/v1/interviews/{interview_id}`

**Authentication Required:** Yes

**Response:**
```json
{
  "id": "5fa85f64-5717-4562-b3fc-2c963f66afa8",
  "user_id": "2fa85f64-5717-4562-b3fc-2c963f66afa9",
  "template_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "status": "in-progress",
  "started_at": "2023-01-01T12:00:00Z",
  "completed_at": null,
  "progress_data": {
    "current_question": 2,
    "questions_completed": [1]
  }
}
```

### Update Interview

Updates an interview's status or metadata.

**Endpoint:** `PATCH /api/v1/interviews/{interview_id}`

**Authentication Required:** Yes

**Request Body:**
```json
{
  "status": "completed",
  "progress_data": {
    "current_question": 4, 
    "questions_completed": [1, 2, 3, 4]
  }
}
```

**Response:** Updated interview object

```json
{
  "id": "5fa85f64-5717-4562-b3fc-2c963f66afa8",
  "user_id": "2fa85f64-5717-4562-b3fc-2c963f66afa9",
  "template_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "status": "completed",
  "started_at": "2023-01-01T12:00:00Z",
  "completed_at": "2023-01-01T13:30:00Z",
  "progress_data": {
    "current_question": 4,
    "questions_completed": [1, 2, 3, 4]
  }
}
```

### Delete Interview

Deletes an interview.

**Endpoint:** `DELETE /api/v1/interviews/{interview_id}`

**Authentication Required:** Yes

**Response:** No content (204)

### Generate Interview Credentials

Generates ephemeral credentials for an interview session, including TURN server credentials and a session token.

**Endpoint:** `POST /api/v1/interviews/{interview_id}/credentials`

**Authentication Required:** Yes

**Response:**
```json
{
  "turn_credentials": {
    "username": "user123:1744396800",
    "password": "abc123def456",
    "ttl": 86400,
    "expiration": 1744396800,
    "urls": [
      "turn:turn.example.com:3478?transport=udp",
      "turn:turn.example.com:3478?transport=tcp",
      "turn:turn.example.com:443?transport=tcp",
      "stun:stun.example.com:3478"
    ]
  },
  "session_token": {
    "id": "sess_interview123_user456",
    "object": "realtime.session",
    "model": "gpt-4o-realtime-preview",
    "modalities": ["audio", "text"],
    "instructions": "You are an interview assistant...",
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
    "expires_at": "2025-04-10T12:00:00Z",
    "ttl": 3600
  }
}
```

### Generate Question-Specific Session Token

Generates a realtime session token for a specific interview question, with dynamically generated instructions based on the question context.

**Endpoint:** `GET /api/v1/interviews/{interview_id}/questions/{question_number}/token`

**Authentication Required:** Yes

**Path Parameters:**
- `interview_id`: UUID of the interview
- `question_number`: Question number (1-4)

**Query Parameters:**
- `ttl`: Time to live in seconds (default: 3600, min: 300, max: 7200)

**Response:**
```json
{
  "id": "sess_interview123_user456_2",
  "object": "realtime.session",
  "model": "gpt-4o-realtime-preview",
  "modalities": ["audio", "text"],
  "instructions": "You are an expert case interview assistant for a Medium Market Entry case in the Technology industry...",
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

## Error Responses

All API endpoints follow a standardized error response format:

```json
{
  "detail": "Error message description"
}
```

Common error status codes:
- `400 Bad Request`: Invalid input or parameters
- `401 Unauthorized`: Missing or invalid authentication credentials
- `403 Forbidden`: Authenticated but not authorized to access the resource
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server-side error

## Realtime Session Usage

The question-specific session token can be used to establish a realtime session with OpenAI's Realtime API. The token provides a secure, ephemeral credential that includes context-aware instructions for the AI assistant based on the specific interview question.

The session token is structured according to OpenAI's Realtime session object format and includes:

1. Session identification (`id`)
2. AI model configuration (`model`, `temperature`, etc.)
3. Audio settings (`voice`, `input_audio_format`, etc.)
4. Question-specific instructions tailored to the interview context
5. Security credentials (`client_secret`)
6. Expiration metadata (`expires_at`, `ttl`)

Once you have obtained a session token, it can be used with a WebRTC or WebSocket connection to the Realtime API service, enabling real-time audio and text interactions between the user and the AI assistant. 