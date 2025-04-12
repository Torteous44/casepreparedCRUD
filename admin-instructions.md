# CasePrepared Admin Interface

## Overview
The CasePrepared Admin Interface allows administrators to manage interview templates, upload images, and perform other administrative tasks.

## Authentication
All admin endpoints are protected with an admin password. When making requests to admin endpoints, you must include the admin password in the Authorization header:

```
Authorization: Bearer CasePreparedAdmin2025!
```

## Admin Features

### Managing Templates
- **Create Template**: Admin can create new interview templates using structured questions and prompts
- **Update Template**: Modify existing templates
- **Delete Template**: Remove templates from the system

### Image Management
- **Upload Images**: Securely upload images to Cloudflare for use in templates
- **Get Upload URL**: Get a direct upload URL for client-side image uploads

## API Endpoints

### Interview Templates
- `POST /api/v1/interview-templates/`: Create a new template
- `POST /api/v1/interview-templates/admin`: Create a template with structured questions
- `PUT /api/v1/interview-templates/{template_id}`: Update an existing template
- `DELETE /api/v1/interview-templates/{template_id}`: Delete a template

### Images
- `POST /api/v1/images/upload-url`: Get a direct upload URL
- `POST /api/v1/images/upload`: Upload an image from the server

## Example Usage

### Creating a New Template
```json
POST /api/v1/interview-templates/admin
Authorization: Bearer CasePreparedAdmin2025!

{
  "case_type": "Market Entry",
  "lead_type": "Interviewer-led",
  "difficulty": "Medium",
  "company": "Tech Corp",
  "industry": "Technology",
  "prompt": "Your client is a technology company looking to enter the European market...",
  "image_url": "https://imagedelivery.net/example/image.jpg",
  "version": "1.0",
  "question1": {
    "question": "What factors should the client consider when entering this market?",
    "context": "Think about competition, market size, and regulations."
  },
  "question2": {
    "question": "How would you segment this market?",
    "context": "Consider different customer types and needs."
  },
  "question3": {
    "question": "What is your recommended entry strategy?",
    "context": "Options include acquisition, partnership, or organic growth."
  },
  "question4": {
    "question": "What risks should the client be aware of?",
    "context": "Think about financial, operational, and regulatory risks."
  }
}
```

### Uploading an Image
```
POST /api/v1/images/upload
Authorization: Bearer CasePreparedAdmin2025!
Content-Type: multipart/form-data

[file content]
```

## Security Notes
- Keep the admin password secure and change it regularly
- All admin actions are logged for security purposes
- Only share admin access with trusted team members 