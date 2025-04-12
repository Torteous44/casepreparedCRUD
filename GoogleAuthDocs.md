# Google Authentication Documentation

This document provides comprehensive guidance on implementing Google authentication (both sign-up and login) with the CasePrepared API.

## Overview

The backend provides a single endpoint for Google authentication that handles both first-time users (sign-up) and returning users (login). The system automatically determines whether to create a new account or authenticate an existing one based on the email associated with the Google token.

## API Endpoint

**Endpoint:** `POST /api/v1/auth/google-login`

**Important:** This endpoint only accepts POST requests. Do not use GET requests.

**Request Body:**
```json
{
  "token": "google_id_token"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Status Codes:**
- `200 OK`: Authentication successful (either new user created or existing user authenticated)
- `401 Unauthorized`: Invalid Google token
- `400 Bad Request`: Missing email in token info
- `405 Method Not Allowed`: Incorrect HTTP method used (e.g., using GET instead of POST)

## Implementation Guide

### Backend Flow

1. User authenticates with Google on the frontend
2. Frontend sends the Google ID token to the backend
3. Backend verifies the token with Google
4. If the token is valid, the backend checks if a user with the email exists
   - If user exists: authenticates the user and issues a JWT token
   - If user doesn't exist: creates a new user account and issues a JWT token
5. Backend returns the JWT token to the frontend

### Frontend Implementation (React)

Here's a complete implementation example using React:

#### 1. Install dependencies

```bash
npm install @react-oauth/google jwt-decode
```

#### 2. Set up Google OAuth Provider in your app

```jsx
// main.jsx or App.jsx
import { GoogleOAuthProvider } from '@react-oauth/google';

function App() {
  return (
    <GoogleOAuthProvider clientId="YOUR_GOOGLE_CLIENT_ID">
      {/* Your app components */}
    </GoogleOAuthProvider>
  );
}
```

#### 3. Create a Google Login Button Component

```jsx
// GoogleLoginButton.jsx
import { useGoogleLogin } from '@react-oauth/google';
import { useState } from 'react';
import axios from 'axios';

function GoogleLoginButton({ onSuccess }) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleGoogleLogin = useGoogleLogin({
    onSuccess: async (response) => {
      setIsLoading(true);
      setError(null);
      console.log('Google auth response received', response);
      
      try {
        // Get ID token from Google response
        const { credential } = response;
        console.log('Got credential, sending to backend', credential);
        
        // Send token to your backend - MUST use POST method
        const backendResponse = await axios.post(
          'https://casepreparedcrud.onrender.com/api/v1/auth/google-login',
          { token: credential },  // Send as JSON body, not query parameter
          {
            headers: {
              'Content-Type': 'application/json'
            }
          }
        );
        
        const { access_token, token_type } = backendResponse.data;
        
        // Store tokens in local storage or state management
        localStorage.setItem('access_token', access_token);
        localStorage.setItem('token_type', token_type);
        
        // Trigger success callback
        if (onSuccess) onSuccess(access_token);
        
      } catch (err) {
        console.error('Error with Google authentication:', err);
        setError(err.response?.data?.detail || 'Authentication failed');
      } finally {
        setIsLoading(false);
      }
    },
    onError: (error) => {
      console.error('Google login error:', error);
      setError('Google authentication failed');
    },
    flow: 'implicit'
  });

  return (
    <div>
      <button 
        onClick={handleGoogleLogin}
        disabled={isLoading}
        className="google-login-button"
      >
        {isLoading ? 'Loading...' : 'Sign in with Google'}
      </button>
      
      {error && <div className="error-message">{error}</div>}
    </div>
  );
}

export default GoogleLoginButton;
```

#### 4. Alternative Implementation with Google Identity Services

```jsx
// GoogleLoginButton.jsx (alternative implementation)
import { GoogleLogin } from '@react-oauth/google';
import { useState } from 'react';
import axios from 'axios';

function GoogleLoginButton({ onSuccess }) {
  const [error, setError] = useState(null);

  const handleGoogleSuccess = async (credentialResponse) => {
    console.log('Google auth response received', credentialResponse);
    
    try {
      // Send token to your backend using POST
      const response = await axios.post(
        'https://casepreparedcrud.onrender.com/api/v1/auth/google-login',
        { token: credentialResponse.credential },
        {
          headers: {
            'Content-Type': 'application/json'
          }
        }
      );
      
      // Store the token
      localStorage.setItem('access_token', response.data.access_token);
      
      // Call success callback
      if (onSuccess) onSuccess(response.data);
      
    } catch (err) {
      console.error('Error with Google authentication:', err);
      setError(err.response?.data?.detail || 'Authentication failed');
    }
  };

  return (
    <div>
      <GoogleLogin
        onSuccess={handleGoogleSuccess}
        onError={() => {
          console.error('Google Login Failed');
          setError('Google authentication failed');
        }}
        useOneTap
      />
      
      {error && <div className="error-message">{error}</div>}
    </div>
  );
}

export default GoogleLoginButton;
```

## Common Issues and Solutions

### 1. "Method Not Allowed" (405) Error

**Problem**: You're seeing a 405 Method Not Allowed error.

**Solution**: Ensure you're using a POST request, not GET. Many HTTP clients default to GET, but this endpoint requires POST.

```javascript
// CORRECT
axios.post('/api/v1/auth/google-login', { token: googleToken });

// INCORRECT
axios.get('/api/v1/auth/google-login?token=' + googleToken);
```

### 2. Invalid Token Error

**Problem**: You receive a 401 Unauthorized response with "Invalid Google token".

**Solution**: 
- Check that you're sending the full credential token from Google
- Verify your GOOGLE_CLIENT_ID in your backend .env file matches your Google Cloud project
- Token could be expired (they typically last 1 hour)

### 3. Front-end/Back-end CORS Issues

**Problem**: You see CORS errors in the browser console.

**Solution**: The backend is configured to allow all origins, but ensure your request includes the appropriate headers and that you're testing with a proper domain, not from a file:// protocol.

### 4. Authentication Flow Logic

**Problem**: You're unsure when to sign up versus log in.

**Solution**: The endpoint handles both cases automatically:
- If a user with the email exists: it performs a login
- If no user with the email exists: it performs a sign-up

Your frontend code doesn't need to determine this - the backend handles it based on the Google token's email.

## Testing Google Authentication

1. Make sure your Google Cloud project has the correct OAuth credentials
2. Set up your application with the correct redirect URIs
3. Test with a valid Google account
4. Check server logs for detailed error messages if authentication fails

## Sign-Up vs Login Behavior

Since our endpoint handles both sign-up and login, the user experience will be:

### First-time Users (Sign-up)
1. User clicks "Sign in with Google"
2. User selects their Google account
3. Backend creates a new user account
4. User is logged in automatically

### Returning Users (Login)
1. User clicks "Sign in with Google"
2. User selects their Google account
3. Backend authenticates the existing user
4. User is logged in

The only difference between these flows is whether the user's email already exists in the database. 