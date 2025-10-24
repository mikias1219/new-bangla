# 🚀 BanglaChatPro Production Deployment Guide

## Prerequisites

- **Server**: Ubuntu 20.04+ or CentOS 7+ with 4GB RAM, 2 CPU cores
- **Domain**: SSL-enabled domain (Let's Encrypt recommended)
- **Database**: PostgreSQL 13+ (SQLite for development only)
- **Reverse Proxy**: Nginx
- **SSL Certificate**: Valid SSL certificate

## Quick Deployment (Docker)

### 1. Clone Repository
```bash
git clone https://github.com/your-org/banglachatpro.git
cd banglachatpro
```

### 2. Environment Configuration
```bash
cp env.example .env
# Edit .env with your configuration
```

### 3. Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up -d

# Or use the deployment script
chmod +x deploy_production.sh
./deploy_production.sh
```

## Manual Deployment

### Backend Setup

#### 1. Install Python Dependencies
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 2. Database Setup
```bash
# Create database
createdb bangla_chat_pro

# Run migrations
alembic upgrade head

# Create admin user
python create_admin.py
```

#### 3. Start Backend Service
```bash
# Using systemd
sudo cp deployment/backend.service /etc/systemd/system/
sudo systemctl enable bangla-chat-pro-backend
sudo systemctl start bangla-chat-pro-backend

# Or using PM2
pm2 start run.py --name bangla-chat-pro-backend
```

### Frontend Setup

#### 1. Install Dependencies
```bash
npm install
```

#### 2. Build for Production
```bash
npm run build
```

#### 3. Start Frontend Service
```bash
# Using PM2
pm2 start npm --name bangla-chat-pro-frontend -- start

# Or using systemd
sudo cp deployment/frontend.service /etc/systemd/system/
sudo systemctl enable bangla-chat-pro-frontend
sudo systemctl start bangla-chat-pro-frontend
```

### Nginx Configuration

#### 1. Install Nginx
```bash
sudo apt update
sudo apt install nginx
```

#### 2. SSL Certificate (Let's Encrypt)
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

#### 3. Nginx Configuration
```nginx
# /etc/nginx/sites-available/banglachatpro
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";

    # Frontend (Next.js)
    location / {
        proxy_pass http://localhost:3002;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static files
    location /_next/static/ {
        proxy_pass http://localhost:3002;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

#### 4. Enable Site
```bash
sudo ln -s /etc/nginx/sites-available/banglachatpro /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Environment Variables

### Required Variables
```bash
# Core
NEXT_PUBLIC_BACKEND_URL=https://yourdomain.com
DATABASE_URL=postgresql://user:pass@localhost/db
SECRET_KEY=your-jwt-secret

# Twilio (for IVR)
TWILIO_ACCOUNT_SID=ACxxx
TWILIO_AUTH_TOKEN=xxx
TWILIO_PHONE_NUMBER=+880xxx
BASE_URL=https://yourdomain.com

# OpenAI
OPENAI_API_KEY=sk-xxx
```

### Optional Variables
```bash
# Email
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Social Media
FACEBOOK_APP_ID=your-facebook-app-id
FACEBOOK_APP_SECRET=your-facebook-app-secret
WHATSAPP_ACCESS_TOKEN=your-whatsapp-access-token
WHATSAPP_PHONE_NUMBER_ID=your-phone-number-id

# Payments
STRIPE_SECRET_KEY=sk_live_your_live_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_live_your_live_stripe_publishable_key

# Monitoring
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
ENVIRONMENT=production
```

## Database Migration

### Production Database Setup
```bash
# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE bangla_chat_pro;
CREATE USER bcp_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE bangla_chat_pro TO bcp_user;

# Update DATABASE_URL in .env
DATABASE_URL=postgresql://bcp_user:secure_password@localhost:5432/bangla_chat_pro
```

### Run Migrations
```bash
cd backend
source venv/bin/activate
alembic upgrade head
python create_admin.py
```

## SSL & Security

### 1. SSL Certificate
```bash
# Let's Encrypt (automatic renewal)
sudo certbot renew --dry-run

# Manual certificate
# Place certificate files in /etc/ssl/certs/
# Update nginx configuration accordingly
```

### 2. Firewall Configuration
```bash
# UFW (Ubuntu)
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw --force enable
```

### 3. Security Hardening
```bash
# Disable root login
sudo sed -i 's/#PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sudo systemctl reload sshd

# Install fail2ban
sudo apt install fail2ban
sudo systemctl enable fail2ban
```

## Monitoring & Logging

### 1. Application Monitoring
```bash
# PM2 monitoring
pm2 monit

# Logs
pm2 logs bangla-chat-pro-backend
pm2 logs bangla-chat-pro-frontend
```

### 2. Server Monitoring
```bash
# Install monitoring tools
sudo apt install htop iotop ncdu

# System logs
sudo journalctl -u bangla-chat-pro-backend
sudo journalctl -u nginx
```

## Scaling

### Horizontal Scaling
```bash
# Load balancer configuration (nginx upstream)
upstream backend_servers {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}
```

### Performance Optimization
```bash
# Enable gzip compression
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss;
```

## Troubleshooting

### Common Issues

#### 1. 502 Bad Gateway
```bash
# Check if backend is running
sudo systemctl status bangla-chat-pro-backend

# Check backend logs
sudo journalctl -u bangla-chat-pro-backend -f
```

#### 2. SSL Certificate Issues
```bash
# Renew Let's Encrypt certificate
sudo certbot renew

# Check certificate validity
openssl x509 -in /etc/letsencrypt/live/yourdomain.com/cert.pem -text -noout
```

## Support

For deployment support:
- 📧 Email: deployment@banglachatpro.com
- 📚 Docs: https://docs.banglachatpro.com/deployment
- 🚨 Issues: https://github.com/your-org/banglachatpro/issues
