# CasePrepared Admin Interface Guide

This document provides specific guidance for frontend developers building the admin interface for the CasePrepared application. It assumes admins already have accounts set up in the system.

## Base URLs

- **Development**: `http://localhost:8000`
- **Production**: `https://casepreparedcrud.onrender.com`

All endpoints are prefixed with `/api/v1`.

## Admin Authentication

### Admin Login

Admin users log in through the standard login endpoint:

**Endpoint:** `POST /api/v1/auth/login`

**Request Body (form-data):**
```
username=admin@example.com&password=adminpassword
```

**Content-Type:** `application/x-www-form-urlencoded`

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Using Authentication Tokens

Include the JWT token in the Authorization header for all admin API requests:

```
Authorization: Bearer YOUR_ADMIN_ACCESS_TOKEN
```

## Identifying Admin Users

To determine if a user is an admin, check the `is_admin` field in the user object returned from the `/api/v1/users/me` endpoint:

```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "email": "admin@example.com",
  "full_name": "Admin User",
  "is_admin": true,
  "created_at": "2023-01-01T12:00:00Z",
  "updated_at": "2023-01-01T12:00:00Z"
}
```

### Admin Privileges

Admin users have the following privileges:

1. **No Subscription Required**: Admins can access all endpoints without an active subscription
2. **Access to All Templates**: Admins can create, edit, and delete interview templates
3. **Access to All Interviews**: Admins can view, update, and delete any user's interviews
4. **User Management**: Admins can view all user information

## Admin-Only Endpoints

### Template Management Endpoints

#### 1. List All Interview Templates

**Endpoint:** `GET /api/v1/templates/`

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

**Endpoint:** `GET /api/v1/templates/{template_id}`

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

**Endpoint:** `POST /api/v1/templates/`

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

**Endpoint:** `PUT /api/v1/templates/{template_id}`

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

**Endpoint:** `DELETE /api/v1/templates/{template_id}`

**Authentication Required:** Yes (Admin only)

**Response:** No content (204)

## Interview Management Endpoints

In addition to template management, administrators may need to view and manage user interviews. Here are the relevant endpoints:

### 1. List All Interviews (Admin View)

**Endpoint:** `GET /api/v1/interviews/`

**Authentication Required:** Yes

**Query Parameters:**
- `skip`: Number of records to skip (pagination)
- `limit`: Maximum number of records to return
- `status`: Filter by status (scheduled, completed, canceled)
- `user_id`: Filter by specific user (admin only)

**Response:**
```json
[
  {
    "id": "5fa85f64-5717-4562-b3fc-2c963f66afa8",
    "user_id": "2fa85f64-5717-4562-b3fc-2c963f66afa9",
    "template_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "scheduled_at": "2023-01-15T14:00:00Z",
    "status": "scheduled",
    "created_at": "2023-01-01T12:00:00Z",
    "updated_at": "2023-01-01T12:00:00Z"
  },
  {
    "id": "6fa85f64-5717-4562-b3fc-2c963f66afa8",
    "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa9",
    "template_id": "4fa85f64-5717-4562-b3fc-2c963f66afa7",
    "scheduled_at": "2023-01-16T15:00:00Z",
    "status": "completed",
    "created_at": "2023-01-01T13:00:00Z",
    "updated_at": "2023-01-17T16:00:00Z"
  }
]
```

### 2. Get Interview Details

**Endpoint:** `GET /api/v1/interviews/{interview_id}`

**Authentication Required:** Yes

**Note:** Admins can access any interview, while regular users can only access their own interviews.

**Response:**
```json
{
  "id": "5fa85f64-5717-4562-b3fc-2c963f66afa8",
  "user_id": "2fa85f64-5717-4562-b3fc-2c963f66afa9",
  "template_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "scheduled_at": "2023-01-15T14:00:00Z",
  "status": "scheduled",
  "feedback": {
    "overall_score": 8,
    "strengths": "Clear structured approach. Good market sizing.",
    "areas_for_improvement": "Could improve on handling objections.",
    "notes": "Candidate showed strong analytical skills."
  },
  "created_at": "2023-01-01T12:00:00Z",
  "updated_at": "2023-01-01T12:00:00Z"
}
```

### 3. Update Interview Status/Feedback (Admin)

**Endpoint:** `PATCH /api/v1/interviews/{interview_id}`

**Authentication Required:** Yes (Admin can update any interview)

**Request Body:**
```json
{
  "status": "completed",
  "feedback": {
    "overall_score": 8,
    "strengths": "Clear structured approach. Good market sizing.",
    "areas_for_improvement": "Could improve on handling objections.",
    "notes": "Candidate showed strong analytical skills."
  }
}
```

**Response:** Same as interview details response above with updated information.

### 4. Delete Interview

**Endpoint:** `DELETE /api/v1/interviews/{interview_id}`

**Authentication Required:** Yes (Admin or owner of the interview)

**Response:** No content (204)

## Admin UI Implementation Guide

### Admin Dashboard Architecture

1. **Admin Login Flow**:
   ```javascript
   const handleLogin = async (email, password) => {
     try {
       const formData = new URLSearchParams();
       formData.append('username', email);
       formData.append('password', password);
       
       const response = await axios.post(
         `${API_BASE_URL}/auth/login`, 
         formData.toString(),
         {
           headers: {
             'Content-Type': 'application/x-www-form-urlencoded'
           }
         }
       );
       
       // Store the token
       const { access_token } = response.data;
       localStorage.setItem('access_token', access_token);
       
       // Check if user is admin
       const userResponse = await axios.get(`${API_BASE_URL}/users/me`, {
         headers: {
           'Authorization': `Bearer ${access_token}`
         }
       });
       
       if (userResponse.data.is_admin) {
         // Redirect to admin dashboard
         navigate('/admin/dashboard');
       } else {
         // Not an admin
         alert('Admin access required');
       }
     } catch (error) {
       console.error('Login failed:', error);
     }
   };
   ```

2. **Admin Authentication Guard**:
   ```javascript
   // Component to protect admin routes
   function AdminRoute({ children }) {
     const [isAdmin, setIsAdmin] = useState(false);
     const [loading, setLoading] = useState(true);
     
     useEffect(() => {
       const checkAdminStatus = async () => {
         try {
           const token = localStorage.getItem('access_token');
           if (!token) {
             navigate('/login');
             return;
           }
           
           const response = await axios.get(`${API_BASE_URL}/users/me`, {
             headers: {
               'Authorization': `Bearer ${token}`
             }
           });
           
           if (response.data.is_admin) {
             setIsAdmin(true);
           } else {
             navigate('/unauthorized');
           }
         } catch (error) {
           console.error('Error checking admin status:', error);
           navigate('/login');
         } finally {
           setLoading(false);
         }
       };
       
       checkAdminStatus();
     }, []);
     
     if (loading) return <div>Loading...</div>;
     return isAdmin ? children : null;
   }
   ```

### Template Management Implementation

#### Template List Component

```javascript
// Example using React and Axios

import axios from 'axios';
import { useState, useEffect } from 'react';

const API_BASE_URL = 'https://casepreparedcrud.onrender.com/api/v1';

function AdminTemplateList() {
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    case_type: '',
    difficulty: '',
    industry: ''
  });

  useEffect(() => {
    fetchTemplates();
  }, [filters]);
  
  const fetchTemplates = async () => {
    try {
      const token = localStorage.getItem('access_token');
      
      // Build query params for filtering
      const queryParams = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value) queryParams.append(key, value);
      });
      
      const response = await axios.get(
        `${API_BASE_URL}/templates?${queryParams.toString()}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );
      
      setTemplates(response.data);
      setLoading(false);
    } catch (err) {
      setError('Failed to fetch templates');
      setLoading(false);
      console.error('Error fetching templates:', err);
    }
  };

  const handleDelete = async (templateId) => {
    if (!window.confirm('Are you sure you want to delete this template?')) {
      return;
    }
    
    try {
      const token = localStorage.getItem('access_token');
      
      await axios.delete(`${API_BASE_URL}/templates/${templateId}`, {
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
      
      {/* Filter controls */}
      <div className="filter-controls">
        <select 
          value={filters.case_type} 
          onChange={(e) => setFilters({...filters, case_type: e.target.value})}
        >
          <option value="">All Case Types</option>
          <option value="Market Entry">Market Entry</option>
          <option value="Profitability">Profitability</option>
          <option value="Pricing">Pricing</option>
          <option value="Growth Strategy">Growth Strategy</option>
        </select>
        
        <select 
          value={filters.difficulty} 
          onChange={(e) => setFilters({...filters, difficulty: e.target.value})}
        >
          <option value="">All Difficulties</option>
          <option value="Easy">Easy</option>
          <option value="Medium">Medium</option>
          <option value="Hard">Hard</option>
        </select>
        
        <select 
          value={filters.industry} 
          onChange={(e) => setFilters({...filters, industry: e.target.value})}
        >
          <option value="">All Industries</option>
          <option value="Technology">Technology</option>
          <option value="Healthcare">Healthcare</option>
          <option value="Retail">Retail</option>
          <option value="Finance">Finance</option>
        </select>
      </div>
      
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

#### Template Edit/Create Form

```javascript
function TemplateForm({ templateId }) {
  const [loading, setLoading] = useState(templateId ? true : false);
  const [error, setError] = useState(null);
  const [template, setTemplate] = useState({
    case_type: '',
    lead_type: '',
    difficulty: '',
    company: '',
    industry: '',
    prompt: '',
    structure: {
      question1: { prompt: '', context: '' },
      question2: { prompt: '', context: '' },
      question3: { prompt: '', context: '' },
      question4: { prompt: '', context: '' }
    },
    image_url: '',
    version: '1.0'
  });

  useEffect(() => {
    if (templateId) {
      fetchTemplate(templateId);
    }
  }, [templateId]);

  const fetchTemplate = async (id) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.get(`${API_BASE_URL}/templates/${id}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      setTemplate(response.data);
      setLoading(false);
    } catch (err) {
      setError('Failed to fetch template');
      setLoading(false);
      console.error('Error fetching template:', err);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setTemplate({
      ...template,
      [name]: value
    });
  };

  const handleStructureChange = (questionNum, field, value) => {
    setTemplate({
      ...template,
      structure: {
        ...template.structure,
        [questionNum]: {
          ...template.structure[questionNum],
          [field]: value
        }
      }
    });
  };

  const handleImageUpload = async (file) => {
    // In a real app, you would upload the image to a storage service
    // and get back a URL
    const imageUrl = await uploadImage(file);
    setTemplate({
      ...template,
      image_url: imageUrl
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      const token = localStorage.getItem('access_token');
      
      if (templateId) {
        // Update existing template
        await axios.put(
          `${API_BASE_URL}/templates/${templateId}`,
          template,
          {
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            }
          }
        );
      } else {
        // Create new template
        await axios.post(
          `${API_BASE_URL}/templates`,
          template,
          {
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            }
          }
        );
      }
      
      // Redirect back to templates list
      navigate('/admin/templates');
    } catch (err) {
      setError('Failed to save template');
      console.error('Error saving template:', err);
    }
  };

  if (loading) return <div>Loading template...</div>;
  
  return (
    <div className="template-form">
      <h2>{templateId ? 'Edit' : 'Create'} Interview Template</h2>
      
      {error && <div className="error">{error}</div>}
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="case_type">Case Type</label>
          <input
            type="text"
            id="case_type"
            name="case_type"
            value={template.case_type}
            onChange={handleChange}
            required
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="lead_type">Lead Type</label>
          <select
            id="lead_type"
            name="lead_type"
            value={template.lead_type}
            onChange={handleChange}
            required
          >
            <option value="">Select Lead Type</option>
            <option value="Interviewer-led">Interviewer-led</option>
            <option value="Candidate-led">Candidate-led</option>
          </select>
        </div>
        
        <div className="form-group">
          <label htmlFor="difficulty">Difficulty</label>
          <select
            id="difficulty"
            name="difficulty"
            value={template.difficulty}
            onChange={handleChange}
            required
          >
            <option value="">Select Difficulty</option>
            <option value="Easy">Easy</option>
            <option value="Medium">Medium</option>
            <option value="Hard">Hard</option>
          </select>
        </div>
        
        <div className="form-group">
          <label htmlFor="company">Company (Optional)</label>
          <input
            type="text"
            id="company"
            name="company"
            value={template.company || ''}
            onChange={handleChange}
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="industry">Industry (Optional)</label>
          <input
            type="text"
            id="industry"
            name="industry"
            value={template.industry || ''}
            onChange={handleChange}
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="prompt">Main Prompt</label>
          <textarea
            id="prompt"
            name="prompt"
            value={template.prompt}
            onChange={handleChange}
            rows="6"
            required
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="image_url">Image URL</label>
          <input
            type="text"
            id="image_url"
            name="image_url"
            value={template.image_url || ''}
            onChange={handleChange}
          />
          <div className="image-upload">
            <input
              type="file"
              accept="image/*"
              onChange={(e) => handleImageUpload(e.target.files[0])}
            />
            {template.image_url && (
              <img 
                src={template.image_url} 
                alt="Template" 
                className="preview" 
                width="150" 
              />
            )}
          </div>
        </div>
        
        <h3>Question Structure</h3>
        
        {Object.keys(template.structure).map((questionKey) => (
          <div className="question-section" key={questionKey}>
            <h4>{questionKey.replace(/([A-Z])/g, ' $1').toLowerCase()}</h4>
            
            <div className="form-group">
              <label htmlFor={`${questionKey}-prompt`}>Question Prompt</label>
              <textarea
                id={`${questionKey}-prompt`}
                value={template.structure[questionKey].prompt}
                onChange={(e) => handleStructureChange(questionKey, 'prompt', e.target.value)}
                rows="3"
                required
              />
            </div>
            
            <div className="form-group">
              <label htmlFor={`${questionKey}-context`}>Context (for interviewers)</label>
              <textarea
                id={`${questionKey}-context`}
                value={template.structure[questionKey].context}
                onChange={(e) => handleStructureChange(questionKey, 'context', e.target.value)}
                rows="3"
                required
              />
            </div>
          </div>
        ))}
        
        <div className="form-actions">
          <button type="button" onClick={() => navigate('/admin/templates')}>
            Cancel
          </button>
          <button type="submit">
            {templateId ? 'Update' : 'Create'} Template
          </button>
        </div>
      </form>
    </div>
  );
}
```

### Error Handling

The API returns standard HTTP status codes with error details:

```json
{
  "detail": "Error message describing what went wrong"
}
```

Common error codes:

- `401 Unauthorized`: Invalid or missing authentication token
- `403 Forbidden`: Insufficient permissions (non-admin attempting admin actions)
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error

## Template Data Model Reference

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

## Best Practices for Admin Interface

1. **Image Handling**:
   - Use a service like AWS S3, Cloudinary, or Firebase Storage for image uploads
   - Consider implementing an image cropping/resizing tool
   - Validate file types and sizes before upload

2. **Form Validation**:
   - Implement client-side validation before submitting to API
   - Handle server validation errors appropriately
   - Provide clear error messages to admin users

3. **Performance Considerations**:
   - Implement pagination for template lists
   - Use filtering to limit results when applicable
   - Consider caching frequently accessed data

4. **Security Precautions**:
   - Always verify admin status on protected routes
   - Implement session timeouts for admin sessions
   - Log sensitive admin operations
   - Never bypass backend permission checks with frontend-only validations 