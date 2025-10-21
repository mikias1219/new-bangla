# Bangla Chat Pro Deployment Guide

## Overview
This guide explains how to deploy Bangla Chat Pro with both frontend and backend on your domain.

## Architecture
- **Frontend**: Next.js application served on `https://bdchatpro.com`
- **Backend**: FastAPI application served on `https://bdchatpro.com/api`
- **Database**: SQLite (file-based)
- **Reverse Proxy**: Nginx
- **SSL**: Let's Encrypt certificates
- **Process Manager**: PM2

## Prerequisites
- Ubuntu/Debian server
- Domain name (bdchatpro.com)
- SSH access to server
- GitHub repository

## Local Development Workflow

### 1. Work on Local Machine
```bash
# Make your changes
cd /home/mikias/Mikias/Work/Projects/Freelance/bangla-chat-pro

# Test locally
./start.sh

# Commit and push changes
git add .
git commit -m "Your changes"
git push origin main  # or master
```

### 2. Deploy on Server
SSH into your server and run the deployment script:

```bash
# On your server (88.222.245.41)
cd /root/bangla-chat-pro
./server_deploy.sh
```

## Initial Server Setup

If this is your first deployment, set up the server:

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3 python3-pip python3-venv nginx certbot python3-certbot-nginx nodejs npm git curl

# Install PM2 globally
sudo npm install -g pm2

# Clone repository
cd /root
git clone https://github.com/yourusername/bangla-chat-pro.git

# Make deployment script executable
cd bangla-chat-pro
chmod +x server_deploy.sh
```

## Configuration

### Environment Variables

**Backend (.env)**:
```env
DATABASE_URL=sqlite:///./bangla_chat_pro.db
SECRET_KEY=your-super-secret-jwt-key-change-this-in-production-2025
OPENAI_API_KEY=YOUR_OPENAI_API_KEY_HERE
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
```

**Frontend (.env.local)**:
```env
NEXT_PUBLIC_BACKEND_URL=https://bdchatpro.com/api
NEXT_PUBLIC_SITE_URL=https://bdchatpro.com
```

### DNS Configuration

Point your domain to the server:
- `bdchatpro.com` → `88.222.245.41`
- `www.bdchatpro.com` → `88.222.245.41`
- API is proxied via `/api` on the main domain (no subdomain)

## Deployment Process

### Automated Deployment
1. **Local**: Make changes and push to GitHub
2. **Server**: Pull changes and redeploy
   ```bash
   cd /root/bangla-chat-pro
   ./server_deploy.sh
   ```

### Manual Deployment Steps
If you need to deploy manually:

```bash
# 1. Pull latest changes
cd /root/bangla-chat-pro
git pull origin main

# 2. Setup backend
cd backend
source venv/bin/activate
pip install -r requirements.txt
python create_admin.py

# 3. Setup frontend
cd ..
npm install
npm run build

# 4. Restart services
pm2 restart bangla-chat-backend
pm2 restart bangla-chat-frontend
sudo systemctl restart nginx
```

## Services

### PM2 Processes
- `bangla-chat-backend`: FastAPI backend on port 8000
- `bangla-chat-frontend`: Next.js frontend on port 3002

### Nginx Configuration
- Frontend: `https://bdchatpro.com` → `http://localhost:3002`
- Backend: `https://bdchatpro.com/api` → `http://localhost:8000`

## Admin Access

After deployment, access the admin panel:
- **URL**: `https://bdchatpro.com/admin`
- **Username**: `admin@bdchatpro.com`
- **Password**: `admin123!@#` (change this immediately!)

## Monitoring

### Check Service Status
```bash
# PM2 processes
pm2 list
pm2 logs

# Nginx status
sudo systemctl status nginx

# Check endpoints
curl -I https://bdchatpro.com
curl -I https://bdchatpro.com/api
```

### Logs
```bash
# Application logs
pm2 logs bangla-chat-backend
pm2 logs bangla-chat-frontend

# Nginx logs
sudo tail -f /var/log/nginx/bdchatpro.access.log
sudo tail -f /var/log/nginx/bdchatpro.error.log
```

## Troubleshooting

### SSL Certificate Issues
```bash
# Renew certificates
sudo certbot renew

# Check certificate status
sudo certbot certificates
```

### Database Issues
```bash
# Reset database (WARNING: This deletes all data)
cd /root/bangla-chat-pro/backend
rm bangla_chat_pro.db
python create_admin.py
```

### Service Not Starting
```bash
# Check PM2 logs
pm2 logs

# Restart services
pm2 restart all
sudo systemctl restart nginx
```

## Security Notes

1. **Change default admin password** immediately after first login
2. **Update SECRET_KEY** in production
3. **Configure firewall** properly
4. **Keep dependencies updated**
5. **Monitor logs regularly**

## Features Included

- ✅ User authentication and registration
- ✅ Subscription management
- ✅ AI chat with OpenAI integration
- ✅ Voice input/output
- ✅ Social media sharing
- ✅ Admin dashboard
- ✅ SQLite database
- ✅ SSL certificates
- ✅ Responsive design

## Support

For issues, check:
1. PM2 logs: `pm2 logs`
2. Nginx logs: `/var/log/nginx/`
3. Application logs in respective directories
