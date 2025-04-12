# Admin Interview Template Management Documentation

This document provides information on the admin-only endpoints for managing interview templates in the CasePrepared API.

## Overview

The interview template system has been updated with the following changes:

1. Added `image_url` field to the interview template model
2. Added admin-only access controls for template management endpoints
3. Added a user admin role system

## Admin User Setup

To create or promote a user to an admin role, use the provided script:

```bash
# Set required environment variables
export ADMIN_EMAIL="admin@example.com"
export ADMIN_NAME="Admin User"
export ADMIN_PASSWORD="secure_password"

# Run the script
python scripts/create_admin.py
```

## Admin API Endpoints

All endpoints require authentication with an admin user. Requests must include the JWT token in the Authorization header:

```
Authorization: Bearer YOUR_ADMIN_ACCESS_TOKEN
```

### 1. Create New Interview Template

Creates a new interview template.

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

**Status Codes:**
- `200 OK`: Template created successfully
- `401 Unauthorized`: Invalid or missing authentication token
- `403 Forbidden`: User does not have admin privileges
- `422 Unprocessable Entity`: Invalid input data

### 2. Update Interview Template

Updates an existing interview template.

**Endpoint:** `PUT /api/v1/interview-templates/{template_id}`

**Authentication Required:** Yes (Admin only)

**Path Parameters:**
- `template_id`: UUID of the template to update

**Request Body:**
```json
{
  "case_type": "Market Entry Strategy",
  "difficulty": "Hard",
  "image_url": "https://example.com/images/updated_market_entry.jpg"
}
```

Note: You only need to include the fields you want to update. All fields are optional.

**Response:**
```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "case_type": "Market Entry Strategy",
  "lead_type": "Interviewer-led",
  "difficulty": "Hard",
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
  "image_url": "https://example.com/images/updated_market_entry.jpg",
  "version": "1.0",
  "created_at": "2023-01-01T12:00:00Z",
  "updated_at": "2023-01-02T12:00:00Z"
}
```

**Status Codes:**
- `200 OK`: Template updated successfully
- `401 Unauthorized`: Invalid or missing authentication token
- `403 Forbidden`: User does not have admin privileges
- `404 Not Found`: Template with specified ID does not exist
- `422 Unprocessable Entity`: Invalid input data

### 3. Delete Interview Template

Deletes an interview template.

**Endpoint:** `DELETE /api/v1/interview-templates/{template_id}`

**Authentication Required:** Yes (Admin only)

**Path Parameters:**
- `template_id`: UUID of the template to delete

**Response:** No content (204)

**Status Codes:**
- `204 No Content`: Template deleted successfully
- `401 Unauthorized`: Invalid or missing authentication token
- `403 Forbidden`: User does not have admin privileges
- `404 Not Found`: Template with specified ID does not exist

## Usage Examples

### Create a New Template

```javascript
const createTemplate = async (templateData) => {
  try {
    const response = await fetch('https://casepreparedcrud.onrender.com/api/v1/interview-templates', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('admin_access_token')}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(templateData)
    });
    
    if (!response.ok) {
      if (response.status === 403) {
        throw new Error('Admin privileges required');
      }
      throw new Error('Failed to create template');
    }
    
    const newTemplate = await response.json();
    return newTemplate;
  } catch (error) {
    console.error('Error creating template:', error);
    throw error;
  }
};
```

### Update a Template

```javascript
const updateTemplate = async (templateId, updateData) => {
  try {
    const response = await fetch(`https://casepreparedcrud.onrender.com/api/v1/interview-templates/${templateId}`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('admin_access_token')}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(updateData)
    });
    
    if (!response.ok) {
      if (response.status === 403) {
        throw new Error('Admin privileges required');
      }
      if (response.status === 404) {
        throw new Error('Template not found');
      }
      throw new Error('Failed to update template');
    }
    
    const updatedTemplate = await response.json();
    return updatedTemplate;
  } catch (error) {
    console.error('Error updating template:', error);
    throw error;
  }
};
```

### Delete a Template

```javascript
const deleteTemplate = async (templateId) => {
  try {
    const response = await fetch(`https://casepreparedcrud.onrender.com/api/v1/interview-templates/${templateId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('admin_access_token')}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      if (response.status === 403) {
        throw new Error('Admin privileges required');
      }
      if (response.status === 404) {
        throw new Error('Template not found');
      }
      throw new Error('Failed to delete template');
    }
    
    return true;
  } catch (error) {
    console.error('Error deleting template:', error);
    throw error;
  }
};
```

## Admin Frontend Considerations

When building an admin interface, consider:

1. **Authentication Flow**: Implement admin login separate from regular user login
2. **UI Access Control**: Only show admin features to users with admin privileges
3. **Template Image Management**: Provide upload functionality for template images
4. **Error Handling**: Handle 403 Forbidden responses appropriately to guide admin users
5. **Batch Operations**: Consider implementing batch operations for managing multiple templates

## Data Model

### Interview Template Model

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| id | UUID | Unique identifier | Auto-generated |
| case_type | string | Type of case (e.g., Market Entry, Profitability) | Yes |
| lead_type | string | How the case is led (e.g., Interviewer-led, Candidate-led) | Yes |
| difficulty | string | Difficulty level (e.g., Easy, Medium, Hard) | Yes |
| company | string | Company featured in the case | No |
| industry | string | Industry sector | No |
| prompt | text | Main case prompt | Yes |
| structure | JSON | Question structure with prompts and context | Yes |
| image_url | string | URL to an image for the template | No |
| version | string | Template version | Default: "1.0" |
| created_at | datetime | When the template was created | Auto-generated |
| updated_at | datetime | When the template was last updated | Auto-updated | 