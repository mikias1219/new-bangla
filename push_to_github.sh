#!/bin/bash

echo "🚀 Pushing Bangla Chat Pro to GitHub..."

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Clean up cache files
echo -e "${BLUE}[INFO]${NC} Cleaning up cache files..."
rm -rf backend/app/__pycache__ backend/app/auth/__pycache__ backend/app/models/__pycache__ backend/app/routers/__pycache__ backend/venv .next

# Add and commit changes
echo -e "${BLUE}[INFO]${NC} Committing changes..."
git add .
git commit -m "feat: Complete Bangla Chat Pro with admin, voice, social features

- Admin dashboard and user management
- Voice chat with speech recognition and TTS
- Social media integration for AI responses
- SQLite database configuration
- SSL certificates and production deployment
- PM2 process management and Nginx reverse proxy"

# Set GitHub remote
echo -e "${BLUE}[INFO]${NC} Setting up GitHub remote..."
git remote add github https://github.com/mikias1219/new-bangla.git 2>/dev/null || echo "Remote already exists"

# Push to GitHub
echo -e "${YELLOW}[WARNING]${NC} Pushing to GitHub (you may need to authenticate)..."
if git push github master; then
    echo -e "${GREEN}[SUCCESS]${NC} Code pushed to GitHub successfully!"
    echo -e "${GREEN}[NEXT]${NC} Now run this on your server (88.222.245.41):"
    echo "cd /root/bangla-chat-pro && ./server_deploy.sh"
else
    echo -e "${RED}[ERROR]${NC} Failed to push to GitHub. You may need to:"
    echo "1. Create a Personal Access Token on GitHub"
    echo "2. Use: git push https://mikias1219:YOUR_TOKEN@github.com/mikias1219/new-bangla.git master"
fi
