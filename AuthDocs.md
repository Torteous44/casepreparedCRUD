# Authentication Documentation for CasePrepared Frontend

This document contains all the information needed for implementing authentication in the frontend application, including regular login/signup and Google OAuth authentication.

## API Endpoints

All authentication endpoints are available under the base URL: `/api/v1/auth`

### 1. User Registration (Email/Password)

**Endpoint:** `POST /api/v1/auth/register`

**Request Body:**
```json
{
  "email": "user@example.com",
  "full_name": "John Doe",
  "password": "securepassword"
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
- `200 OK`: Registration successful
- `400 Bad Request`: Email already exists or invalid input

### 2. User Login (Email/Password)

**Endpoint:** `POST /api/v1/auth/login`

**Request Body:**
```
username=user@example.com&password=securepassword
```
**Note:** This endpoint follows the OAuth2 password flow standard, so the email is sent as `username`.

**Content-Type:** `application/x-www-form-urlencoded`

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Status Codes:**
- `200 OK`: Login successful
- `401 Unauthorized`: Incorrect email or password

### 3. Google OAuth Login

**Endpoint:** `POST /api/v1/auth/google-login`

**Request Body:**
```json
{
  "token": "google_id_token_from_client"
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
- `200 OK`: Login successful
- `401 Unauthorized`: Invalid Google token
- `400 Bad Request`: Missing email in token info

## Authentication Flow

### Regular Email/Password Authentication

1. User fills out the registration form with email, full name, and password
2. Frontend sends a POST request to `/api/v1/auth/register`
3. On successful registration, store the received JWT token securely (preferably in an HTTP-only cookie or secure local storage)
4. For subsequent logins, user enters email and password
5. Frontend sends a POST request to `/api/v1/auth/login` with form-encoded data
6. On successful login, store the received JWT token

### Google OAuth Authentication

1. Set up Google OAuth in your frontend application:
   - Create a Google Developer Console project
   - Configure OAuth consent screen
   - Create OAuth client ID for Web application
   - Set authorized JavaScript origins and redirect URIs

2. Implement Google Sign-In button using the Google Identity Services library:

```html
<script src="https://accounts.google.com/gsi/client" async defer></script>
```

```javascript
function handleGoogleCallback(response) {
  // Get the ID token from the response
  const token = response.credential;
  
  // Send the token to your backend
  fetch('/api/v1/auth/google-login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ token }),
  })
  .then(response => response.json())
  .then(data => {
    // Store the access token and redirect or update UI
    localStorage.setItem('access_token', data.access_token);
    // Redirect to dashboard or protected page
  })
  .catch(error => {
    console.error('Google login error:', error);
  });
}
```

```html
<div id="g_id_onload"
     data-client_id="YOUR_GOOGLE_CLIENT_ID"
     data-callback="handleGoogleCallback"
     data-auto_prompt="false">
</div>
<div class="g_id_signin"
     data-type="standard"
     data-size="large"
     data-theme="outline"
     data-text="sign_in_with"
     data-shape="rectangular"
     data-logo_alignment="left">
</div>
```

## Token Management

### Storing Tokens

Store the JWT token securely:
- Preferred: HTTP-only cookies with Secure and SameSite flags
- Alternative: localStorage or sessionStorage (with proper security measures)

### Using Tokens for Authenticated Requests

Include the JWT token in the Authorization header for all authenticated API requests:

```javascript
fetch('/api/v1/some-protected-endpoint', {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
  },
})
.then(response => {
  // Handle response
});
```

### Token Expiration

The default token expiration is set to 30 minutes. You may want to implement:
- Automatic logout when token expires
- Token refresh mechanism (currently not implemented in the backend)
- Session tracking

## User Model

The user model includes the following fields:

- `id`: UUID, primary key
- `email`: String, unique, required
- `full_name`: String, required
- `password_hash`: String (only for email/password users)
- `google_oauth_id`: String (only for Google OAuth users)
- `created_at`: DateTime
- `updated_at`: DateTime

## Environment Configuration

The frontend needs to set the following environment variables:

```
GOOGLE_CLIENT_ID=your_google_client_id_here
API_BASE_URL=http://localhost:8000 # or your actual API URL
```

## Security Considerations

1. **HTTPS**: Ensure all communication occurs over HTTPS to prevent token interception
2. **XSS Protection**: Implement proper XSS protection when handling tokens
3. **CSRF Protection**: Implement CSRF tokens for form submissions
4. **Secure Storage**: Store tokens in secure storage mechanisms
5. **Token Validation**: Validate tokens on the client-side when possible before making requests
6. **Error Handling**: Implement proper error handling for authentication failures

## Logout Implementation

Since JWT tokens are stateless, frontend logout should:
1. Remove the token from storage (localStorage, cookies, etc.)
2. Redirect the user to the login page
3. Reset application state

## Protected Routes

In your frontend routing, implement protected routes that check for valid authentication:

```javascript
// Example using React Router
const ProtectedRoute = ({ children }) => {
  const token = localStorage.getItem('access_token');
  
  if (!token) {
    // Redirect to login if no token exists
    return <Navigate to="/login" replace />;
  }
  
  // Optional: Check if token is expired
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    if (payload.exp * 1000 < Date.now()) {
      localStorage.removeItem('access_token');
      return <Navigate to="/login" replace />;
    }
  } catch (e) {
    localStorage.removeItem('access_token');
    return <Navigate to="/login" replace />;
  }
  
  return children;
};
``` 