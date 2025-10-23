# Twilio IVR Setup Guide for Bangla Chat Pro

This guide provides step-by-step instructions to set up Twilio for the AI-powered Bangla IVR system.

## 📋 Prerequisites

1. **Twilio Account**: Sign up at [twilio.com](https://twilio.com)
2. **Twilio Phone Number**: Purchase a phone number for IVR calls
3. **Server with Public IP**: Your Hostinger VPS with public access
4. **SSL Certificate**: HTTPS enabled for webhook security

## 🔧 Step 1: Twilio Console Setup

### 1.1 Create Twilio Account
1. Go to [twilio.com](https://twilio.com) and sign up
2. Verify your email and phone number
3. Complete account setup

### 1.2 Get API Credentials
1. Go to [Twilio Console](https://console.twilio.com)
2. Navigate to **Account → API keys & tokens**
3. Copy your:
   - **Account SID**
   - **Auth Token**
   - **API Key** (create one if needed)
   - **API Secret**

### 1.3 Purchase Phone Number
1. Go to **Phone Numbers → Manage → Buy a number**
2. Search for numbers in your target country (Bangladesh: +880)
3. Purchase a number suitable for voice calls
4. Note the phone number (e.g., +8801234567890)

## ⚙️ Step 2: Server Configuration

### 2.1 Environment Variables
Add these to your `.env` file:

```bash
# Twilio Configuration
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_PHONE_NUMBER=+8801234567890
TWILIO_API_KEY=SKxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_API_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_APPLICATION_SID=APxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 2.2 Webhook URLs
Configure these webhook URLs in Twilio Console:

#### Voice Webhooks (Phone Numbers → Manage)
```
Voice Request URL: https://yourdomain.com/ivr/webhook/incoming-call
Method: POST
```

#### Application Webhooks (Voice → Manage → TwiML Apps)
```
Voice Request URL: https://yourdomain.com/ivr/webhook/incoming-call
Status Callback URL: https://yourdomain.com/ivr/webhook/call-completed
```

## 🎯 Step 3: Testing the IVR System

### 3.1 Test Voice Webhooks
```bash
# Test incoming call webhook
curl -X POST https://yourdomain.com/ivr/webhook/incoming-call \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "CallSid=CA123&From=%2B8801234567890&To=%2B8800987654321"
```

### 3.2 Test TTS Functionality
```bash
# Test Bangla text-to-speech
curl -X POST https://yourdomain.com/ivr/test-tts \
  -H "Content-Type: application/json" \
  -d '{"text": "স্বাগতম বাংলা চ্যাট প্রো-তে", "voice": "Polly.Aditi", "language": "bn-IN"}'
```

### 3.3 Test Call Simulation
```bash
# Make a test call to your IVR number
# This will trigger the webhook and test the full flow
```

## 🎤 Step 4: Bangla Voice Configuration

### 4.1 Supported Voices
Twilio supports these Bangla voices:

- **Amazon Polly - Aditi**: `Polly.Aditi` (bn-IN)
- **Google TTS**: Bangla voices (may require additional setup)

### 4.2 Voice Quality Settings
```xml
<!-- TwiML Example -->
<Response>
  <Say voice="Polly.Aditi" language="bn-IN" rate="0.9" pitch="1">
    স্বাগতম বাংলা চ্যাট প্রো-তে
  </Say>
</Response>
```

## 📞 Step 5: IVR Menu Configuration

### 5.1 Main Menu Structure
The IVR system includes these menus:

1. **Main Menu** (`ivr_menus["main"]`)
   - 1: অর্ডার স্ট্যাটাস (Order Status)
   - 2: প্রোডাক্ট তথ্য (Product Info)
   - 3: সাপোর্ট (Support)
   - 4: মানুষের সাথে কথা (Speak to Human)
   - 0: পুনরায় শুনুন (Repeat)

2. **Order Menu** (`ivr_menus["order"]`)
   - Speech recognition for order IDs

3. **Product Menu** (`ivr_menus["product"]`)
   - Speech recognition for product search

4. **Support Menu** (`ivr_menus["support"]`)
   - General support queries

### 5.2 DTMF Configuration
- **Timeout**: 10 seconds
- **Max Attempts**: 3 before escalation
- **Input Length**: 1 digit for main menu

## 🚨 Step 6: Escalation Rules

### 6.1 Automatic Escalation
The system escalates to human agents when:

1. **AI Confidence < 50%** for 2 consecutive responses
2. **User explicitly requests** human agent (press 4)
3. **Max retry attempts** reached (3 attempts)
4. **No input timeout** (2 timeouts)

### 6.2 Escalation Process
1. Update call status to "escalated"
2. Play escalation message
3. Queue call for human agent
4. Log escalation event

## 📊 Step 7: Monitoring & Analytics

### 7.1 Real-time Monitoring
- Call status dashboard in admin panel
- Live call metrics
- Escalation tracking

### 7.2 Analytics Metrics
- Total calls handled
- Completion rate
- Escalation rate
- Average call duration
- Language usage statistics

## 🔧 Step 8: Troubleshooting

### 8.1 Common Issues

#### Webhook Not Receiving Calls
- Check webhook URL is publicly accessible
- Verify SSL certificate is valid
- Check Twilio console for webhook errors

#### Voice Not Working
- Verify Twilio credentials
- Check voice permissions
- Test TTS endpoint manually

#### Speech Recognition Issues
- Check language settings (bn-BD)
- Verify speech timeout settings
- Test with clear speech

### 8.2 Debug Mode
Enable debug logging in Twilio Console:
1. Go to **Monitor → Logs**
2. Check webhook request/response logs
3. Monitor call events

## 📈 Step 9: Scaling & Optimization

### 9.1 Performance Optimization
- Implement call queuing for high volume
- Use Redis for session management
- Optimize database queries
- Implement caching for frequent responses

### 9.2 Cost Optimization
- Monitor Twilio usage costs
- Set up billing alerts
- Optimize call routing
- Implement call limits per user/org

## 🔒 Step 10: Security Best Practices

### 10.1 Webhook Security
- Validate Twilio request signatures
- Use HTTPS for all webhooks
- Implement rate limiting
- Log all webhook requests

### 10.2 Data Protection
- PII masking in logs
- Secure credential storage
- Regular security audits
- Compliance with local regulations

## 📞 Support & Resources

### Documentation
- [Twilio Voice API Docs](https://www.twilio.com/docs/voice)
- [Twilio TwiML Reference](https://www.twilio.com/docs/voice/twiml)
- [Twilio Console Guide](https://www.twilio.com/docs/usage/console)

### Support Channels
- Twilio Support: support@twilio.com
- Bangladesh-specific support
- 24/7 technical support for paid plans

---

## ✅ Quick Setup Checklist

- [ ] Twilio account created
- [ ] API credentials configured
- [ ] Phone number purchased
- [ ] Environment variables set
- [ ] Webhooks configured
- [ ] SSL certificate active
- [ ] Test call successful
- [ ] Bangla voice working
- [ ] Escalation rules tested
- [ ] Admin dashboard monitoring active

## 🚀 Deployment Ready

Once all steps are completed, your AI-powered Bangla IVR system will be ready to handle customer calls with natural language processing, intelligent routing, and seamless escalation to human agents when needed.
