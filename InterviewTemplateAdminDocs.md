# Interview Template Administration API Documentation

This document provides information for administrators on creating and managing interview templates with the CasePrepared API.

## Overview

The Interview Template Administration API allows administrators to:

1. Upload images to Cloudflare
2. Create interview templates with structured questions
3. Update existing templates
4. Delete templates

All endpoints require authentication and should be restricted to administrators in a production environment.

## Image Upload

Before creating a template with an image, you'll need to upload the image to Cloudflare. There are two methods available:

### 1. Server-side Upload

**Endpoint:** `POST /api/v1/images/upload`

**Authentication Required:** Yes

**Request:**
- Content-Type: multipart/form-data
- Body:
  - file: The image file to upload

**Response:**
```json
{
  "image_url": "https://cloudflare-images.com/v1/your-account-id/your-image-id/image.jpg"
}
```

**Example:**
```javascript
const uploadImage = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch('https://casepreparedcrud.onrender.com/api/v1/images/upload', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`
    },
    body: formData
  });

  const data = await response.json();
  return data.image_url;
};
```

### 2. Client-side Direct Upload (Recommended for larger files)

**Endpoint:** `POST /api/v1/images/upload-url`

**Authentication Required:** Yes

**Response:**
```json
{
  "upload_url": "https://upload.imagedelivery.net/your-direct-upload-url",
  "id": "image-id",
  "expires": "2023-01-01T12:00:00Z"
}
```

**Example:**
```javascript
// Step 1: Get a direct upload URL
const getUploadUrl = async () => {
  const response = await fetch('https://casepreparedcrud.onrender.com/api/v1/images/upload-url', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    }
  });
  
  return response.json();
};

// Step 2: Upload the image directly to Cloudflare
const uploadImageDirectly = async (file) => {
  const { upload_url } = await getUploadUrl();
  
  const formData = new FormData();
  formData.append('file', file);
  
  const uploadResponse = await fetch(upload_url, {
    method: 'POST',
    body: formData
  });
  
  // The image URL will be available in the response
  const uploadResult = await uploadResponse.json();
  return uploadResult.result.variants[0]; // The image URL
};
```

## Creating Interview Templates

### Admin Template Creation Endpoint

**Endpoint:** `POST /api/v1/templates/admin`

**Authentication Required:** Yes

**Request Body:**
```json
{
  "case_type": "Market Entry",
  "lead_type": "Interviewer-Led",
  "difficulty": "Medium",
  "company": "Tech Corp",
  "industry": "Technology",
  "prompt": "Your client is a tech company looking to enter the healthcare market...",
  "image_url": "https://cloudflare-images.com/v1/your-account-id/your-image-id/image.jpg",
  "version": "1.0",
  "question1": {
    "question": "What factors should the client consider when entering this market?",
    "context": "The healthcare market has strict regulations and high barriers to entry."
  },
  "question2": {
    "question": "How should they position their product?",
    "context": "There are already established competitors in this space."
  },
  "question3": {
    "question": "What pricing strategy would you recommend?",
    "context": "Healthcare products have unique pricing considerations."
  },
  "question4": {
    "question": "How can they effectively reach their target audience?",
    "context": "Healthcare professionals have specific channels for discovering new products."
  }
}
```

**Response:**
```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "case_type": "Market Entry",
  "lead_type": "Interviewer-Led",
  "difficulty": "Medium",
  "company": "Tech Corp",
  "industry": "Technology",
  "prompt": "Your client is a tech company looking to enter the healthcare market...",
  "image_url": "https://cloudflare-images.com/v1/your-account-id/your-image-id/image.jpg",
  "structure": {
    "question1": {
      "question": "What factors should the client consider when entering this market?",
      "context": "The healthcare market has strict regulations and high barriers to entry."
    },
    "question2": {
      "question": "How should they position their product?",
      "context": "There are already established competitors in this space."
    },
    "question3": {
      "question": "What pricing strategy would you recommend?",
      "context": "Healthcare products have unique pricing considerations."
    },
    "question4": {
      "question": "How can they effectively reach their target audience?",
      "context": "Healthcare professionals have specific channels for discovering new products."
    }
  },
  "version": "1.0",
  "created_at": "2023-01-01T12:00:00Z",
  "updated_at": "2023-01-01T12:00:00Z"
}
```

**Example:**
```javascript
const createTemplate = async (templateData) => {
  const response = await fetch('https://casepreparedcrud.onrender.com/api/v1/templates/admin', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(templateData)
  });
  
  return response.json();
};
```

### Standard Template Creation Endpoint

Alternatively, you can use the standard endpoint if you prefer to structure the data manually:

**Endpoint:** `POST /api/v1/templates`

**Request Body:**
```json
{
  "case_type": "Market Entry",
  "lead_type": "Interviewer-Led",
  "difficulty": "Medium",
  "company": "Tech Corp",
  "industry": "Technology",
  "prompt": "Your client is a tech company looking to enter the healthcare market...",
  "image_url": "https://cloudflare-images.com/v1/your-account-id/your-image-id/image.jpg",
  "structure": {
    "question1": {
      "question": "What factors should the client consider when entering this market?",
      "context": "The healthcare market has strict regulations and high barriers to entry."
    },
    "question2": {
      "question": "How should they position their product?",
      "context": "There are already established competitors in this space."
    },
    "question3": {
      "question": "What pricing strategy would you recommend?",
      "context": "Healthcare products have unique pricing considerations."
    },
    "question4": {
      "question": "How can they effectively reach their target audience?",
      "context": "Healthcare professionals have specific channels for discovering new products."
    }
  },
  "version": "1.0"
}
```

## Updating Templates

**Endpoint:** `PUT /api/v1/templates/{template_id}`

**Authentication Required:** Yes

**Path Parameters:**
- `template_id`: UUID of the template to update

**Request Body:**
All fields are optional, only include the ones you want to update:
```json
{
  "case_type": "Market Sizing",
  "lead_type": "Candidate-Led",
  "difficulty": "Hard",
  "company": "New Company",
  "industry": "New Industry",
  "prompt": "Updated prompt...",
  "image_url": "https://cloudflare-images.com/v1/your-account-id/your-new-image-id/image.jpg",
  "structure": {
    "question1": {
      "question": "Updated question 1?",
      "context": "Updated context 1."
    },
    "question2": {
      "question": "Updated question 2?",
      "context": "Updated context 2."
    },
    "question3": {
      "question": "Updated question 3?",
      "context": "Updated context 3."
    },
    "question4": {
      "question": "Updated question 4?",
      "context": "Updated context 4."
    }
  },
  "version": "1.1"
}
```

**Response:**
Returns the updated template object.

## Deleting Templates

**Endpoint:** `DELETE /api/v1/templates/{template_id}`

**Authentication Required:** Yes

**Path Parameters:**
- `template_id`: UUID of the template to delete

**Response:**
```json
{
  "success": true
}
```

## Data Model

### Question Structure

Each template must have exactly 4 questions, with each question having:

| Field | Type | Description |
|-------|------|-------------|
| question | string | The question to ask the interviewee |
| context | string | Background information or hints for the interviewer |

### Template Structure

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| case_type | string | Type of case (e.g., Market Entry, Profitability) | Yes |
| lead_type | string | Who leads the case (e.g., Interviewer-Led, Candidate-Led) | Yes |
| difficulty | string | Difficulty level (e.g., Easy, Medium, Hard) | Yes |
| company | string | Company the case is about | No |
| industry | string | Industry the case is in | No |
| prompt | string | Main case prompt/description | Yes |
| image_url | string | URL to the image for the case | No |
| structure | object | Contains 4 questions with context | Yes |
| version | string | Version of the template | No (defaults to "1.0") |

## Example: Complete Flow

```javascript
// 1. Upload an image
const imageFile = document.getElementById('imageUpload').files[0];
const imageUrl = await uploadImage(imageFile);

// 2. Create a template with the image URL
const templateData = {
  case_type: "Market Entry",
  lead_type: "Interviewer-Led",
  difficulty: "Medium",
  company: "Tech Corp",
  industry: "Technology",
  prompt: "Your client is a tech company looking to enter the healthcare market...",
  image_url: imageUrl,
  question1: {
    question: "What factors should the client consider when entering this market?",
    context: "The healthcare market has strict regulations and high barriers to entry."
  },
  question2: {
    question: "How should they position their product?",
    context: "There are already established competitors in this space."
  },
  question3: {
    question: "What pricing strategy would you recommend?",
    context: "Healthcare products have unique pricing considerations."
  },
  question4: {
    question: "How can they effectively reach their target audience?",
    context: "Healthcare professionals have specific channels for discovering new products."
  }
};

const newTemplate = await createTemplate(templateData);
console.log('Created template with ID:', newTemplate.id);
``` 