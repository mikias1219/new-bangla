#!/bin/bash

echo "🔄 Bangla Chat Pro Production Update Script"
echo "==========================================="

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

print_status "Starting update process..."

# 1. Push local changes to GitHub
print_status "Pushing local changes to GitHub..."
if git status --porcelain | grep -q .; then
    git add .
    git commit -m "Update: $(date)"
    git push origin master
else
    print_status "No local changes to push"
fi

# 2. Pull latest changes on server
print_status "Pulling latest changes on server..."
run_remote "cd $REMOTE_PROJECT_DIR && git pull origin master"

# 3. Update backend dependencies
print_status "Updating backend..."
run_remote "cd $REMOTE_PROJECT_DIR/backend && source venv/bin/activate && pip install -r requirements.txt"

# 4. Update frontend dependencies and build
print_status "Updating frontend..."
run_remote "cd $REMOTE_PROJECT_DIR && npm install"
run_remote "cd $REMOTE_PROJECT_DIR && npm run build"

# 5. Restart services
print_status "Restarting services..."
run_remote "pm2 restart all"
run_remote "systemctl restart nginx"

# 6. Health checks
print_status "Running health checks..."
sleep 5

# Check PM2 status
run_remote "pm2 list"

# Test endpoints
print_status "Testing endpoints..."
run_remote "curl -s -o /dev/null -w 'Frontend HTTP status: %{http_code}\n' https://$DOMAIN/ || echo 'Frontend check failed'"
run_remote "curl -s -o /dev/null -w 'Backend API HTTP status: %{http_code}\n' https://api.$DOMAIN/ || echo 'Backend API check failed'"

print_success "Update completed successfully!"
print_success "Frontend: https://$DOMAIN"
print_success "Backend API: https://api.$DOMAIN"

# Show recent logs
echo ""
print_status "Recent PM2 logs:"
run_remote "pm2 logs --lines 5"
