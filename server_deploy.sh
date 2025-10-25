#!/bin/bash

# Django deployment script for Bangla Chat Pro
# Run this on the server after pushing changes to GitHub

echo "🚀 Bangla Chat Pro Django Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="/root/bangla-chat-pro"
DOMAIN="bdchatpro.com"
GITHUB_REPO="https://github.com/mikias1219/new-bangla.git"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 1. Pull latest changes from GitHub
print_status "Pulling latest changes from GitHub..."
if [ ! -d "$PROJECT_DIR" ]; then
    print_status "Cloning repository..."
    git clone $GITHUB_REPO $PROJECT_DIR
else
    print_status "Updating repository..."
    cd $PROJECT_DIR && git pull origin main || git pull origin master
fi

# 2. Setup Django application
print_status "Setting up Django application..."
cd $PROJECT_DIR

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_status "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate venv and install/update dependencies
print_status "Installing Python dependencies..."
source venv/bin/activate
pip install -r requirements.txt

# Create/update .env file
print_status "Setting up environment variables..."
cat > .env << 'EOF'
SECRET_KEY=django-insecure-production-key-change-this-2025
DEBUG=False
ALLOWED_HOSTS=bdchatpro.com,www.bdchatpro.com,localhost,127.0.0.1
DB_NAME=bangla_chat_pro
DB_USER=bangla_chat
DB_PASSWORD=secure_password_2025
DB_HOST=localhost
DB_PORT=5432
VOICE_API_KEY=
VOICE_API_ENDPOINT=
OPENAI_API_KEY=YOUR_OPENAI_API_KEY_HERE
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
EOF

# Run Django migrations
print_status "Running Django migrations..."
python manage.py migrate

# Collect static files
print_status "Collecting static files..."
python manage.py collectstatic --noinput

# Create admin user if it doesn't exist
print_status "Ensuring admin user exists..."
python manage.py shell -c "
from accounts.models import Organization, User
from django.contrib.auth import get_user_model

# Create organization
org, created = Organization.objects.get_or_create(
    name='BanglaChatPro',
    defaults={
        'is_active': True,
        'description': 'AI-powered customer service platform',
        'max_users': 100,
        'max_conversations': 10000
    }
)

# Create superuser
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    admin = User.objects.create_superuser(
        username='admin',
        email='admin@bdchatpro.com',
        password='admin123',
        first_name='Admin',
        last_name='User',
        organization=org,
        is_admin=True
    )
    print('Superuser created')
else:
    print('Superuser already exists')
"

# 4. Configure Nginx (if not already configured)
print_status "Ensuring Nginx configuration..."
if [ ! -f "/etc/nginx/sites-enabled/bdchatpro" ]; then
    print_status "Setting up Nginx configuration..."

    # Create Nginx configuration
    cat > /etc/nginx/sites-available/bdchatpro << 'EOF'
# Django Application
server {
    listen 80;
    server_name bdchatpro.com www.bdchatpro.com;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;

    # Django static files
    location /static/ {
        alias /root/bangla-chat-pro/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Django media files
    location /media/ {
        alias /root/bangla-chat-pro/media/;
        expires 30d;
        add_header Cache-Control "public";
    }

    # Django application
    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;

        # CORS headers for API
        add_header 'Access-Control-Allow-Origin' 'https://bdchatpro.com' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization' always;

        if ($request_method = 'OPTIONS') {
            return 204;
        }
    }
}
EOF

    # Enable site
    ln -sf /etc/nginx/sites-available/bdchatpro /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default

    # Test nginx configuration
    nginx -t
fi

# 5. Setup SSL certificates (if not already set up)
print_status "Ensuring SSL certificates..."
if [ ! -d "/etc/letsencrypt/live/bdchatpro.com" ]; then
    print_status "Obtaining SSL certificates..."
    certbot --nginx -d bdchatpro.com -d www.bdchatpro.com --non-interactive --agree-tos --email admin@bdchatpro.com
fi

# 6. Setup systemd service for Django
print_status "Setting up Django systemd service..."

# Create systemd service file
cat > /etc/systemd/system/bangla-chat-pro.service << EOF
[Unit]
Description=Bangla Chat Pro Django Application
After=network.target

[Service]
User=root
Group=root
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin"
ExecStart=$PROJECT_DIR/venv/bin/gunicorn --workers 4 --bind 0.0.0.0:8000 bangla_chat_pro.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and start service
systemctl daemon-reload
systemctl enable bangla-chat-pro
systemctl start bangla-chat-pro

# 7. Restart services
print_status "Restarting services..."
systemctl restart nginx

# 8. Health checks
print_status "Running health checks..."
sleep 3

# Check if services are running
pm2 list

# Check nginx status
systemctl status nginx --no-pager

print_success "Deployment completed!"
print_success "Frontend: https://bdchatpro.com"
print_success "Backend API: https://bdchatpro.com/api"
print_success "Admin login: admin@bdchatpro.com / admin123!@#"
print_warning "Remember to change the admin password after first login!"
