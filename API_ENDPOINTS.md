# BanglaChatPro API Endpoints Documentation

## Main Application Endpoints

### Chat Interface
- **GET** `/` - Main BanglaChatPro chat interface
- **GET** `/conversation/<id>/` - View specific conversation
- **GET** `/start/` - Start new conversation

### Admin Dashboard
- **GET** `/admin-dashboard/` - Custom admin dashboard
- **GET** `/admin/` - Django admin interface

### Account Management
- **GET** `/accounts/login/` - User login
- **GET** `/accounts/register/` - User registration
- **GET** `/accounts/logout/` - User logout

## API Endpoints

### Core Chat API
- **POST** `/api/chat/` - Send message and get AI response
  ```json
  {
    "client_id": 1,
    "user_name": "User Name",
    "message": "আপনার বার্তা"
  }
  ```

### Voice API
- **POST** `/api/voice/` - Process voice input and return audio response
  ```json
  {
    "client_id": 1,
    "caller_name": "Caller Name",
    "question": "Voice question"
  }
  ```

### Rating API
- **POST** `/api/rate/` - Rate a conversation
  ```json
  {
    "conversation_id": 123,
    "rating": 5
  }
  ```

### Human Handoff API
- **POST** `/api/handoff/` - Request human handoff
  ```json
  {
    "conversation_id": 123,
    "reason": "AI failed to understand"
  }
  ```

### Order Management API
- **GET** `/api/orders/<order_id>/` - Get mock order status

### Client Management API
- **GET** `/api/clients/` - List all active clients
- **POST** `/api/clients/` - Create new client
  ```json
  {
    "name": "Client Name",
    "domain": "client.com",
    "contact_email": "contact@client.com"
  }
  ```

### Intent Management API
- **GET** `/api/intents/?client_id=1` - List intents for a client
- **POST** `/api/intents/` - Create new intent
  ```json
  {
    "client_id": 1,
    "name": "Intent Name",
    "training_phrase": "Training phrase",
    "ai_response_template": "Response template"
  }
  ```

## Additional Features

### Voice Features
- **GET** `/voice/` - Voice interface
- **POST** `/voice/upload/` - Upload voice recording
- **POST** `/voice/synthesize/` - Synthesize speech

### Social Media Integration
- **GET** `/social/accounts/` - Social media accounts
- **POST** `/social/webhook/facebook/<org_id>/` - Facebook webhook
- **POST** `/social/webhook/twitter/<org_id>/` - Twitter webhook
- **POST** `/social/webhook/instagram/<org_id>/` - Instagram webhook

### Client Onboarding
- **GET** `/onboarding/` - Onboarding dashboard
- **GET** `/onboarding/step/<step_name>/` - Specific onboarding step
- **GET** `/onboarding/tickets/` - Support tickets

## Response Formats

### Success Response
```json
{
  "conversation_id": 123,
  "ai_response": "AI response in Bangla",
  "confidence": 0.95,
  "is_escalated": false,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Error Response
```json
{
  "error": "Error message",
  "status": 400
}
```

## Authentication

Most API endpoints require authentication. Use one of these methods:

1. **Token Authentication**: Include `Authorization: Token <token>` header
2. **Session Authentication**: Login via `/accounts/login/` first
3. **Basic Authentication**: Include `Authorization: Basic <base64>` header

## Rate Limiting

- Chat API: 60 requests per minute
- Voice API: 30 requests per minute
- Other APIs: 100 requests per hour

## CORS Configuration

Allowed origins:
- `http://localhost:3000`
- `http://127.0.0.1:3000`
- `https://bdchatpro.com`
- `https://www.bdchatpro.com`
