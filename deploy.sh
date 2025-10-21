#!/bin/bash

echo "🚀 Starting Bangla Chat Pro Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REMOTE_HOST="88.222.245.41"
REMOTE_USER="root"
PROJECT_DIR="/home/mikias/Mikias/Work/Projects/Freelance/bangla-chat-pro"
REMOTE_PROJECT_DIR="/root/bangla-chat-pro"
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

# Check if we're running on the server or locally
if [ "$REMOTE_HOST" = "$(hostname -I | awk '{print $1}')" ] || [ "$REMOTE_HOST" = "$(hostname)" ]; then
    print_status "Running deployment on server"
    IS_REMOTE=true
else
    print_status "Running deployment locally, will deploy to remote server"
    IS_REMOTE=false
fi

# Function to run commands locally or remotely
run_cmd() {
    if [ "$IS_REMOTE" = true ]; then
        eval "$1"
    else
        ssh -i ~/.ssh/id_ed25519 -o StrictHostKeyChecking=no root@$REMOTE_HOST "$1"
    fi
}

# 1. Update system and install dependencies
print_status "Updating system and installing dependencies..."
run_cmd "apt update && apt upgrade -y"
run_cmd "apt install -y python3 python3-pip python3-venv nginx certbot python3-certbot-nginx nodejs npm git curl"

# 2. Install PM2 for process management
print_status "Installing PM2 for process management..."
run_cmd "npm install -g pm2"

# 3. Clone or update repository from GitHub
print_status "Pulling latest changes from GitHub..."
run_cmd "if [ ! -d '$REMOTE_PROJECT_DIR' ]; then git clone $GITHUB_REPO $REMOTE_PROJECT_DIR; else cd $REMOTE_PROJECT_DIR && git pull origin main || git pull origin master; fi"

# 4. Setup backend
print_status "Setting up backend..."
run_cmd "cd $REMOTE_PROJECT_DIR/backend"

# Create virtual environment
run_cmd "cd $REMOTE_PROJECT_DIR/backend && python3 -m venv venv"

# Activate venv and install dependencies
run_cmd "cd $REMOTE_PROJECT_DIR/backend && source venv/bin/activate && pip install -r requirements.txt"

# Create .env file with production settings
run_cmd "cd $REMOTE_PROJECT_DIR/backend && cat > .env << 'EOF'
DATABASE_URL=sqlite:///./bangla_chat_pro.db
SECRET_KEY=$(openssl rand -hex 32)
OPENAI_API_KEY=YOUR_OPENAI_API_KEY_HERE
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
EOF"

# Create admin user
run_cmd "cd $REMOTE_PROJECT_DIR/backend && source venv/bin/activate && python create_admin.py"

# 5. Setup frontend
print_status "Setting up frontend..."
run_cmd "cd $REMOTE_PROJECT_DIR"

# Install dependencies
run_cmd "cd $REMOTE_PROJECT_DIR && npm install"

# Create production environment file
run_cmd "cd $REMOTE_PROJECT_DIR && cat > .env.local << 'EOF'
NEXT_PUBLIC_BACKEND_URL=https://bdchatpro.com/api
NEXT_PUBLIC_SITE_URL=https://bdchatpro.com
EOF"

# Build frontend
run_cmd "cd $REMOTE_PROJECT_DIR && npm run build"

# 6. Configure Nginx
print_status "Configuring Nginx..."

# Create Nginx configuration
run_cmd "cat > /etc/nginx/sites-available/bdchatpro << 'EOF'
# Frontend (Next.js)
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
    server_name api.bdchatpro.com;

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
        add_header 'Access-Control-Allow-Origin' 'https://bdchatpro.com' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization' always;

        if (\$request_method = 'OPTIONS') {
            return 204;
        }
    }
}
EOF"

# Enable site
run_cmd "ln -sf /etc/nginx/sites-available/bdchatpro /etc/nginx/sites-enabled/"
run_cmd "rm -f /etc/nginx/sites-enabled/default"

# Test nginx configuration
run_cmd "nginx -t"

# 7. Setup SSL certificates
print_status "Setting up SSL certificates..."

# Get SSL certificate for both domains
run_cmd "certbot --nginx -d bdchatpro.com -d www.bdchatpro.com -d api.bdchatpro.com --non-interactive --agree-tos --email admin@bdchatpro.com"

# 8. Start services with PM2
print_status "Starting services with PM2..."

# Stop existing processes
run_cmd "pm2 delete all 2>/dev/null || true"

# Start backend
run_cmd "cd $REMOTE_PROJECT_DIR/backend && pm2 start --name 'bangla-chat-backend' 'source venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4'"

# Start frontend
run_cmd "cd $REMOTE_PROJECT_DIR && pm2 start --name 'bangla-chat-frontend' 'npm start'"

# Save PM2 configuration
run_cmd "pm2 save"
run_cmd "pm2 startup"
run_cmd "pm2 save"

# 9. Setup firewall
print_status "Configuring firewall..."
run_cmd "ufw --force enable"
run_cmd "ufw allow ssh"
run_cmd "ufw allow 'Nginx Full'"
run_cmd "ufw --force reload"

# 10. Restart services
print_status "Restarting services..."
run_cmd "systemctl restart nginx"
run_cmd "pm2 restart all"

# 11. Health checks
print_status "Running health checks..."

# Wait a moment for services to start
sleep 5

# Check if services are running
run_cmd "pm2 list"

# Check nginx status
run_cmd "systemctl status nginx --no-pager"

# Test endpoints
run_cmd "curl -s -o /dev/null -w '%{http_code}' https://bdchatpro.com/ || echo 'Frontend check failed'"
run_cmd "curl -s -o /dev/null -w '%{http_code}' https://api.bdchatpro.com/ || echo 'Backend check failed'"

print_success "Deployment completed!"
print_success "Frontend: https://bdchatpro.com"
print_success "Backend API: https://api.bdchatpro.com"
print_success "Admin login: admin@bdchatpro.com / admin123!@#"
print_warning "Remember to change the admin password after first login!"
print_warning "SSL certificates are set to auto-renew via certbot"

# Show logs
echo ""
print_status "Recent logs:"
run_cmd "pm2 logs --lines 10"
