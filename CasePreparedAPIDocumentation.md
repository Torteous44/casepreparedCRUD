# CasePrepared API Documentation

This document provides comprehensive information about the CasePrepared API endpoints, authentication, data models, and integration guidance for frontend developers building the admin interface and user-facing applications.

## Base URLs

- **Development**: `http://localhost:8000`
- **Production**: `https://casepreparedcrud.onrender.com`

All endpoints are prefixed with `/api/v1`.

## Authentication

### Authentication Methods

The API supports two authentication methods:

1. **Email/Password Authentication**
2. **Google OAuth Authentication**

### Authentication Endpoints

#### 1. User Registration (Email/Password)

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

#### 2. User Login (Email/Password)

**Endpoint:** `POST /api/v1/auth/login`

**Request Body (form-data):**
```
username=user@example.com&password=securepassword
```

**Content-Type:** `application/x-www-form-urlencoded`

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### 3. Google OAuth Login

**Endpoint:** `POST /api/v1/auth/google-login`

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

### Using Authentication Tokens

Include the JWT token in the Authorization header for all authenticated API requests:

```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

## User Management

### User Endpoints

#### 1. Get Current User

**Endpoint:** `GET /api/v1/users/me`

**Authentication Required:** Yes

**Response:**
```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_admin": false,
  "created_at": "2023-01-01T12:00:00Z",
  "updated_at": "2023-01-01T12:00:00Z"
}
```

#### 2. Update Current User

**Endpoint:** `PATCH /api/v1/users/me`

**Authentication Required:** Yes

**Request Body:**
```json
{
  "email": "newemail@example.com",
  "full_name": "New Name",
  "password": "newpassword"
}
```

**Response:**
```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "email": "newemail@example.com",
  "full_name": "New Name",
  "is_admin": false,
  "created_at": "2023-01-01T12:00:00Z",
  "updated_at": "2023-01-02T12:00:00Z"
}
```

#### 3. Get User by ID

**Endpoint:** `GET /api/v1/users/{user_id}`

**Authentication Required:** Yes

**Response:**
```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_admin": false,
  "created_at": "2023-01-01T12:00:00Z",
  "updated_at": "2023-01-01T12:00:00Z"
}
```

## Interview Templates

### Template Endpoints

#### 1. List Interview Templates

**Endpoint:** `GET /api/v1/interview-templates/`

**Authentication Required:** Yes

**Query Parameters:**
- `skip`: Number of records to skip (pagination)
- `limit`: Maximum number of records to return
- `case_type`: Filter by case type
- `lead_type`: Filter by lead type
- `difficulty`: Filter by difficulty
- `company`: Filter by company
- `industry`: Filter by industry

**Response:**
```json
[
  {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "case_type": "Market Entry",
    "lead_type": "Interviewer-led",
    "difficulty": "Medium",
    "company": "Example Corp",
    "industry": "Technology",
    "image_url": "https://example.com/images/market_entry.jpg",
    "version": "1.0"
  },
  {
    "id": "4fa85f64-5717-4562-b3fc-2c963f66afa7",
    "case_type": "Profitability",
    "lead_type": "Candidate-led",
    "difficulty": "Hard",
    "company": "Sample Inc",
    "industry": "Healthcare",
    "image_url": "https://example.com/images/profitability.jpg",
    "version": "1.0"
  }
]
```

#### 2. Get Interview Template Details

**Endpoint:** `GET /api/v1/interview-templates/{template_id}`

**Authentication Required:** Yes

**Response:**
```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "case_type": "Market Entry",
  "lead_type": "Interviewer-led",
  "difficulty": "Medium",
  "company": "Example Corp",
  "industry": "Technology",
  "prompt": "Your client is a technology company looking to enter the smart home market...",
  "structure": {
    "question1": {
      "prompt": "What is the market size for smart home devices?",
      "context": "Look for thoughtful market segmentation and growth trends"
    },
    "question2": {
      "prompt": "What are the key customer segments?",
      "context": "Evaluate ability to identify different customer needs"
    },
    "question3": {
      "prompt": "What would be an appropriate go-to-market strategy?",
      "context": "Check for channel strategy and prioritization"
    },
    "question4": {
      "prompt": "What are potential risks and how would you mitigate them?",
      "context": "Assess risk identification and mitigation planning"
    }
  },
  "image_url": "https://example.com/images/market_entry.jpg",
  "version": "1.0",
  "created_at": "2023-01-01T12:00:00Z",
  "updated_at": "2023-01-01T12:00:00Z"
}
```

#### 3. Create Interview Template (Admin Only)

**Endpoint:** `POST /api/v1/interview-templates/`

**Authentication Required:** Yes (Admin only)

**Request Body:**
```json
{
  "case_type": "Market Entry",
  "lead_type": "Interviewer-led",
  "difficulty": "Medium",
  "company": "Example Corp",
  "industry": "Technology",
  "prompt": "Your client is a technology company looking to enter the smart home market...",
  "structure": {
    "question1": {
      "prompt": "What is the market size for smart home devices?",
      "context": "Look for thoughtful market segmentation and growth trends"
    },
    "question2": {
      "prompt": "What are the key customer segments?",
      "context": "Evaluate ability to identify different customer needs"
    },
    "question3": {
      "prompt": "What would be an appropriate go-to-market strategy?",
      "context": "Check for channel strategy and prioritization"
    },
    "question4": {
      "prompt": "What are potential risks and how would you mitigate them?",
      "context": "Assess risk identification and mitigation planning"
    }
  },
  "image_url": "https://example.com/images/market_entry.jpg",
  "version": "1.0"
}
```

**Response:**
```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "case_type": "Market Entry",
  "lead_type": "Interviewer-led",
  "difficulty": "Medium",
  "company": "Example Corp",
  "industry": "Technology",
  "prompt": "Your client is a technology company looking to enter the smart home market...",
  "structure": {
    "question1": {
      "prompt": "What is the market size for smart home devices?",
      "context": "Look for thoughtful market segmentation and growth trends"
    },
    "question2": {
      "prompt": "What are the key customer segments?",
      "context": "Evaluate ability to identify different customer needs"
    },
    "question3": {
      "prompt": "What would be an appropriate go-to-market strategy?",
      "context": "Check for channel strategy and prioritization"
    },
    "question4": {
      "prompt": "What are potential risks and how would you mitigate them?",
      "context": "Assess risk identification and mitigation planning"
    }
  },
  "image_url": "https://example.com/images/market_entry.jpg",
  "version": "1.0",
  "created_at": "2023-01-01T12:00:00Z",
  "updated_at": "2023-01-01T12:00:00Z"
}
```

#### 4. Update Interview Template (Admin Only)

**Endpoint:** `PUT /api/v1/interview-templates/{template_id}`

**Authentication Required:** Yes (Admin only)

**Request Body:**
```json
{
  "case_type": "Market Entry Strategy",
  "difficulty": "Hard",
  "prompt": "Updated prompt text...",
  "image_url": "https://example.com/images/updated_market_entry.jpg"
}
```

**Response:**
```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "case_type": "Market Entry Strategy",
  "lead_type": "Interviewer-led",
  "difficulty": "Hard",
  "company": "Example Corp",
  "industry": "Technology",
  "prompt": "Updated prompt text...",
  "structure": {
    "question1": {
      "prompt": "What is the market size for smart home devices?",
      "context": "Look for thoughtful market segmentation and growth trends"
    },
    "question2": {
      "prompt": "What are the key customer segments?",
      "context": "Evaluate ability to identify different customer needs"
    },
    "question3": {
      "prompt": "What would be an appropriate go-to-market strategy?",
      "context": "Check for channel strategy and prioritization"
    },
    "question4": {
      "prompt": "What are potential risks and how would you mitigate them?",
      "context": "Assess risk identification and mitigation planning"
    }
  },
  "image_url": "https://example.com/images/updated_market_entry.jpg",
  "version": "1.0",
  "created_at": "2023-01-01T12:00:00Z",
  "updated_at": "2023-01-02T12:00:00Z"
}
```

#### 5. Delete Interview Template (Admin Only)

**Endpoint:** `DELETE /api/v1/interview-templates/{template_id}`

**Authentication Required:** Yes (Admin only)

**Response:** No content (204)

## Interviews

### Interview Endpoints

#### 1. Create Interview

**Endpoint:** `POST /api/v1/interviews/`

**Authentication Required:** Yes

**Request Body:**
```json
{
  "template_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "scheduled_at": "2023-01-15T14:00:00Z"
}
```

**Response:**
```json
{
  "id": "5fa85f64-5717-4562-b3fc-2c963f66afa8",
  "user_id": "2fa85f64-5717-4562-b3fc-2c963f66afa9",
  "template_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "scheduled_at": "2023-01-15T14:00:00Z",
  "status": "scheduled",
  "created_at": "2023-01-01T12:00:00Z",
  "updated_at": "2023-01-01T12:00:00Z"
}
```

#### 2. Get User Interviews

**Endpoint:** `GET /api/v1/interviews/`

**Authentication Required:** Yes

**Response:**
```json
[
  {
    "id": "5fa85f64-5717-4562-b3fc-2c963f66afa8",
    "user_id": "2fa85f64-5717-4562-b3fc-2c963f66afa9",
    "template_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "template": {
      "case_type": "Market Entry",
      "lead_type": "Interviewer-led",
      "difficulty": "Medium",
      "company": "Example Corp",
      "industry": "Technology",
      "image_url": "https://example.com/images/market_entry.jpg"
    },
    "scheduled_at": "2023-01-15T14:00:00Z",
    "status": "scheduled",
    "created_at": "2023-01-01T12:00:00Z",
    "updated_at": "2023-01-01T12:00:00Z"
  }
]
```

#### 3. Get Interview Details

**Endpoint:** `GET /api/v1/interviews/{interview_id}`

**Authentication Required:** Yes

**Response:**
```json
{
  "id": "5fa85f64-5717-4562-b3fc-2c963f66afa8",
  "user_id": "2fa85f64-5717-4562-b3fc-2c963f66afa9",
  "template_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "template": {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "case_type": "Market Entry",
    "lead_type": "Interviewer-led",
    "difficulty": "Medium",
    "company": "Example Corp",
    "industry": "Technology",
    "prompt": "Your client is a technology company looking to enter the smart home market...",
    "structure": {
      "question1": {
        "prompt": "What is the market size for smart home devices?",
        "context": "Look for thoughtful market segmentation and growth trends"
      },
      "question2": {
        "prompt": "What are the key customer segments?",
        "context": "Evaluate ability to identify different customer needs"
      },
      "question3": {
        "prompt": "What would be an appropriate go-to-market strategy?",
        "context": "Check for channel strategy and prioritization"
      },
      "question4": {
        "prompt": "What are potential risks and how would you mitigate them?",
        "context": "Assess risk identification and mitigation planning"
      }
    },
    "image_url": "https://example.com/images/market_entry.jpg"
  },
  "scheduled_at": "2023-01-15T14:00:00Z",
  "status": "scheduled",
  "created_at": "2023-01-01T12:00:00Z",
  "updated_at": "2023-01-01T12:00:00Z"
}
```

## Subscriptions

### Subscription Endpoints

#### 1. Get Current Subscription

**Endpoint:** `GET /api/v1/subscriptions/current`

**Authentication Required:** Yes

**Response:**
```json
{
  "id": "6fa85f64-5717-4562-b3fc-2c963f66afa7",
  "user_id": "2fa85f64-5717-4562-b3fc-2c963f66afa9",
  "plan": "premium",
  "status": "active",
  "start_date": "2023-01-01T00:00:00Z",
  "end_date": "2024-01-01T00:00:00Z",
  "created_at": "2023-01-01T12:00:00Z",
  "updated_at": "2023-01-01T12:00:00Z"
}
```

## Admin-Specific Information

### Identifying Admin Users

To determine if a user is an admin, check the `is_admin` field in the user object. Admin users have this field set to `true`.

### Admin Routes

The following routes require admin privileges:

1. `POST /api/v1/interview-templates/` - Create a new interview template
2. `PUT /api/v1/interview-templates/{template_id}` - Update an existing template
3. `DELETE /api/v1/interview-templates/{template_id}` - Delete a template

### Admin UI Requirements

When building the admin frontend, consider implementing:

1. **Admin Dashboard**:
   - Summary statistics (users, interviews, templates)
   - Quick access to template management

2. **Template Management**:
   - Table view of all templates with filtering/sorting
   - Detail view for creating/editing templates
   - Image upload functionality for template images
   - Rich text editor for template prompts
   - JSON editor for template structure

3. **User Management**:
   - View registered users
   - View user's subscription status
   - Option to grant/revoke admin privileges

## Error Handling

The API returns standard HTTP status codes with error details:

```json
{
  "detail": "Error message describing what went wrong"
}
```

Common error codes:

- `400 Bad Request`: Invalid input data
- `401 Unauthorized`: Invalid or missing authentication token
- `403 Forbidden`: Insufficient permissions (non-admin attempting admin actions)
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error

For 422 responses, additional validation details are provided:

```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

## Data Models

### User Model

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Unique identifier |
| email | string | User's email address (unique) |
| full_name | string | User's full name |
| password_hash | string | Hashed password (not returned to client) |
| google_oauth_id | string | Google OAuth ID (if applicable) |
| is_admin | boolean | Whether the user has admin privileges |
| created_at | datetime | When the account was created |
| updated_at | datetime | When the account was last updated |

### Interview Template Model

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Unique identifier |
| case_type | string | Type of case (e.g., Market Entry, Profitability) |
| lead_type | string | How the case is led (e.g., Interviewer-led, Candidate-led) |
| difficulty | string | Difficulty level (e.g., Easy, Medium, Hard) |
| company | string | Company featured in the case |
| industry | string | Industry sector |
| prompt | text | Main case prompt |
| structure | JSON | Question structure with prompts and context |
| image_url | string | URL to an image for the template |
| version | string | Template version |
| created_at | datetime | When the template was created |
| updated_at | datetime | When the template was last updated |

### Interview Model

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Unique identifier |
| user_id | UUID | ID of user who owns the interview |
| template_id | UUID | ID of the interview template |
| scheduled_at | datetime | When the interview is scheduled |
| status | string | Status of the interview (scheduled, completed, cancelled) |
| created_at | datetime | When the interview was created |
| updated_at | datetime | When the interview was last updated |

### Subscription Model

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Unique identifier |
| user_id | UUID | ID of user who owns the subscription |
| plan | string | Subscription plan (free, premium, etc.) |
| status | string | Status (active, cancelled, trial) |
| start_date | datetime | When the subscription started |
| end_date | datetime | When the subscription ends |
| created_at | datetime | When the record was created |
| updated_at | datetime | When the record was last updated |

## Frontend Implementation Guide

### Authentication Flow

1. **User Login**:
   - Regular users can log in with email/password or Google OAuth
   - Store the JWT token securely (HTTP-only cookie or secure localStorage)

2. **Admin Login**:
   - Use the same login endpoints
   - Check the `is_admin` field in the user object to determine admin status
   - Redirect to admin dashboard if user is an admin

### Admin Dashboard Implementation

1. **Template Management**:
   - Implement CRUD operations for templates
   - Image upload for template images
   - Rich text editor for prompts
   - Form validation matching API requirements

2. **Design Considerations**:
   - Clear separation between admin and user interfaces
   - Proper error handling for admin-only operations
   - Confirmation dialogs for destructive actions (deletes)

### Code Example: Admin Template List

```javascript
// Example using React and Axios

import axios from 'axios';
import { useState, useEffect } from 'react';

const API_BASE_URL = 'https://casepreparedcrud.onrender.com/api/v1';

function AdminTemplateList() {
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchTemplates = async () => {
      try {
        const token = localStorage.getItem('access_token');
        
        const response = await axios.get(`${API_BASE_URL}/interview-templates`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        setTemplates(response.data);
        setLoading(false);
      } catch (err) {
        setError('Failed to fetch templates. Check if you have admin privileges.');
        setLoading(false);
        console.error('Error fetching templates:', err);
      }
    };

    fetchTemplates();
  }, []);

  const handleDelete = async (templateId) => {
    if (!window.confirm('Are you sure you want to delete this template?')) {
      return;
    }
    
    try {
      const token = localStorage.getItem('access_token');
      
      await axios.delete(`${API_BASE_URL}/interview-templates/${templateId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      // Remove from local state
      setTemplates(templates.filter(template => template.id !== templateId));
    } catch (err) {
      setError('Failed to delete template');
      console.error('Error deleting template:', err);
    }
  };

  if (loading) return <div>Loading templates...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="admin-template-list">
      <h2>Interview Templates</h2>
      <button className="create-button" onClick={() => navigate('/admin/templates/new')}>
        Create New Template
      </button>
      
      <table>
        <thead>
          <tr>
            <th>Image</th>
            <th>Case Type</th>
            <th>Lead Type</th>
            <th>Difficulty</th>
            <th>Company</th>
            <th>Industry</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {templates.map(template => (
            <tr key={template.id}>
              <td>
                {template.image_url ? (
                  <img src={template.image_url} alt={template.case_type} width="50" />
                ) : (
                  <span>No image</span>
                )}
              </td>
              <td>{template.case_type}</td>
              <td>{template.lead_type}</td>
              <td>{template.difficulty}</td>
              <td>{template.company || 'N/A'}</td>
              <td>{template.industry || 'N/A'}</td>
              <td>
                <button onClick={() => navigate(`/admin/templates/edit/${template.id}`)}>
                  Edit
                </button>
                <button className="delete" onClick={() => handleDelete(template.id)}>
                  Delete
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

### Security Considerations

1. **Token Storage**:
   - Store tokens securely (HTTP-only cookies preferred)
   - Implement token refresh mechanism for long sessions

2. **Admin Role Protection**:
   - Check `is_admin` flag on frontend to hide/show admin UI
   - Never bypass API's role checking with frontend-only checks

3. **HTTPS**:
   - Ensure all API communication happens over HTTPS

## Appendix: Common Tasks and Solutions

### Checking Admin Status

```javascript
const checkAdminStatus = async () => {
  try {
    const token = localStorage.getItem('access_token');
    
    const response = await axios.get(`${API_BASE_URL}/users/me`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    return response.data.is_admin === true;
  } catch (err) {
    console.error('Error checking admin status:', err);
    return false;
  }
};
```

### Handling Image Upload

```javascript
const uploadImage = async (file) => {
  // In a real implementation, you would upload to your 
  // chosen storage service (AWS S3, Cloudinary, etc.)
  // and return the public URL
  
  // This is a placeholder example
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await axios.post('YOUR_IMAGE_UPLOAD_SERVICE', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
  
  return response.data.url; // Returns the image URL
};
``` 