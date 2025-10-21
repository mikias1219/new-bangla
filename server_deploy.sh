#!/bin/bash

# Server-side deployment script for Bangla Chat Pro
# Run this on the server after pushing changes to GitHub

echo "🚀 Bangla Chat Pro Server Deployment..."

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

# 2. Setup backend
print_status "Setting up backend..."
cd $PROJECT_DIR/backend

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
DATABASE_URL=sqlite:///./bangla_chat_pro.db
SECRET_KEY=your-super-secret-jwt-key-change-this-in-production-2025
OPENAI_API_KEY=YOUR_OPENAI_API_KEY_HERE
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
EOF

# Create admin user if it doesn't exist
print_status "Ensuring admin user exists..."
python3 create_admin.py

# 3. Setup frontend
print_status "Setting up frontend..."
cd $PROJECT_DIR

# Install dependencies
print_status "Installing Node dependencies..."
npm install

# Create production environment file
print_status "Setting up frontend environment..."
cat > .env.local << 'EOF'
NEXT_PUBLIC_BACKEND_URL=https://bdchatpro.com/api
NEXT_PUBLIC_SITE_URL=https://bdchatpro.com
EOF

# Build frontend
print_status "Building frontend..."
npm run build

# 4. Configure Nginx (if not already configured)
print_status "Ensuring Nginx configuration..."
if [ ! -f "/etc/nginx/sites-enabled/bdchatpro" ]; then
    print_status "Setting up Nginx configuration..."

    # Create Nginx configuration
    cat > /etc/nginx/sites-available/bdchatpro << 'EOF'
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

    # Frontend routes
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

    # Backend API routes
    location /api/ {
        proxy_pass http://localhost:8000/;
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

# 6. Start/restart services with PM2
print_status "Starting services with PM2..."

# Stop existing processes
pm2 delete bangla-chat-backend bangla-chat-frontend 2>/dev/null || true

# Start backend
cd $PROJECT_DIR/backend
pm2 start --name bangla-chat-backend "source venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4"

# Start frontend
cd $PROJECT_DIR
pm2 start --name bangla-chat-frontend "npm start"

# Save PM2 configuration
pm2 save

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
