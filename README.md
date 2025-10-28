# BanglaChatPro - AI Customer Care Platform

A comprehensive Django-based AI customer care platform designed specifically for Bangla language support, featuring real-time chat, voice interactions, and comprehensive admin management.

## 🚀 Features

### Core Features
- **🤖 AI-Powered Chat**: OpenAI GPT-4 integration with Bangla language support
- **🎤 Voice Interactions**: Web Speech API + OpenAI TTS for voice conversations
- **👥 Human Handoff**: Automatic escalation after 2 failed AI responses
- **🏢 Multi-Client Support**: Manage multiple businesses from one platform
- **📊 Analytics Dashboard**: Comprehensive analytics and reporting
- **🔧 Custom Admin Panel**: Unified admin dashboard with all super admin features

### Technical Features
- **🔒 Security**: CSRF protection, authentication, environment-based config
- **📱 Responsive UI**: TailwindCSS with Bangla font support
- **🌐 RESTful API**: Complete API for all features
- **📊 Real-time Updates**: WebSocket support for live chat
- **🗄️ SQLite Database**: Lightweight, production-ready database
- **🚀 Production Ready**: Gunicorn + Nginx deployment configuration

## 📋 Requirements

- Python 3.8+
- Django 5.0+
- OpenAI API Key
- Node.js (for frontend assets)
- Nginx (for production)
- Gunicorn (for production)

## 🛠️ Installation

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/bangla-chat-pro.git
   cd bangla-chat-pro
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp production.env .env
   # Edit .env file with your configuration
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start development server**
   ```bash
   python manage.py runserver
   ```

### Production Deployment

1. **Run deployment script**
   ```bash
   ./deploy.sh
   ```

2. **Configure environment**
   - Update `.env` file with production values
   - Set up SSL certificates
   - Configure domain DNS

3. **Start services**
   ```bash
   systemctl start bangla-chat-pro
   systemctl start nginx
   ```

## 🔧 Configuration

### Environment Variables

Key environment variables to configure:

```bash
# Required
SECRET_KEY=your-secret-key
OPENAI_API_KEY=your-openai-api-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Optional
DATABASE_URL=sqlite:///db.sqlite3
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
```

### OpenAI API Setup

1. Get API key from [OpenAI Platform](https://platform.openai.com/)
2. Add to `.env` file:
   ```bash
   OPENAI_API_KEY=sk-your-api-key-here
   ```

## 📚 API Documentation

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main chat interface |
| `/admin-dashboard/` | GET | Custom admin dashboard |
| `/admin/` | GET | Django admin interface |
| `/api/chat/` | POST | Send chat message |
| `/api/voice/` | POST | Process voice input |
| `/api/rate/` | POST | Rate conversation |
| `/api/handoff/` | POST | Request human handoff |
| `/api/clients/` | GET/POST | Manage clients |
| `/api/intents/` | GET/POST | Manage intents |

### API Examples

**Send Chat Message**
```bash
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": 1,
    "user_name": "User Name",
    "message": "আপনার বার্তা"
  }'
```

**Process Voice Input**
```bash
curl -X POST http://localhost:8000/api/voice/ \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": 1,
    "caller_name": "Caller Name",
    "question": "Voice question"
  }'
```

## 🎯 Usage

### For Users
1. Visit the main chat interface
2. Select your client/business
3. Start chatting in Bangla
4. Use voice mode for hands-free interaction
5. Request human help if needed

### For Admins
1. Login to admin dashboard (`/admin-dashboard/`)
2. Monitor conversations and analytics
3. Manage clients and AI agents
4. Test features using the testing panel
5. Configure system settings

### For Developers
1. Use Django admin for database management
2. Access API endpoints for integration
3. Customize templates and views
4. Add new features using the modular structure

## 🏗️ Project Structure

```
bangla-chat-pro/
├── accounts/           # User and organization management
├── api/               # REST API endpoints
├── chat/              # Chat interface and models
├── client_onboarding/ # Client onboarding flow
├── core/              # Core BanglaChatPro models and admin
├── services/          # External service integrations
├── social_media/      # Social media integration
├── templates/         # HTML templates
├── voice/             # Voice features
├── static/            # Static files (CSS, JS, images)
├── bangla_chat_pro/   # Django project settings
├── requirements.txt   # Python dependencies
├── deploy.sh         # Production deployment script
└── production.env    # Environment configuration template
```

## 🔒 Security

- CSRF protection enabled
- Secure session cookies
- Environment-based configuration
- Input validation and sanitization
- Rate limiting on API endpoints
- HTTPS enforcement in production

## 📊 Monitoring

### Logs
- Application logs: `/var/log/bangla-chat-pro/`
- System logs: `journalctl -u bangla-chat-pro -f`
- Nginx logs: `/var/log/nginx/`

### Health Checks
- Service status: `systemctl status bangla-chat-pro`
- Database: `python manage.py check --deploy`
- API health: `curl http://localhost:8000/api/clients/`

## 🚀 Deployment

### Quick Deploy
```bash
./deploy.sh
```

### Manual Deploy
1. Clone repository on server
2. Set up virtual environment
3. Install dependencies
4. Configure environment
5. Run migrations
6. Set up systemd service
7. Configure Nginx
8. Start services

## 🧪 Testing

### Test Features
1. Login to admin dashboard
2. Go to "Testing & Debug" section
3. Test chat API with sample messages
4. Test voice API with sample text
5. Verify all endpoints are working

### Manual Testing
```bash
# Test main interface
curl http://localhost:8000/

# Test API
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"client_id": 1, "user_name": "Test", "message": "Hello"}'
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: Check this README and API documentation
- **Issues**: Report bugs via GitHub issues
- **Admin Panel**: Use the testing section for debugging
- **Logs**: Check application and system logs

## 🎉 Success Metrics

After deployment, verify:
- ✅ Main chat interface loads
- ✅ Admin dashboard accessible
- ✅ API endpoints respond correctly
- ✅ OpenAI integration working
- ✅ Voice features functional
- ✅ Database persistent
- ✅ All security measures active

---

**BanglaChatPro** - Empowering businesses with AI-powered Bangla customer care! 🇧🇩