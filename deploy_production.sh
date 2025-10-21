#!/bin/bash

echo "🚀 Bangla Chat Pro Production Deployment Script"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REMOTE_HOST="88.222.245.41"
REMOTE_USER="root"
SSH_KEY="~/.ssh/id_ed25519"
PROJECT_NAME="bangla-chat-pro"
DOMAIN="bdchatpro.com"
GITHUB_REPO="https://github.com/mikias1219/new-bangla.git"
REMOTE_PROJECT_DIR="/root/$PROJECT_NAME"

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

# Function to run commands on remote server
run_remote() {
    ssh -i $SSH_KEY -o StrictHostKeyChecking=no $REMOTE_USER@$REMOTE_HOST "$1"
}

# Check if we're running locally or on server
if [ "$REMOTE_HOST" = "$(hostname -I | awk '{print $1}')" ] || [ "$REMOTE_HOST" = "$(hostname)" ]; then
    print_status "Running deployment on server directly"
    IS_REMOTE=true
else
    print_status "Running deployment from local machine to remote server"
    IS_REMOTE=false
fi

# Function to run commands (local or remote)
run_cmd() {
    if [ "$IS_REMOTE" = true ]; then
        eval "$1"
    else
        run_remote "$1"
    fi
}

print_status "Starting deployment process..."

# 1. Update system packages
print_status "Updating system packages..."
run_cmd "apt update && apt upgrade -y"

# 2. Install required system packages
print_status "Installing system dependencies..."
run_cmd "apt install -y python3 python3-pip python3-venv nodejs npm git curl nginx certbot python3-certbot-nginx ufw"

# 3. Install PM2 globally
print_status "Installing PM2 process manager..."
run_cmd "npm install -g pm2"

# 4. Clone or update repository
print_status "Setting up project repository..."
if [ "$IS_REMOTE" = false ]; then
    # If deploying from local, push first then clone on server
    print_status "Pushing local changes to GitHub..."
    if git status --porcelain | grep -q .; then
        git add .
        git commit -m "Deployment update: $(date)"
    fi
    git push origin master
fi

# Clone/update on server
run_cmd "if [ ! -d '$REMOTE_PROJECT_DIR' ]; then git clone $GITHUB_REPO $REMOTE_PROJECT_DIR; else cd $REMOTE_PROJECT_DIR && git pull origin master; fi"

# 5. Setup backend
print_status "Setting up backend..."
run_cmd "cd $REMOTE_PROJECT_DIR/backend"

# Create/update virtual environment
run_cmd "cd $REMOTE_PROJECT_DIR/backend && python3 -m venv venv --clear"

# Install Python dependencies
run_cmd "cd $REMOTE_PROJECT_DIR/backend && source venv/bin/activate && pip install --upgrade pip"
run_cmd "cd $REMOTE_PROJECT_DIR/backend && source venv/bin/activate && pip install -r requirements.txt"

# Create production environment file
run_cmd "cd $REMOTE_PROJECT_DIR/backend && cat > .env << 'EOF'
DATABASE_URL=sqlite:///./bangla_chat_pro.db
SECRET_KEY=$(openssl rand -hex 32)
OPENAI_API_KEY=YOUR_OPENAI_API_KEY_HERE
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
EOF"

# Create admin user
run_cmd "cd $REMOTE_PROJECT_DIR/backend && source venv/bin/activate && python create_admin.py"

# 6. Setup frontend
print_status "Setting up frontend..."
run_cmd "cd $REMOTE_PROJECT_DIR"

# Install Node.js dependencies
run_cmd "cd $REMOTE_PROJECT_DIR && npm install"

# Create production environment file
run_cmd "cd $REMOTE_PROJECT_DIR && cat > .env.local << 'EOF'
NEXT_PUBLIC_BACKEND_URL=https://$DOMAIN/api
NEXT_PUBLIC_SITE_URL=https://$DOMAIN
EOF"

# Build frontend for production
run_cmd "cd $REMOTE_PROJECT_DIR && npm run build"

# 7. Configure Nginx
print_status "Configuring Nginx..."

# Create Nginx configuration
run_cmd "cat > /etc/nginx/sites-available/$DOMAIN << 'EOF'
# Frontend (Next.js)
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;

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

    location / {
        proxy_pass http://localhost:3002;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }
}

# Backend API
server {
    listen 80;
    server_name api.$DOMAIN;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;

        # CORS headers for API
        add_header 'Access-Control-Allow-Origin' 'https://$DOMAIN' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization' always;

        if (\$request_method = 'OPTIONS') {
            return 204;
        }
    }
}
EOF"

# Enable site and disable default
run_cmd "ln -sf /etc/nginx/sites-available/$DOMAIN /etc/nginx/sites-enabled/"
run_cmd "rm -f /etc/nginx/sites-enabled/default"

# Test nginx configuration
run_cmd "nginx -t"

# 8. Setup SSL certificates
print_status "Setting up SSL certificates..."

# Get SSL certificate for both domains
run_cmd "certbot --nginx -d $DOMAIN -d www.$DOMAIN -d api.$DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN"

# 9. Configure PM2 processes
print_status "Configuring PM2 processes..."

# Stop existing processes
run_cmd "pm2 delete all 2>/dev/null || true"

# Start backend
run_cmd "cd $REMOTE_PROJECT_DIR/backend && pm2 start --name '$PROJECT_NAME-backend' 'source venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4'"

# Start frontend
run_cmd "cd $REMOTE_PROJECT_DIR && pm2 start --name '$PROJECT_NAME-frontend' 'npm start'"

# Save PM2 configuration
run_cmd "pm2 save"
run_cmd "pm2 startup"
run_cmd "pm2 save"

# 10. Configure firewall
print_status "Configuring firewall..."
run_cmd "ufw --force enable"
run_cmd "ufw allow ssh"
run_cmd "ufw allow 'Nginx Full'"
run_cmd "ufw --force reload"

# 11. Restart services
print_status "Restarting services..."
run_cmd "systemctl restart nginx"
run_cmd "pm2 restart all"

# 12. Health checks
print_status "Running health checks..."

# Wait for services to start
sleep 10

# Check PM2 status
run_cmd "pm2 list"

# Check service statuses
run_cmd "systemctl status nginx --no-pager -l | head -20"

# Test endpoints
print_status "Testing endpoints..."
run_cmd "curl -s -o /dev/null -w 'Frontend HTTP status: %{http_code}\n' https://$DOMAIN/ || echo 'Frontend check failed'"
run_cmd "curl -s -o /dev/null -w 'Backend API HTTP status: %{http_code}\n' https://$DOMAIN/api/ || echo 'Backend API check failed'"

print_success "Deployment completed successfully!"
print_success "=================================="
print_success "Frontend: https://$DOMAIN"
print_success "Backend API: https://$DOMAIN/api"
print_success "Admin login: admin@$DOMAIN / admin123"
print_warning "Remember to change the admin password after first login!"
print_warning "SSL certificates are set to auto-renew via certbot"

# Show PM2 logs
echo ""
print_status "Recent PM2 logs:"
run_cmd "pm2 logs --lines 10"

print_success "Deployment script completed!"
