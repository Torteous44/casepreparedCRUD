# AssemblyAI Token API

## Endpoint

```
GET /api/v1/assembly/token
```

## Description

Generates a temporary AssemblyAI token for real-time transcription services. This token can be used client-side to connect to AssemblyAI's real-time transcription WebSocket API.

## Authentication

Requires authentication with a valid user account.

## Request

No request body required.

## Response

```json
{
  "token": "temporary_assembly_ai_token"
}
```

The token is valid for 1 hour (3600 seconds).

## Error Handling

- `401 Unauthorized`: If authentication is missing or invalid
- `500 Internal Server Error`: If the AssemblyAI API key is not configured
- `500 Internal Server Error`: If the request to AssemblyAI fails
- `500 Internal Server Error`: If the response from AssemblyAI doesn't contain a token

## Example Usage

```javascript
// Client-side JavaScript example
async function getAssemblyToken() {
  const response = await fetch('https://api.caseprepared.com/api/v1/assembly/token', {
    method: 'GET',
    headers: {
      'Authorization': 'Bearer YOUR_ACCESS_TOKEN'
    }
  });
  
  const data = await response.json();
  return data.token;
}

// Using the token with AssemblyAI's real-time transcription
async function startTranscription() {
  const token = await getAssemblyToken();
  
  // Connect to AssemblyAI with the temporary token
  const socket = new WebSocket(`wss://api.assemblyai.com/v2/realtime/ws?token=${token}`);
  
  socket.onopen = () => {
    console.log('Connected to AssemblyAI');
    // Start sending audio data...
  };
}
``` 