# 🔌 BanglaChatPro API Documentation

## Overview

BanglaChatPro provides a comprehensive REST API for managing AI agents, handling conversations, and integrating with various communication platforms.

## Base URL
```
https://api.banglachatpro.com
```

## Authentication

All API requests require authentication using JWT tokens in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

### Login to get JWT token

```bash
POST /auth/token
Content-Type: application/x-www-form-urlencoded

username=your_username&password=your_password
```

## Core Endpoints

### AI Agents Management

#### List AI Agents
```http
GET /organizations/ai-agents
```

#### Create AI Agent
```http
POST /organizations/ai-agents
Content-Type: application/json

{
  "name": "Customer Support Agent",
  "description": "Handles customer inquiries",
  "system_prompt": "You are a helpful customer support agent...",
  "model_name": "gpt-4",
  "temperature": 0.7
}
```

#### Update AI Agent Customization
```http
PUT /organizations/ai-agents/{agent_id}/customization
Content-Type: application/json

{
  "response_tone": "friendly",
  "language_preference": "bn",
  "custom_instructions": "Always be polite and use formal Bangla"
}
```

### Chat & Conversations

#### Send Message to AI Agent
```http
POST /chat/agents/{agent_id}/chat
Content-Type: application/json

{
  "message": "Hello, I need help with my order",
  "conversation_id": null
}
```

#### Get Conversation History
```http
GET /chat/conversations/{conversation_id}/messages
```

### IVR (Interactive Voice Response)

#### Get IVR Calls
```http
GET /ivr/calls/{organization_id}?page=1&limit=50
```

#### Get IVR Analytics
```http
GET /ivr/analytics/{organization_id}
```

#### Generate Twilio Token
```http
GET /ivr/token
```

### Social Media Integrations

#### Configure WhatsApp
```http
PUT /organizations/ai-agents/{agent_id}/integrations/whatsapp
Content-Type: application/json

{
  "phone_number": "+8801234567890",
  "access_token": "your-whatsapp-access-token",
  "verify_token": "your-verify-token"
}
```

#### Configure Facebook Messenger
```http
PUT /organizations/ai-agents/{agent_id}/integrations/facebook
Content-Type: application/json

{
  "page_id": "your-facebook-page-id",
  "access_token": "your-facebook-access-token",
  "verify_token": "your-verify-token"
}
```

#### Configure Instagram
```http
PUT /organizations/ai-agents/{agent_id}/integrations/instagram
Content-Type: application/json

{
  "account_id": "your-instagram-account-id",
  "access_token": "your-instagram-access-token",
  "verify_token": "your-verify-token"
}
```

### Webhook Endpoints

#### WhatsApp Webhook
```http
POST /chat/webhooks/whatsapp
```

#### Facebook Webhook
```http
POST /chat/webhooks/facebook
```

#### Instagram Webhook
```http
POST /chat/webhooks/instagram
```

#### Twilio IVR Webhook
```http
POST /ivr/webhook/incoming-call
```

## Response Formats

### Success Response
```json
{
  "status": "success",
  "data": { ... },
  "message": "Operation completed successfully"
}
```

### Error Response
```json
{
  "status": "error",
  "message": "Error description",
  "code": "ERROR_CODE"
}
```

## Rate Limits

- **Authenticated requests**: 100 requests per minute per IP
- **Webhook requests**: 1000 requests per minute
- **File uploads**: 10 MB per file, 50 files per hour

## SDKs & Libraries

### JavaScript/Node.js
```javascript
const BanglaChatPro = require('banglachatpro-sdk');

const client = new BanglaChatPro({
  apiKey: 'your-api-key',
  baseUrl: 'https://api.banglachatpro.com'
});

// Send a message
const response = await client.chat.sendMessage({
  agentId: 'agent_123',
  message: 'Hello!'
});
```

### Python
```python
from banglachatpro import BanglaChatPro

client = BanglaChatPro(
    api_key='your-api-key',
    base_url='https://api.banglachatpro.com'
)

# Send a message
response = client.chat.send_message(
    agent_id='agent_123',
    message='Hello!'
)
```

## Error Codes

| Code | Description |
|------|-------------|
| `AUTH_001` | Invalid or expired token |
| `AUTH_002` | Insufficient permissions |
| `AGENT_001` | Agent not found |
| `AGENT_002` | Agent not active |
| `CHAT_001` | Invalid message format |
| `WEBHOOK_001` | Invalid webhook signature |
| `RATE_001` | Rate limit exceeded |

## Webhook Security

All webhook requests include signature verification. Verify the signature using:

```python
import hmac
import hashlib

def verify_signature(payload, signature, secret):
    expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(signature, expected)
```

## Support

For API support, contact:
- Email: api-support@banglachatpro.com
- Documentation: https://docs.banglachatpro.com
- Status Page: https://status.banglachatpro.com
