#!/bin/bash

# BanglaChatPro Server Deployment Script
# This script deploys the application to your production server

set -e

echo "🚀 Starting BanglaChatPro Server Deployment..."

# Configuration
PROJECT_NAME="bangla-chat-pro"
SERVER_PATH="/var/www/bangla-chat-pro"
NGINX_CONFIG="/etc/nginx/sites-available/bangla-chat-pro"
SYSTEMD_SERVICE="bangla-chat-pro"
DOMAIN="bdchatpro.com"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   log_error "This script must be run as root"
   exit 1
fi

log_info "Updating system packages..."
apt update && apt upgrade -y

log_info "Installing required packages..."
apt install -y python3 python3-pip python3-venv nginx git supervisor curl

log_info "Setting up project directory..."
mkdir -p $SERVER_PATH
cd $SERVER_PATH

# Clone or update repository
if [ -d ".git" ]; then
    log_info "Updating existing repository..."
    git pull origin main
else
    log_info "Cloning repository..."
    git clone https://github.com/yourusername/bangla-chat-pro.git .
fi

log_info "Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

log_info "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

log_info "Setting up environment variables..."
if [ ! -f ".env" ]; then
    cp production.env .env
    log_warning "Please update .env file with your actual configuration values!"
fi

log_info "Setting up Django application..."
python manage.py collectstatic --noinput
python manage.py migrate

# Create superuser if not exists
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@bdchatpro.com', 'admin123')
    print('Superuser created')
else:
    print('Superuser already exists')
"

log_info "Setting up static files..."
mkdir -p /var/www/bangla-chat-pro/static
mkdir -p /var/www/bangla-chat-pro/media

log_info "Creating systemd service..."
cat > /etc/systemd/system/$SYSTEMD_SERVICE.service << EOF
[Unit]
Description=BanglaChatPro Django Application
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=$SERVER_PATH
Environment=PATH=$SERVER_PATH/venv/bin
ExecStart=$SERVER_PATH/venv/bin/gunicorn --workers 4 --bind 127.0.0.1:8000 bangla_chat_pro.wsgi:application
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
EOF

log_info "Starting systemd service..."
systemctl daemon-reload
systemctl enable $SYSTEMD_SERVICE
systemctl start $SYSTEMD_SERVICE

log_info "Configuring Nginx..."
cat > $NGINX_CONFIG << EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    
    # Redirect HTTP to HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name $DOMAIN www.$DOMAIN;
    
    # SSL Configuration (update with your certificates)
    ssl_certificate /etc/ssl/certs/$DOMAIN.crt;
    ssl_certificate_key /etc/ssl/private/$DOMAIN.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Static files
    location /static/ {
        alias $SERVER_PATH/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        alias $SERVER_PATH/media/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Main application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
}
EOF

# Enable Nginx site
ln -sf $NGINX_CONFIG /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx

log_info "Setting proper permissions..."
chown -R www-data:www-data $SERVER_PATH
chmod -R 755 $SERVER_PATH

log_info "Creating log directory..."
mkdir -p /var/log/bangla-chat-pro
chown www-data:www-data /var/log/bangla-chat-pro

log_success "Deployment completed successfully!"

# Show status
log_info "Service Status:"
systemctl status $SYSTEMD_SERVICE --no-pager

log_info "Nginx Status:"
systemctl status nginx --no-pager

log_info "Application URLs:"
echo "  Main Dashboard: https://$DOMAIN/"
echo "  Login: https://$DOMAIN/login/"
echo "  Register: https://$DOMAIN/register/"
echo "  Chat Interface: https://$DOMAIN/chat/"
echo "  Admin Dashboard: https://$DOMAIN/admin-dashboard/"
echo "  Django Admin: https://$DOMAIN/admin/"

log_success "🎉 BanglaChatPro deployment completed!"
log_info "Next steps:"
echo "  1. Update .env file with your OpenAI API key"
echo "  2. Set up SSL certificates"
echo "  3. Configure domain DNS"
echo "  4. Test all features"
echo "  5. Monitor logs: journalctl -u $SYSTEMD_SERVICE -f"