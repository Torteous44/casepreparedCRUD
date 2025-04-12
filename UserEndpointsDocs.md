# User API Endpoints Documentation

This document provides information on the available user management endpoints in the CasePrepared API.

## Base URL

All endpoints are available under the base URL: `/api/v1/users`

## Authentication

All user endpoints require authentication. Requests must include the JWT token in the Authorization header:

```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

## Endpoints

### 1. Get Current User

Retrieves the profile information of the currently authenticated user.

**Endpoint:** `GET /api/v1/users/me`

**Authentication Required:** Yes

**Request:** No parameters required

**Response:**
```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "email": "user@example.com",
  "full_name": "John Doe",
  "created_at": "2023-01-01T12:00:00Z",
  "updated_at": "2023-01-01T12:00:00Z"
}
```

**Status Codes:**
- `200 OK`: Request successful
- `401 Unauthorized`: Invalid or missing authentication token

### 2. Update Current User

Updates the profile information of the currently authenticated user.

**Endpoint:** `PATCH /api/v1/users/me`

**Authentication Required:** Yes

**Request Body:**
```json
{
  "email": "newemail@example.com",  // Optional
  "full_name": "New Name",          // Optional
  "password": "newpassword"         // Optional
}
```

Note: You only need to include the fields you want to update. All fields are optional.

**Response:**
```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "email": "newemail@example.com",
  "full_name": "New Name",
  "created_at": "2023-01-01T12:00:00Z",
  "updated_at": "2023-01-02T12:00:00Z"
}
```

**Status Codes:**
- `200 OK`: Update successful
- `401 Unauthorized`: Invalid or missing authentication token
- `422 Unprocessable Entity`: Invalid input data

### 3. Get User by ID

Retrieves the profile information of a specific user by their ID.

**Endpoint:** `GET /api/v1/users/{user_id}`

**Authentication Required:** Yes

**Path Parameters:**
- `user_id`: UUID of the user to retrieve

**Response:**
```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "email": "user@example.com",
  "full_name": "John Doe",
  "created_at": "2023-01-01T12:00:00Z",
  "updated_at": "2023-01-01T12:00:00Z"
}
```

**Status Codes:**
- `200 OK`: Request successful
- `401 Unauthorized`: Invalid or missing authentication token
- `404 Not Found`: User with the specified ID does not exist

## Usage Examples

### Get Current User

```javascript
const getUserProfile = async () => {
  try {
    const response = await fetch('https://casepreparedcrud.onrender.com/api/v1/users/me', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      throw new Error('Failed to fetch user profile');
    }
    
    const userData = await response.json();
    return userData;
  } catch (error) {
    console.error('Error fetching user profile:', error);
    throw error;
  }
};
```

### Update User Profile

```javascript
const updateUserProfile = async (updatedData) => {
  try {
    const response = await fetch('https://casepreparedcrud.onrender.com/api/v1/users/me', {
      method: 'PATCH',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(updatedData)
    });
    
    if (!response.ok) {
      throw new Error('Failed to update user profile');
    }
    
    const updatedUserData = await response.json();
    return updatedUserData;
  } catch (error) {
    console.error('Error updating user profile:', error);
    throw error;
  }
};

// Example usage:
// updateUserProfile({ full_name: "New Name" });
```

### Get User by ID

```javascript
const getUserById = async (userId) => {
  try {
    const response = await fetch(`https://casepreparedcrud.onrender.com/api/v1/users/${userId}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      if (response.status === 404) {
        throw new Error('User not found');
      }
      throw new Error('Failed to fetch user');
    }
    
    const userData = await response.json();
    return userData;
  } catch (error) {
    console.error('Error fetching user by ID:', error);
    throw error;
  }
};
```

## Error Handling

The API returns standard HTTP status codes to indicate the success or failure of a request. In case of errors, the response body typically contains a JSON object with more details:

```json
{
  "detail": "Error message describing what went wrong"
}
```

Common error scenarios:
- `401 Unauthorized`: Missing or invalid authentication token
- `404 Not Found`: Requested resource does not exist
- `422 Unprocessable Entity`: Invalid input data (e.g., invalid email format)

## Data Models

### User Model

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Unique identifier for the user |
| email | string | User's email address (unique) |
| full_name | string | User's full name |
| created_at | datetime | When the user account was created |
| updated_at | datetime | When the user account was last updated |

### UserUpdate Model

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| email | string | New email address | No |
| full_name | string | New full name | No |
| password | string | New password | No |

Note: When updating a user, you only need to include the fields you want to change. 