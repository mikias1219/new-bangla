# Bangla Chat Pro - AI SaaS Platform

A complete multi-tenant SaaS platform for AI-powered customer chatbots with WhatsApp and Facebook Messenger integration.

## 🚀 Features

### Core Features
- ✅ **Multi-tenant Architecture** - Complete data isolation per client
- ✅ **AI Training Pipeline** - Upload documents to train custom AI agents
- ✅ **Real-time Chat Interface** - Web-based chat with AI agents
- ✅ **Document Processing** - Support for PDF, DOCX, TXT, CSV files
- ✅ **Vector Embeddings** - Semantic search using OpenAI embeddings
- ✅ **Conversation History** - Complete chat history and analytics
- ✅ **Admin Dashboard** - Platform management interface

### Integrations
- ✅ **WhatsApp Business API** - Automated WhatsApp responses
- ✅ **Facebook Messenger** - Facebook page integration
- ✅ **Webhook Support** - Real-time message processing

### SaaS Features
- ✅ **Subscription Plans** - Starter, Professional, Enterprise tiers
- ✅ **Usage Tracking** - Monthly chat limits and analytics
- ✅ **Billing System** - Stripe integration ready
- ✅ **Client Management** - Organization and user management

## 🏗️ Architecture

```
Frontend (Next.js)          Backend (FastAPI)
├── Dashboard              ├── Multi-tenant API
├── Chat Interface         ├── AI Training Service
├── Admin Panel            ├── WhatsApp/Facebook Webhooks
└── Client Management      ├── Analytics & Billing

Database (SQLite/PostgreSQL)
├── Organizations          ├── AI Agents
├── Training Documents     ├── Conversations
├── Messages              ├── Payments
└── Analytics
```

## 📋 Prerequisites

- Python 3.8+
- Node.js 18+
- SQLite (or PostgreSQL for production)
- OpenAI API key
- WhatsApp Business API (optional)
- Facebook App (optional)
- Stripe account (optional)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <your-repo-url>
cd bangla-chat-pro

# Run setup script
python3 setup_environment.py
```

### 2. Configure Environment

Edit `.env` file with your API keys:
```env
OPENAI_API_KEY=your_openai_api_key
WHATSAPP_ACCESS_TOKEN=your_whatsapp_token
FACEBOOK_ACCESS_TOKEN=your_facebook_token
STRIPE_SECRET_KEY=your_stripe_key
```

### 3. Initialize Database

```bash
cd backend

# Migrate to multi-tenant architecture
python migrate_to_multi_tenant.py

# Create admin user
python create_admin.py
```

### 4. Start Services

```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate
pip install -r requirements.txt
python run.py

# Terminal 2 - Frontend
npm install
npm run dev
```

### 5. Access Application

- **Frontend**: http://localhost:3002
- **Admin Dashboard**: http://localhost:3002/admin
- **API Documentation**: http://localhost:8000/docs

## 🎯 Usage Guide

### For SaaS Owners (Platform Admins)

1. **Access Admin Dashboard**
   - Login with admin credentials
   - Manage organizations and users
   - View platform analytics

2. **Create Client Organizations**
   ```bash
   # Admin creates organization for new client
   curl -X POST https://yourdomain.com/api/organizations/ \
     -H "Authorization: Bearer <admin_token>" \
     -d '{"name": "Client Corp", "domain": "clientcorp"}'
   ```

3. **Monitor Usage**
   - Track chat volumes per client
   - Monitor AI agent performance
   - View revenue analytics

### For Clients (Organization Owners)

1. **Setup Organization**
   - Login to dashboard
   - Configure organization settings

2. **Train AI Agents**
   - Upload training documents (PDF, DOCX, TXT)
   - Create AI agents with custom personalities
   - Test agents in chat interface

3. **Configure Integrations**
   ```bash
   # Configure WhatsApp
   curl -X PUT https://yourdomain.com/api/organizations/ai-agents/1/integrations/whatsapp \
     -H "Authorization: Bearer <token>" \
     -d '{"phone_number": "+1234567890"}'

   # Configure Facebook
   curl -X PUT https://yourdomain.com/api/organizations/ai-agents/1/integrations/facebook \
     -H "Authorization: Bearer <token>" \
     -d '{"page_id": "your_page_id"}'
   ```

4. **Monitor Performance**
   - View conversation analytics
   - Track response quality
   - Monitor usage limits

## 💰 Pricing & Monetization

### Subscription Plans

| Plan | Monthly Price | AI Agents | Monthly Chats | Features |
|------|---------------|-----------|----------------|----------|
| **Starter** | $29 | 1 | 1,000 | Basic training, web chat |
| **Professional** | $99 | 3 | 5,000 | All integrations, analytics |
| **Enterprise** | $299 | Unlimited | 25,000 | Custom features, priority support |

### Revenue Streams

1. **Subscription Fees** - Monthly recurring revenue
2. **Overage Charges** - Extra chats beyond plan limits
3. **Premium Integrations** - WhatsApp/Facebook add-ons
4. **Custom Training** - Enterprise document processing
5. **White-label Solutions** - Custom branding

## 🔧 API Reference

### Core Endpoints

#### Authentication
```bash
POST /auth/token          # Login
POST /auth/register       # Register new user
```

#### Organization Management
```bash
GET  /organizations/my                    # Get current org
POST /organizations/ai-agents             # Create AI agent
GET  /organizations/ai-agents             # List AI agents
POST /organizations/documents/upload      # Upload training docs
```

#### Chat & AI
```bash
POST /chat/agents/{id}/chat              # Send message to AI
GET  /chat/conversations                 # Get conversations
GET  /analytics/conversations/overview   # Chat analytics
```

#### Integrations
```bash
POST /chat/webhooks/whatsapp             # WhatsApp webhook
POST /chat/webhooks/facebook             # Facebook webhook
GET  /chat/webhooks/whatsapp             # WhatsApp verification
GET  /chat/webhooks/facebook             # Facebook verification
```

#### Billing
```bash
GET  /billing/plans                      # Get pricing plans
GET  /billing/subscription               # Current subscription
POST /billing/subscription/change-plan   # Change plan
GET  /billing/payments                   # Payment history
```

## 🚀 Production Deployment

### 1. Server Setup

```bash
# Install dependencies
sudo apt update
sudo apt install python3 python3-pip nodejs npm nginx certbot

# Setup Python virtual environment
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Nginx

```nginx
# /etc/nginx/sites-available/bdchatpro.com
server {
    listen 80;
    server_name bdchatpro.com www.bdchatpro.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name bdchatpro.com www.bdchatpro.com;

    # SSL certificates
    ssl_certificate /etc/letsencrypt/live/bdchatpro.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/bdchatpro.com/privkey.pem;

    # API routes - proxy to FastAPI backend
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Frontend routes - serve Next.js app
    location / {
        proxy_pass http://127.0.0.1:3002;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

### 3. Setup SSL

```bash
# Get SSL certificates
certbot --nginx -d bdchatpro.com -d www.bdchatpro.com

# Setup auto-renewal
crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### 4. Process Management with PM2

```bash
# Install PM2
npm install -g pm2

# Start backend
cd backend
pm2 start --name bangla-chat-backend "source venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4"

# Start frontend
cd ..
npm run build
pm2 start --name bangla-chat-frontend "npm start"

# Save PM2 configuration
pm2 save
pm2 startup
```

### 5. Environment Setup

```bash
# Production environment variables
cp .env .env.production
# Edit .env.production with production values
```

## 🔒 Security Considerations

- **Data Isolation**: Multi-tenant architecture ensures client data separation
- **API Authentication**: JWT tokens with organization scoping
- **File Upload Security**: File type validation and size limits
- **Rate Limiting**: Usage limits prevent abuse
- **Webhook Verification**: Secure webhook endpoints for integrations

## 📊 Monitoring & Analytics

- **Real-time Metrics**: Chat volumes, response times, user satisfaction
- **Usage Tracking**: Monthly limits and overage monitoring
- **Performance Monitoring**: AI agent response quality
- **Revenue Analytics**: Subscription and payment tracking

## 🚨 Troubleshooting

### Common Issues

1. **Admin dashboard not loading**
   ```bash
   # Check nginx configuration
   nginx -t
   systemctl reload nginx
   ```

2. **Database migration issues**
   ```bash
   cd backend
   source venv/bin/activate
   python migrate_to_multi_tenant.py
   ```

3. **AI responses not working**
   - Check OpenAI API key in `.env`
   - Verify document processing completed
   - Check agent training status

4. **Webhook integrations failing**
   - Verify webhook URLs in WhatsApp/Facebook dashboards
   - Check API keys and tokens
   - Review server logs for webhook errors

## 📈 Scaling Considerations

- **Database**: Upgrade to PostgreSQL for production
- **Caching**: Implement Redis for session and API caching
- **File Storage**: Use AWS S3 or similar for document storage
- **Load Balancing**: Multiple backend instances behind nginx
- **Background Jobs**: Use Celery for document processing queues

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: Check this README and API docs
- **Issues**: Create GitHub issues for bugs/features
- **Email**: admin@bdchatpro.com

---

**Built with ❤️ for AI-powered customer service automation**