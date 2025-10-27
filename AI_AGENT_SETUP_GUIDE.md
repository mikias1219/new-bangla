# 🚀 BanglaChatPro - Complete AI Agent System Setup Guide

## 🎯 **Overview**
BanglaChatPro is a comprehensive multi-tenant AI agent platform that provides customer support across multiple channels including voice calls, chat, SMS, and social media. Each client gets their own AI agent that can handle customer inquiries automatically.

## 🏗️ **Architecture**

### **Multi-Tenant System**
- **Organizations**: Each client has their own organization
- **AI Agents**: Customizable AI agents per organization
- **API Keys**: Secure API key management for external services
- **Subscriptions**: Stripe-powered billing system

### **Communication Channels**
- **Voice Calls**: Twilio-powered inbound/outbound calls with speech recognition
- **SMS**: Text messaging support via Twilio
- **Chat**: Web-based chat interface with AI responses
- **Social Media**: Facebook, Twitter, Instagram, WhatsApp integration

---

## 🔧 **Setup Instructions**

### **1. Environment Configuration**

Add these environment variables to your `.env` file:

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-proj-your-openai-key-here

# Twilio Configuration (for voice calls and SMS)
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_PHONE_NUMBER=+1234567890

# Stripe Configuration (for payments)
STRIPE_SECRET_KEY=sk_test_your-stripe-secret-key
STRIPE_PUBLISHABLE_KEY=pk_test_your-stripe-publishable-key
STRIPE_WEBHOOK_SECRET=whsec_your-webhook-secret

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/bangla_chat_pro

# Django Settings
SECRET_KEY=your-django-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

### **2. Install Dependencies**

```bash
pip install -r requirements.txt
```

### **3. Run Migrations**

```bash
python manage.py migrate
```

### **4. Create Superuser**

```bash
python manage.py createsuperuser
```

### **5. Configure Organizations and AI Agents**

```bash
# Access Django admin at /admin/
# Create organizations, AI agents, and configure API keys
```

---

## 📞 **Twilio Voice Call Setup**

### **1. Twilio Account Setup**
1. Sign up at [twilio.com](https://twilio.com)
2. Get your Account SID and Auth Token
3. Purchase a phone number for voice calls

### **2. Configure Webhooks**
Set these webhook URLs in your Twilio console:

```
Voice Webhook: https://yourdomain.com/voice/twilio/voice/{organization_id}/
SMS Webhook: https://yourdomain.com/voice/twilio/sms/{organization_id}/
```

### **3. Add API Keys in Admin**
1. Go to Django Admin → Accounts → API Keys
2. Create new API key with provider "twilio"
3. Enter Account SID as "key" and Auth Token as "name"

### **4. Test Voice Calls**
```bash
# Test inbound call
curl -X POST https://yourdomain.com/voice/twilio/voice/1/ \
  -d "CallSid=test123&From=+1234567890&To=+0987654321"
```

---

## 💳 **Stripe Payment Setup**

### **1. Stripe Account Setup**
1. Sign up at [stripe.com](https://stripe.com)
2. Get your API keys from the dashboard

### **2. Configure Webhooks**
Set webhook URL in Stripe Dashboard:
```
https://yourdomain.com/api/payments/webhook/
```

### **3. Add API Keys in Admin**
1. Go to Django Admin → Accounts → API Keys
2. Create new API key with provider "stripe"
3. Enter your Stripe Secret Key

### **4. Subscription Plans**
Create subscription products in Stripe Dashboard:
- Basic Plan: $29.99/month (100 conversations)
- Premium Plan: $79.99/month (1000 conversations)
- Enterprise Plan: $199.99/month (Unlimited)

---

## 📱 **Social Media Integration Setup**

### **Facebook Messenger Setup**
1. Create Facebook App at [developers.facebook.com](https://developers.facebook.com)
2. Add Messenger product
3. Get Page Access Token
4. Set webhook URL: `https://yourdomain.com/social/webhook/facebook/{organization_id}/`
5. Verify webhook with token: `fb_verify_{organization_id}`

### **Twitter Setup**
1. Create Twitter App at [developer.twitter.com](https://developer.twitter.com)
2. Get API keys and access tokens
3. Set webhook URL for account activity

### **Instagram Setup**
1. Use Facebook Graph API (same as Facebook)
2. Get Instagram Business Account ID
3. Configure webhooks for messages and comments

### **WhatsApp Setup**
1. Apply for WhatsApp Business API
2. Get Business Account ID and Access Token
3. Set webhook URL for message events

---

## 🤖 **AI Agent Configuration**

### **1. Create AI Agent**
1. Go to Django Admin → Chat → AI Agents
2. Create new agent with:
   - Name and description
   - OpenAI model (gpt-3.5-turbo or gpt-4)
   - System prompt for personality
   - Temperature and token limits

### **2. Training Intents**
1. Add intents for common customer queries
2. Provide training examples
3. Configure response templates

### **3. Voice Settings**
- Enable voice features
- Set voice type (male/female/neutral)
- Configure speech synthesis language

### **4. Social Media Settings**
- Enable auto-reply on social platforms
- Set business hours
- Configure platform-specific responses

---

## 🔐 **Security Configuration**

### **1. SSL/HTTPS**
- Ensure all traffic uses HTTPS
- Configure SSL certificates properly

### **2. API Security**
- Use API keys for external service authentication
- Implement rate limiting
- Monitor API usage

### **3. Data Privacy**
- Implement PII masking in logs
- Configure data retention policies
- GDPR compliance measures

---

## 📊 **Monitoring and Analytics**

### **Real-time Metrics**
- Conversation analytics
- AI agent performance
- Voice call statistics
- Payment processing metrics

### **Social Media Analytics**
- Message response times
- Customer satisfaction ratings
- Platform-specific engagement

### **System Health**
- Server performance monitoring
- API response times
- Error rate tracking

---

## 🚀 **Deployment Checklist**

- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] Static files collected
- [ ] SSL certificates installed
- [ ] Domain DNS configured
- [ ] Twilio webhooks set up
- [ ] Stripe webhooks configured
- [ ] Social media apps created
- [ ] AI agents configured
- [ ] Admin user created
- [ ] Firewall configured
- [ ] Monitoring tools set up

---

## 🧪 **Testing Guide**

### **Voice Call Testing**
```bash
# Test Twilio webhook
curl -X POST https://yourdomain.com/voice/twilio/voice/1/ \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "CallSid=CA123&From=%2B1234567890&SpeechResult=Hello%20AI%20assistant"
```

### **Chat Testing**
```bash
# Test chat API
curl -X POST https://yourdomain.com/api/chat/send/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token your-token" \
  -d '{"content": "Hello", "conversation_id": null}'
```

### **Social Media Testing**
```bash
# Test Facebook webhook
curl -X POST https://yourdomain.com/social/webhook/facebook/1/ \
  -H "Content-Type: application/json" \
  -d '{"object": "page", "entry": [{"messaging": [{"sender": {"id": "123"}, "message": {"text": "Hello"}}]}]}'
```

---

## 💡 **Advanced Features**

### **Custom AI Training**
- Upload company-specific training data
- Fine-tune models for industry-specific responses
- Implement custom intent recognition

### **Multi-language Support**
- Configure language detection
- Set up translation services
- Localized AI responses

### **Integration APIs**
- REST API for external integrations
- Webhook support for real-time updates
- Zapier/IFTTT compatibility

### **Advanced Analytics**
- Customer sentiment analysis
- Conversation flow optimization
- AI performance metrics

---

## 📞 **Support and Maintenance**

### **Regular Tasks**
- Monitor AI agent performance
- Update API keys before expiration
- Review and update training data
- Backup database regularly

### **Scaling Considerations**
- Database optimization for high-volume conversations
- Load balancing for multiple servers
- CDN setup for static assets
- Redis caching implementation

### **Troubleshooting**
- Check Django logs: `tail -f /var/log/django.log`
- Monitor Twilio logs in dashboard
- Review Stripe webhook delivery logs
- Check social media API rate limits

---

## 🎉 **Ready for Production!**

Your BanglaChatPro AI agent system is now fully configured and ready to handle customer support across all channels. Each client can have their own AI agent that provides 24/7 customer support via voice, chat, and social media platforms.

**Live Demo**: Visit `https://bdchatpro.com` to see the system in action!

**Admin Panel**: Access `/admin/` to manage organizations, AI agents, and monitor system performance.

---

*For additional support or customizations, contact the development team.*
