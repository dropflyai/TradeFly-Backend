# TradeFly Backend - EC2 Production Deployment Guide

## Prerequisites

1. **AWS Account** with EC2 access
2. **Supabase Project** (create at https://supabase.com)
3. **Polygon/Massive API Key**

---

## Step 1: Set Up Supabase Database

### 1.1 Create Supabase Project

1. Go to https://supabase.com/dashboard
2. Click "New Project"
3. Name it "TradeFly" 
4. Choose a strong database password
5. Select region closest to your users (e.g., us-east-1)

### 1.2 Run SQL Schema

1. In Supabase dashboard, go to "SQL Editor"
2. Open `supabase_schema.sql` from this repo
3. Copy all SQL and paste into editor
4. Click "Run"
5. Verify tables created (check "Table Editor")

### 1.3 Get Supabase Credentials

In your Supabase project settings:
- **Project URL**: `https://xxx.supabase.co`
- **Service Role Key** (secret): Found under Settings → API → service_role

---

## Step 2: Launch EC2 Instance

### 2.1 Launch Instance

```bash
# From AWS Console or CLI
Instance Type: t3.small (2 vCPU, 2GB RAM) - $15/month
AMI: Ubuntu 22.04 LTS
Storage: 20GB gp3
Security Group: Allow ports 22 (SSH), 80 (HTTP), 443 (HTTPS)
```

### 2.2 Connect to Instance

```bash
# Download your .pem key from AWS
chmod 400 tradefly-key.pem
ssh -i tradefly-key.pem ubuntu@<EC2_PUBLIC_IP>
```

---

## Step 3: Install Dependencies on EC2

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo apt install -y python3.11 python3.11-venv python3-pip git

# Install Nginx (reverse proxy)
sudo apt install -y nginx

# Install certbot (SSL certificates)
sudo apt install -y certbot python3-certbot-nginx
```

---

## Step 4: Deploy Application

### 4.1 Clone Repository

```bash
# Create app directory
sudo mkdir -p /var/www/tradefly
sudo chown ubuntu:ubuntu /var/www/tradefly
cd /var/www/tradefly

# Clone your repo (replace with your repo URL)
git clone https://github.com/YOUR_USERNAME/TradeFly-Backend.git .
```

### 4.2 Set Up Python Environment

```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 4.3 Create Environment File

```bash
# Create .env file
cat > .env << 'ENVEOF'
# Polygon/Massive API
POLYGON_API_KEY=your_polygon_api_key_here

# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_KEY=your_service_role_key_here

# App Config
ACCOUNT_BALANCE=10000
PORT=8002
ENVEOF

# Secure the file
chmod 600 .env
```

### 4.4 Test the Application

```bash
# Activate venv
source venv/bin/activate

# Run server
python3 main_options.py

# In another terminal, test
curl http://localhost:8002/api/health
```

---

## Step 5: Create Systemd Service (Auto-Start)

### 5.1 Create Service File

```bash
sudo cat > /etc/systemd/system/tradefly.service << 'SERVICE_EOF'
[Unit]
Description=TradeFly Options Trading API
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/var/www/tradefly
Environment="PATH=/var/www/tradefly/venv/bin"
EnvironmentFile=/var/www/tradefly/.env
ExecStart=/var/www/tradefly/venv/bin/python3 main_options.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICE_EOF
```

### 5.2 Enable and Start Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service (start on boot)
sudo systemctl enable tradefly

# Start service
sudo systemctl start tradefly

# Check status
sudo systemctl status tradefly

# View logs
sudo journalctl -u tradefly -f
```

---

## Step 6: Configure Nginx Reverse Proxy

### 6.1 Create Nginx Config

```bash
sudo cat > /etc/nginx/sites-available/tradefly << 'NGINX_EOF'
server {
    listen 80;
    server_name your-domain.com;  # Replace with your domain

    location / {
        proxy_pass http://localhost:8002;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
NGINX_EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/tradefly /etc/nginx/sites-enabled/

# Test config
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

### 6.2 Set Up SSL (HTTPS)

```bash
# Get free SSL certificate from Let's Encrypt
sudo certbot --nginx -d your-domain.com

# Auto-renewal is configured automatically
# Test renewal
sudo certbot renew --dry-run
```

---

## Step 7: Update Frontend to Use Production API

In your frontend code, update the API URL:

```javascript
// OLD (localhost)
const API_URL = 'http://localhost:8002';

// NEW (production)
const API_URL = 'https://your-domain.com';
```

---

## Maintenance Commands

### View Logs
```bash
# Real-time logs
sudo journalctl -u tradefly -f

# Last 100 lines
sudo journalctl -u tradefly -n 100

# Errors only
sudo journalctl -u tradefly -p err
```

### Restart Service
```bash
sudo systemctl restart tradefly
```

### Update Code
```bash
cd /var/www/tradefly
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart tradefly
```

### Monitor Resources
```bash
# CPU/Memory usage
htop

# Disk space
df -h

# Service status
sudo systemctl status tradefly
```

---

## Cost Estimate

- **EC2 t3.small**: $15/month
- **Supabase Free Tier**: $0 (500MB database, 2GB bandwidth)
- **Domain (optional)**: $12/year
- **Total**: ~$15-20/month

---

## Troubleshooting

### Service won't start
```bash
# Check logs
sudo journalctl -u tradefly -n 50

# Check if port 8002 is in use
sudo lsof -i :8002

# Test manually
cd /var/www/tradefly
source venv/bin/activate
python3 main_options.py
```

### Database connection issues
```bash
# Test Supabase connection
python3 -c "from supabase_client import get_db; db = get_db(); print('Connected:', db.is_connected())"
```

### Nginx errors
```bash
# Test config
sudo nginx -t

# View error log
sudo tail -f /var/log/nginx/error.log
```

---

## Security Checklist

- [ ] EC2 security group allows only ports 22, 80, 443
- [ ] SSH key-based authentication only (no password login)
- [ ] `.env` file has 600 permissions
- [ ] Supabase service key is secret (never commit to git)
- [ ] SSL certificate installed and auto-renewing
- [ ] Regular system updates enabled

---

## Next Steps

1. Set up monitoring (CloudWatch, UptimeRobot)
2. Configure automated backups (Supabase handles this)
3. Set up CI/CD pipeline (GitHub Actions)
4. Add custom domain with Route 53
5. Implement rate limiting
6. Add user authentication

