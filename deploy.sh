#!/bin/bash

# BanglaChatPro Production Deployment Script
# This script deploys the BanglaChatPro application to production server

set -e  # Exit on any error

echo "🚀 Starting BanglaChatPro Production Deployment..."

# Configuration
PROJECT_NAME="bangla-chat-pro"
GITHUB_REPO="https://github.com/yourusername/bangla-chat-pro.git"
SERVER_USER="root"
SERVER_HOST="your-server.com"
SERVER_PATH="/var/www/bangla-chat-pro"
NGINX_CONFIG="/etc/nginx/sites-available/bangla-chat-pro"
SYSTEMD_SERVICE="bangla-chat-pro"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
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

# Check if running on server
if [[ "$HOSTNAME" == *"server"* ]] || [[ "$USER" == "root" ]]; then
    log_info "Running on production server"
    IS_SERVER=true
else
    log_info "Running locally, will deploy to server"
    IS_SERVER=false
fi

# Step 1: Prepare local environment
if [ "$IS_SERVER" = false ]; then
    log_info "Preparing local environment..."
    
    # Check if git is initialized
    if [ ! -d ".git" ]; then
        log_info "Initializing Git repository..."
        git init
        git add .
        git commit -m "Initial commit: BanglaChatPro production ready"
    fi
    
    # Add remote if not exists
    if ! git remote | grep -q origin; then
        log_info "Adding GitHub remote..."
        git remote add origin $GITHUB_REPO
    fi
    
    # Push to GitHub
    log_info "Pushing to GitHub..."
    git add .
    git commit -m "Production deployment: $(date)"
    git push -u origin main
    
    log_success "Code pushed to GitHub successfully!"
fi

# Step 2: Deploy to server
if [ "$IS_SERVER" = true ]; then
    log_info "Deploying on production server..."
    
    # Update system packages
    log_info "Updating system packages..."
    apt update && apt upgrade -y
    
    # Install required packages
    log_info "Installing required packages..."
    apt install -y python3 python3-pip python3-venv nginx git supervisor
    
    # Create project directory
    log_info "Setting up project directory..."
    mkdir -p $SERVER_PATH
    cd $SERVER_PATH
    
    # Clone or update repository
    if [ -d ".git" ]; then
        log_info "Updating existing repository..."
        git pull origin main
    else
        log_info "Cloning repository..."
        git clone $GITHUB_REPO .
    fi
    
    # Create virtual environment
    log_info "Setting up Python virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    
    # Install dependencies
    log_info "Installing Python dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Set up environment variables
    log_info "Setting up environment variables..."
    if [ ! -f ".env" ]; then
        cp production.env .env
        log_warning "Please update .env file with your actual configuration values!"
    fi
    
    # Run Django setup
    log_info "Setting up Django application..."
    python manage.py collectstatic --noinput
    python manage.py migrate
    python manage.py createsuperuser --noinput --username admin --email admin@bdchatpro.com || true
    
    # Set up static files
    log_info "Setting up static files..."
    mkdir -p /var/www/bangla-chat-pro/static
    mkdir -p /var/www/bangla-chat-pro/media
    
    # Create systemd service
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
    
    # Enable and start service
    log_info "Starting systemd service..."
    systemctl daemon-reload
    systemctl enable $SYSTEMD_SERVICE
    systemctl start $SYSTEMD_SERVICE
    
    # Configure Nginx
    log_info "Configuring Nginx..."
    cat > $NGINX_CONFIG << EOF
server {
    listen 80;
    server_name bdchatpro.com www.bdchatpro.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name bdchatpro.com www.bdchatpro.com;
    
    # SSL Configuration (update with your certificates)
    ssl_certificate /etc/ssl/certs/bdchatpro.com.crt;
    ssl_certificate_key /etc/ssl/private/bdchatpro.com.key;
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
    
    # Set proper permissions
    log_info "Setting proper permissions..."
    chown -R www-data:www-data $SERVER_PATH
    chmod -R 755 $SERVER_PATH
    
    # Create log directory
    mkdir -p /var/log/bangla-chat-pro
    chown www-data:www-data /var/log/bangla-chat-pro
    
    log_success "Deployment completed successfully!"
    
    # Show status
    log_info "Service Status:"
    systemctl status $SYSTEMD_SERVICE --no-pager
    
    log_info "Nginx Status:"
    systemctl status nginx --no-pager
    
    log_info "Application URLs:"
    echo "  Main Chat: https://bdchatpro.com/"
    echo "  Admin Dashboard: https://bdchatpro.com/admin-dashboard/"
    echo "  Django Admin: https://bdchatpro.com/admin/"
    echo "  API Endpoints: https://bdchatpro.com/api/"
    
else
    log_info "To complete deployment, run this script on your production server:"
    echo "  ssh $SERVER_USER@$SERVER_HOST"
    echo "  curl -sSL https://raw.githubusercontent.com/yourusername/bangla-chat-pro/main/deploy.sh | bash"
fi

log_success "🎉 BanglaChatPro deployment process completed!"
log_info "Next steps:"
echo "  1. Update .env file with your actual configuration"
echo "  2. Set up SSL certificates"
echo "  3. Configure domain DNS"
echo "  4. Test all features"
echo "  5. Monitor logs: journalctl -u $SYSTEMD_SERVICE -f"