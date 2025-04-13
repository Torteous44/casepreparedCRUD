# WebRTC Connection Endpoints

This document describes the API endpoints used for WebRTC connections in the Case Prepared application.

## TURN Credentials Endpoint

### GET `/api/v1/webrtc/turn-credentials`

Generates TURN (Traversal Using Relays around NAT) server credentials using Twilio. These credentials are necessary for WebRTC connections to establish peer-to-peer communication, especially when participants are behind NATs or firewalls.

#### Request

```
GET /api/v1/webrtc/turn-credentials
Authorization: Bearer {access_token}
```

#### Response

```json
{
  "iceServers": [
    {
      "url": "stun:global.stun.twilio.com:3478?transport=udp",
      "urls": "stun:global.stun.twilio.com:3478?transport=udp"
    },
    {
      "url": "turn:global.turn.twilio.com:3478?transport=udp",
      "username": "twilio_username",
      "urls": "turn:global.turn.twilio.com:3478?transport=udp",
      "credential": "twilio_credential"
    },
    {
      "url": "turn:global.turn.twilio.com:3478?transport=tcp",
      "username": "twilio_username",
      "urls": "turn:global.turn.twilio.com:3478?transport=tcp",
      "credential": "twilio_credential"
    },
    {
      "url": "turn:global.turn.twilio.com:443?transport=tcp",
      "username": "twilio_username",
      "urls": "turn:global.turn.twilio.com:443?transport=tcp",
      "credential": "twilio_credential"
    }
  ],
  "ttl": 86400
}
```

#### Implementation Details

- Uses the official Twilio SDK to generate credentials
- Requires valid Twilio credentials in the `.env` file
- Provides multiple TURN/STUN server URLs to ensure connectivity across different network conditions

## OpenAI Realtime Session Endpoint

### POST `/api/v1/webrtc/openai-ephemeral-key`

Generates a Realtime Session from the OpenAI API for real-time conversation. The session includes all necessary connection details for the frontend to establish a connection with OpenAI's GPT-4o model for real-time audio/text conversation during an interview.

#### Request

```
POST /api/v1/webrtc/openai-ephemeral-key
Authorization: Bearer {access_token}
Content-Type: application/json
```

```json
{
  "interview_id": "uuid_of_interview",
  "question_number": 1
}
```

#### Response

```json
{
  "id": "sess_interview_id_user_id_question_number",
  "interviewId": "uuid_of_interview",
  "userId": "uuid_of_user",
  "questionNumber": 1,
  "expiresAt": "2023-10-31T12:30:45Z",
  "ttl": 3600,
  "instructions": "Detailed instructions based on interview context and question",
  "realtimeSession": {
    "id": "session_123abc",
    "object": "realtime.session",
    "client_secret": {
      "value": "secret_123abc"
    },
    "model": "gpt-4o-mini-realtime-preview",
    "modalities": ["audio", "text"],
    "voice": "alloy",
    "temperature": 0.8,
    "max_response_output_tokens": "inf"
    // Additional OpenAI session details...
  }
}
```

#### Implementation Details

- Makes a direct call to OpenAI's `/v1/realtime/sessions` endpoint 
- Implements API key rotation with fallback mechanisms
- Maps interview types to appropriate voice personas
- Includes detailed instructions specific to the interview question
- The session is time-limited (default 1 hour) for security

## Usage in Frontend

In the React component that handles WebRTC connections:

1. Fetch TURN credentials at component initialization:
   ```javascript
   const fetchTurnCredentials = async () => {
     const response = await fetch('/api/v1/webrtc/turn-credentials', {
       headers: {
         'Authorization': `Bearer ${accessToken}`
       }
     });
     const data = await response.json();
     
     // Use the ice servers for WebRTC configuration
     const peerConnection = new RTCPeerConnection({
       iceServers: data.iceServers
     });
   };
   ```

2. Connect to OpenAI Realtime API using the session:
   ```javascript
   const connectToOpenAI = async (interviewId, questionNumber) => {
     const response = await fetch('/api/v1/webrtc/openai-ephemeral-key', {
       method: 'POST',
       headers: {
         'Content-Type': 'application/json',
         'Authorization': `Bearer ${accessToken}`
       },
       body: JSON.stringify({ interview_id: interviewId, question_number: questionNumber })
     });
     const data = await response.json();
     
     // Use the realtime session to connect to OpenAI
     const openai = new OpenAI();
     
     // Connect using the realtime session's client secret value
     const realtimeStream = await openai.beta.audio.realtime.connect({
       session: data.realtimeSession,
       clientSecret: data.realtimeSession.client_secret.value
     });
   };
   ```

## Security Considerations

- All endpoints require authentication with a valid JWT
- API key rotation provides resilience and load balancing
- Realtime sessions have limited lifetimes (typically 1 hour)
- Server-side validation ensures users can only access interviews they are authorized for
- Client secrets provide better security than direct API key usage 