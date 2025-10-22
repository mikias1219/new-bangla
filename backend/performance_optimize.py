#!/usr/bin/env python3
"""
Performance Optimization Script for BanglaChatPro
Optimizes the application for Hostinger VPS deployment
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def check_system_requirements():
    """Check if system meets minimum requirements"""
    print("🔍 Checking system requirements...")

    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("❌ Python 3.8+ required")
        return False
    print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")

    # Check available memory
    try:
        with open('/proc/meminfo', 'r') as f:
            mem_info = f.read()
            mem_total = int([line for line in mem_info.split('\n') if 'MemTotal' in line][0].split()[1]) // 1024  # MB
            if mem_total < 1024:  # Less than 1GB
                print(f"⚠️ Low memory: {mem_total}MB (recommended: 2048MB+)")
            else:
                print(f"✅ Memory: {mem_total}MB")
    except:
        print("⚠️ Could not check memory")

    # Check disk space
    try:
        result = subprocess.run(['df', '/'], capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                disk_info = lines[1].split()
                available_gb = int(disk_info[3]) * 512 // (1024 * 1024 * 1024)  # Convert to GB
                if available_gb < 5:
                    print(f"⚠️ Low disk space: {available_gb}GB available (recommended: 10GB+)")
                else:
                    print(f"✅ Disk space: {available_gb}GB available")
    except:
        print("⚠️ Could not check disk space")

    return True

def optimize_database():
    """Optimize database configuration for VPS"""
    print("🗄️ Optimizing database configuration...")

    # Check if we're using SQLite (good for VPS)
    if os.getenv("DATABASE_URL", "").startswith("sqlite"):
        print("✅ Using SQLite (recommended for VPS)")

        # Optimize SQLite for better performance
        db_path = os.getenv("DATABASE_URL", "").replace("sqlite:///", "")
        if db_path and os.path.exists(db_path):
            # Enable WAL mode for better concurrency
            try:
                import sqlite3
                conn = sqlite3.connect(db_path)
                conn.execute("PRAGMA journal_mode=WAL;")
                conn.execute("PRAGMA synchronous=NORMAL;")
                conn.execute("PRAGMA cache_size=-64000;")  # 64MB cache
                conn.execute("PRAGMA temp_store=memory;")
                conn.commit()
                conn.close()
                print("✅ SQLite optimized for performance")
            except Exception as e:
                print(f"⚠️ Could not optimize SQLite: {e}")
    else:
        print("ℹ️ Using external database (PostgreSQL recommended for production)")

def optimize_application():
    """Optimize application settings for VPS"""
    print("⚙️ Optimizing application settings...")

    # Create optimized environment configuration
    env_optimized = {
        "UVICORN_WORKERS": "2",  # 2 workers for 1-2GB VPS
        "UVICORN_HOST": "0.0.0.0",
        "UVICORN_PORT": "8000",
        "MAX_REQUESTS_PER_WORKER": "1000",  # Restart worker after 1000 requests
        "WORKER_TIMEOUT": "30",
        "GRACEFUL_TIMEOUT": "10"
    }

    # Check current memory and adjust workers
    try:
        with open('/proc/meminfo', 'r') as f:
            mem_info = f.read()
            mem_total = int([line for line in mem_info.split('\n') if 'MemTotal' in line][0].split()[1]) // 1024

            if mem_total < 1024:  # Less than 1GB
                env_optimized["UVICORN_WORKERS"] = "1"
                print("⚠️ Low memory detected - using 1 worker")
            elif mem_total < 2048:  # Less than 2GB
                env_optimized["UVICORN_WORKERS"] = "2"
                print("✅ Using 2 workers for optimal performance")
            else:  # 2GB+
                env_optimized["UVICORN_WORKERS"] = "4"
                print("✅ Using 4 workers for high performance")
    except:
        print("ℹ️ Using default worker configuration")

    # Create optimized .env template
    env_content = []
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                key = line.split('=')[0] if '=' in line else line.strip()
                if key in env_optimized:
                    env_content.append(f"{key}={env_optimized[key]}")
                else:
                    env_content.append(line.rstrip())
    else:
        env_content = [f"{k}={v}" for k, v in env_optimized.items()]

    # Add performance optimizations
    performance_env = [
        "# Performance Optimizations",
        "PYTHONOPTIMIZE=1",
        "PYTHONDONTWRITEBYTECODE=1",
        "UVICORN_NO_ACCESS_LOG=1",  # Disable access logs for better performance
    ]

    env_content.extend(performance_env)

    with open('.env.optimized', 'w') as f:
        f.write('\n'.join(env_content))

    print("✅ Created optimized environment configuration (.env.optimized)")

def setup_nginx():
    """Setup optimized Nginx configuration"""
    print("🌐 Setting up optimized Nginx configuration...")

    nginx_config = """
# Optimized Nginx configuration for BanglaChatPro
upstream bangla_chat_backend {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;  # Backup worker
    keepalive 32;
}

server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    # Static files caching
    location /static/ {
        alias /path/to/your/static/files/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # API endpoints
    location /api/ {
        proxy_pass http://bangla_chat_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeout settings
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;

        # Buffer settings for better performance
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }

    # Frontend (Next.js)
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;

        # Frontend caching
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\\n";
        add_header Content-Type text/plain;
    }
}
"""

    with open('nginx.conf.optimized', 'w') as f:
        f.write(nginx_config)

    print("✅ Created optimized Nginx configuration (nginx.conf.optimized)")
    print("   Remember to:")
    print("   - Replace 'your-domain.com' with your actual domain")
    print("   - Update static file paths")
    print("   - Copy to /etc/nginx/sites-available/")

def create_systemd_service():
    """Create optimized systemd service file"""
    print("🔧 Creating optimized systemd service...")

    service_config = """[Unit]
Description=BanglaChatPro Backend
After=network.target
Requires=network.target

[Service]
Type=exec
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/bangla-chat-pro/backend
Environment=PATH=/home/ubuntu/bangla-chat-pro/backend/venv/bin
ExecStart=/home/ubuntu/bangla-chat-pro/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
ExecReload=/bin/kill -s HUP $MAINPID

# Performance optimizations
Restart=always
RestartSec=5
LimitNOFILE=65536

# Security
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ReadWritePaths=/home/ubuntu/bangla-chat-pro
ProtectHome=yes

[Install]
WantedBy=multi-user.target
"""

    with open('bangla-chat.service', 'w') as f:
        f.write(service_config)

    print("✅ Created systemd service file (bangla-chat.service)")
    print("   Copy to: sudo cp bangla-chat.service /etc/systemd/system/")
    print("   Enable: sudo systemctl enable bangla-chat")
    print("   Start: sudo systemctl start bangla-chat")

def create_monitoring_script():
    """Create basic monitoring script"""
    print("📊 Creating monitoring script...")

    monitoring_script = """#!/bin/bash
# BanglaChatPro Health Monitoring Script

echo "🔍 BanglaChatPro Health Check - $(date)"

# Check if backend is running
if curl -f -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend: RUNNING"
else
    echo "❌ Backend: DOWN"
fi

# Check if frontend is running
if curl -f -s http://localhost:3000 > /dev/null; then
    echo "✅ Frontend: RUNNING"
else
    echo "❌ Frontend: DOWN"
fi

# Check database connectivity
if [ -f "bangla_chat_pro.db" ]; then
    DB_SIZE=$(du -h bangla_chat_pro.db | cut -f1)
    echo "✅ Database: ${DB_SIZE}"
else
    echo "❌ Database: NOT FOUND"
fi

# Check system resources
echo "📈 System Resources:"
echo "  CPU: $(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\\([0-9.]*\\)%* id.*/\\1/" | awk '{print 100 - $1"%"}')"
echo "  Memory: $(free -h | grep "^Mem:" | awk '{print $3 "/" $2}')"

# Check recent errors in logs
if [ -f "logs/app.log" ]; then
    ERROR_COUNT=$(grep -c "ERROR" logs/app.log 2>/dev/null || echo "0")
    echo "⚠️ Recent Errors: ${ERROR_COUNT}"
fi

echo "✅ Health check completed"
"""

    with open('health-check.sh', 'w') as f:
        f.write(monitoring_script)

    # Make executable
    os.chmod('health-check.sh', 0o755)

    print("✅ Created health monitoring script (health-check.sh)")
    print("   Run: ./health-check.sh")
    print("   Setup cron: */5 * * * * /path/to/health-check.sh")

def create_backup_script():
    """Create automated backup script"""
    print("💾 Creating backup script...")

    backup_script = """#!/bin/bash
# BanglaChatPro Automated Backup Script

BACKUP_DIR="/home/ubuntu/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="bangla_chat_backup_${TIMESTAMP}"

echo "💾 Creating backup: ${BACKUP_NAME}"

# Create backup directory
mkdir -p ${BACKUP_DIR}

# Backup database
if [ -f "bangla_chat_pro.db" ]; then
    cp bangla_chat_pro.db ${BACKUP_DIR}/${BACKUP_NAME}.db
    echo "✅ Database backed up"
else
    echo "❌ Database file not found"
    exit 1
fi

# Backup environment file
if [ -f ".env" ]; then
    cp .env ${BACKUP_DIR}/${BACKUP_NAME}.env
    echo "✅ Environment file backed up"
fi

# Backup embeddings and documents
if [ -d "embeddings" ]; then
    tar -czf ${BACKUP_DIR}/${BACKUP_NAME}_embeddings.tar.gz embeddings/
    echo "✅ Embeddings backed up"
fi

if [ -d "uploads" ]; then
    tar -czf ${BACKUP_DIR}/${BACKUP_NAME}_uploads.tar.gz uploads/
    echo "✅ Uploads backed up"
fi

# Compress backup
cd ${BACKUP_DIR}
tar -czf ${BACKUP_NAME}.tar.gz ${BACKUP_NAME}.db ${BACKUP_NAME}.env ${BACKUP_NAME}_embeddings.tar.gz ${BACKUP_NAME}_uploads.tar.gz 2>/dev/null
rm ${BACKUP_NAME}.db ${BACKUP_NAME}.env ${BACKUP_NAME}_embeddings.tar.gz ${BACKUP_NAME}_uploads.tar.gz 2>/dev/null

# Clean old backups (keep last 7 days)
find ${BACKUP_DIR} -name "bangla_chat_backup_*.tar.gz" -mtime +7 -delete

echo "✅ Backup completed: ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz"
echo "📊 Backup size: $(du -h ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz | cut -f1)"
"""

    with open('backup.sh', 'w') as f:
        f.write(backup_script)

    os.chmod('backup.sh', 0o755)

    print("✅ Created backup script (backup.sh)")
    print("   Run manual backup: ./backup.sh")
    print("   Setup daily backup: 0 2 * * * /path/to/backup.sh")

def main():
    """Run all performance optimizations"""
    print("🚀 BanglaChatPro Performance Optimization for VPS")
    print("=" * 60)

    # Change to backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)

    optimizations = [
        ("System Requirements Check", check_system_requirements),
        ("Database Optimization", optimize_database),
        ("Application Optimization", optimize_application),
        ("Nginx Configuration", setup_nginx),
        ("Systemd Service", create_systemd_service),
        ("Monitoring Setup", create_monitoring_script),
        ("Backup Setup", create_backup_script)
    ]

    completed = 0
    total = len(optimizations)

    for opt_name, opt_func in optimizations:
        print(f"\n🔧 {opt_name}...")
        try:
            if opt_func():
                completed += 1
                print(f"✅ {opt_name} completed")
            else:
                print(f"⚠️ {opt_name} completed with warnings")
        except Exception as e:
            print(f"❌ {opt_name} failed: {e}")

    print(f"\n📊 Optimization Results: {completed}/{total} completed")

    if completed == total:
        print("🎉 All optimizations completed successfully!")
        print("\n📋 Next Steps:")
        print("  1. Review and apply .env.optimized settings")
        print("  2. Copy nginx.conf.optimized to /etc/nginx/sites-available/")
        print("  3. Copy bangla-chat.service to /etc/systemd/system/")
        print("  4. Run: sudo systemctl daemon-reload && sudo systemctl enable bangla-chat")
        print("  5. Setup monitoring: */5 * * * * /path/to/health-check.sh")
        print("  6. Setup backups: 0 2 * * * /path/to/backup.sh")
        print("  7. Test your deployment with: ./health-check.sh")
    else:
        print("⚠️ Some optimizations may need manual attention.")

if __name__ == "__main__":
    main()
