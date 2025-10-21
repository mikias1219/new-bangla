#!/usr/bin/env python3
"""
Environment setup script for Bangla Chat Pro SaaS
This script helps configure the environment variables and initial setup
"""

import os
import secrets
from pathlib import Path

def generate_secret_key():
    """Generate a secure secret key"""
    return secrets.token_hex(32)

def create_env_file():
    """Create .env file with required environment variables"""
    env_content = f"""# Bangla Chat Pro Environment Configuration

# Database
DATABASE_URL=sqlite:///./bangla_chat_pro.db

# JWT Authentication
SECRET_KEY={generate_secret_key()}

# OpenAI API (Required for AI functionality)
OPENAI_API_KEY=your_openai_api_key_here

# WhatsApp Business API (Optional - for WhatsApp integration)
WHATSAPP_ACCESS_TOKEN=your_whatsapp_access_token
WHATSAPP_PHONE_NUMBER_ID=your_whatsapp_phone_number_id
WHATSAPP_VERIFY_TOKEN={secrets.token_hex(16)}

# Facebook Messenger API (Optional - for Facebook integration)
FACEBOOK_ACCESS_TOKEN=your_facebook_access_token
FACEBOOK_APP_SECRET=your_facebook_app_secret
FACEBOOK_VERIFY_TOKEN={secrets.token_hex(16)}

# Stripe (Optional - for payment processing)
STRIPE_SECRET_KEY=your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret

# Email (Optional - for notifications)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# Application Settings
DEBUG=true
CORS_ORIGINS=http://localhost:3000,http://localhost:3002,https://bdchatpro.com

# File Upload Settings
MAX_UPLOAD_SIZE=10485760  # 10MB in bytes
ALLOWED_FILE_TYPES=pdf,docx,txt,csv

# AI Settings
EMBEDDING_MODEL=text-embedding-3-small
CHAT_MODEL=gpt-4
MAX_TOKENS=1000
TEMPERATURE=0.7
"""

    with open('.env', 'w') as f:
        f.write(env_content)

    print("✅ Created .env file with default configuration")
    print("⚠️  IMPORTANT: Please update the API keys and secrets in .env file")

def create_directories():
    """Create necessary directories"""
    directories = [
        'uploads',
        'uploads/organizations',
        'embeddings',
        'embeddings/organizations',
        'logs'
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

    print("✅ Created necessary directories")

def print_setup_instructions():
    """Print setup instructions"""
    print("""
🚀 Bangla Chat Pro SaaS Setup Complete!

Next Steps:

1. 📝 Configure Environment Variables:
   - Edit .env file with your actual API keys
   - Required: OpenAI API key for AI functionality
   - Optional: WhatsApp, Facebook, Stripe keys for full features

2. 🗄️  Initialize Database:
   cd backend
   python migrate_to_multi_tenant.py

3. 👑 Create Admin User:
   python create_admin.py

4. 🚀 Start Services:
   # Terminal 1 - Backend
   cd backend
   source venv/bin/activate
   python run.py

   # Terminal 2 - Frontend
   npm install
   npm run dev

5. 🌐 Access Application:
   - Frontend: http://localhost:3002
   - Admin Dashboard: http://localhost:3002/admin
   - API Docs: http://localhost:8000/docs

6. 🔧 Production Deployment:
   - Set up domain and SSL certificates
   - Configure nginx with the provided config
   - Set up PM2 for process management
   - Configure webhook endpoints for WhatsApp/Facebook

7. 💰 Revenue Setup:
   - Configure Stripe for payments
   - Set up pricing plans
   - Configure webhooks for subscription management

📚 Documentation:
- Check README.md for detailed setup instructions
- Visit /docs for API documentation
- Admin credentials: admin@bdchatpro.com / admin123!@#

🎯 Ready to sell your AI SaaS platform!
""")

def main():
    """Main setup function"""
    print("🎯 Setting up Bangla Chat Pro SaaS Environment...")

    try:
        create_env_file()
        create_directories()
        print_setup_instructions()

    except Exception as e:
        print(f"❌ Setup failed: {str(e)}")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())
