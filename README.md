# CasePrepared CRUD Microservice

This repository contains the CRUD (Create, Read, Update, Delete) microservice for the CasePrepared platform. The microservice is responsible for managing persistent, relational data including user authentication, subscription management, and interview session tracking.

## Features

- **User Authentication & Profile Management**
  - User registration and login (email/password or Google OAuth)
  - Password security using bcrypt
  - User profile management

- **Payments & Subscriptions**
  - Stripe integration for payment processing
  - Subscription management (creation, updates, cancellation)
  - Webhook handling for subscription events

- **Interview Creation & Management**
  - Creating and managing interview sessions
  - Template-based interview creation
  - Progress tracking for interviews

- **Credential Generation**
  - Ephemeral session keys for realtime interviews
  - TURN/STUN server credentials for WebRTC

## Tech Stack

- **FastAPI**: Modern, high-performance web framework
- **SQLAlchemy**: ORM for database interactions
- **Pydantic**: Data validation and settings management
- **PostgreSQL**: Relational database
- **Alembic**: Database migration tool
- **JWT**: Authentication mechanism
- **Stripe**: Payment processing

## Getting Started

### Prerequisites

- Python 3.8 or higher
- PostgreSQL
- Stripe account (for payment processing)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/caseprepared-crud.git
   cd caseprepared-crud
   ```

2. Create a virtual environment and install dependencies:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Create a `.env` file based on `.env.example` and fill in your configuration details:
   ```
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. Create the database:
   ```
   # In PostgreSQL
   CREATE DATABASE caseprepared_db;
   ```

5. Run the migrations:
   ```
   alembic upgrade head
   ```

6. Initialize the database with initial data:
   ```
   python -m scripts.init_db
   ```

7. Run the application:
   ```
   uvicorn app.main:app --reload
   ```

### Creating a superuser

To create a superuser (admin):

```
python -m scripts.create_superuser <email> <password> <full_name>
```

## API Documentation

Once the application is running, you can access the OpenAPI documentation at:

```
http://localhost:8000/api/v1/docs
```

This provides a detailed overview of all available endpoints, request/response schemas, and allows interactive testing of the API.

## Database Structure

The service uses four main database tables:

1. **Users**: Stores user credentials and profile information
2. **Subscriptions**: Tracks user subscription status and payment details
3. **Interview Templates**: Contains the blueprints for case interviews
4. **Interviews**: Records each interview session and tracks progress

## License

[MIT License](LICENSE) 