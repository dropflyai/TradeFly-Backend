# TradeFly - Production Deployment Strategy

## Current Status
- ✅ Backend deployed on EC2 (3.144.234.232:8002)
- ✅ Supabase database configured
- ✅ Frontend accessible at http://3.144.234.232:8002
- ⚠️ Running with nohup (not production-ready)

---

## Recommended Strategy: Hybrid Vercel + EC2

### Architecture Overview
```
User → Vercel CDN (Frontend) → EC2 Backend (API) → Supabase (Database)
```

### Why This Approach?

**Vercel for Frontend:**
- Global CDN (faster load times worldwide)
- Automatic SSL certificates
- Zero configuration deployment
- Git-based deployments (push to deploy)
- Free tier: 100GB bandwidth/month

**EC2 for Backend:**
- Full control over Python environment
- Handle long-running market scans
- Cost-effective for compute-intensive tasks
- Easy to scale vertically (upgrade instance size)

**Supabase for Database:**
- Managed PostgreSQL (no maintenance)
- Automatic backups
- REST API built-in
- Free tier: 500MB database, 2GB egress/month

---

## Phase 1: Harden EC2 Backend (Do First)

### 1.1 Create Systemd Service (Auto-Restart)

Currently using `nohup`, which doesn't auto-restart on crash or reboot.

**Create service file on EC2:**
```bash
sudo tee /etc/systemd/system/tradefly.service > /dev/null << 'EOF'
[Unit]
Description=TradeFly Options Trading API
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/var/www/tradefly
Environment="PATH=/var/www/tradefly/venv/bin"
Environment="POLYGON_API_KEY=3LJuAPplRFEeAlnMDHkmFVK93hcxEftF"
Environment="SUPABASE_URL=https://nplgxhthjwwyywbnvxzt.supabase.co"
Environment="SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
Environment="PORT=8002"
Environment="ACCOUNT_BALANCE=10000"
ExecStart=/var/www/tradefly/venv/bin/python3 main_options.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable tradefly
sudo systemctl start tradefly

# Check status
sudo systemctl status tradefly

# View logs
sudo journalctl -u tradefly -f
```

**Benefits:**
- Auto-starts on server reboot
- Auto-restarts on crash
- Centralized logging with journalctl
- Managed by systemd (standard Linux service manager)

### 1.2 Install Nginx Reverse Proxy

**Why?**
- Better performance than FastAPI serving directly
- Can add rate limiting
- Easy SSL certificate management
- Can serve multiple apps on same server

**Install and configure:**
```bash
# Install Nginx
sudo apt update
sudo apt install -y nginx

# Create config
sudo tee /etc/nginx/sites-available/tradefly > /dev/null << 'EOF'
server {
    listen 80;
    server_name _;  # Accept all for now

    # Increase timeouts for long-running scans
    proxy_connect_timeout 600;
    proxy_send_timeout 600;
    proxy_read_timeout 600;
    send_timeout 600;

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
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/tradefly /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default  # Remove default site

# Test and restart
sudo nginx -t
sudo systemctl restart nginx
```

**After this, your API will be available at:**
- http://3.144.234.232 (port 80, no need to specify :8002)

### 1.3 Add SSL Certificate (HTTPS)

**Only do this if you have a custom domain.**

If you have a domain (e.g., api.tradefly.com):

```bash
# Install certbot
sudo apt install -y certbot python3-certbot-nginx

# Get SSL certificate (auto-configures Nginx)
sudo certbot --nginx -d api.tradefly.com

# Test auto-renewal
sudo certbot renew --dry-run
```

**After SSL, your API will be:**
- https://api.tradefly.com (secure, production-ready)

### 1.4 Update Security Group

Currently port 8002 is open. After Nginx setup:

**Update EC2 Security Group:**
- ✅ Keep port 22 (SSH)
- ✅ Keep port 80 (HTTP)
- ✅ Add port 443 (HTTPS) if using SSL
- ❌ Remove port 8002 (backend should only be accessed via Nginx)

---

## Phase 2: Deploy Frontend to Vercel

### 2.1 Extract Frontend Files

Your frontend is currently in `/Users/rioallen/.../TradeFly-Backend/frontend/`

**Create separate frontend repo:**
```bash
cd /Users/rioallen/Documents/DropFly-OS-App-Builder/DropFly-PROJECTS
mkdir TradeFly-Frontend
cd TradeFly-Frontend

# Copy frontend files
cp -r ../TradeFly-Backend/frontend/* .

# Update API URL in frontend code
# Change from relative URLs to absolute EC2 URL
```

### 2.2 Update API URLs in Frontend

Find all API calls and update:

**Before (relative URLs):**
```javascript
fetch('/api/market/dynamic-watchlist')
```

**After (absolute URLs):**
```javascript
// For development
const API_URL = import.meta.env.DEV
  ? 'http://localhost:8002'
  : 'http://3.144.234.232';  // Replace with your domain later

fetch(`${API_URL}/api/market/dynamic-watchlist`)
```

### 2.3 Push to GitHub

```bash
cd /Users/rioallen/Documents/DropFly-OS-App-Builder/DropFly-PROJECTS/TradeFly-Frontend

git init
git add .
git commit -m "Initial commit: TradeFly frontend"

# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/TradeFly-Frontend.git
git branch -M main
git push -u origin main
```

### 2.4 Deploy to Vercel

1. Go to https://vercel.com/new
2. Import your GitHub repo
3. Configure:
   - **Framework Preset:** Auto-detect (or select your framework)
   - **Root Directory:** ./
   - **Build Command:** (auto-detected)
   - **Environment Variables:**
     - `VITE_API_URL=http://3.144.234.232` (or your domain)
4. Click "Deploy"

**Your frontend will be live at:**
- https://tradefly-frontend.vercel.app (or custom domain)

---

## Phase 3: Add Custom Domain (Optional but Recommended)

### 3.1 Purchase Domain

Buy a domain (e.g., tradefly.io) from:
- Namecheap (~$12/year)
- Google Domains
- GoDaddy

### 3.2 Configure DNS (Route 53 or Domain Registrar)

**Backend API (EC2):**
- Create A record: `api.tradefly.io` → `3.144.234.232`

**Frontend (Vercel):**
- Vercel will provide CNAME instructions
- Create CNAME: `app.tradefly.io` → `cname.vercel-dns.com`

### 3.3 Update API URL in Frontend

```javascript
const API_URL = 'https://api.tradefly.io';
```

Redeploy frontend to Vercel (auto-deploys on git push).

---

## Cost Breakdown

### Current Setup (EC2 Only)
- EC2 t3.medium: **~$30/month**
- Supabase Free Tier: **$0**
- **Total: $30/month**

### Recommended Setup (Vercel + EC2)
- EC2 t3.small: **$15/month** (can downsize since only serving API)
- Vercel Free Tier: **$0** (100GB bandwidth)
- Supabase Free Tier: **$0**
- Domain: **$12/year** ($1/month)
- **Total: $16/month**

**Savings:** $14/month + Better performance + Auto-scaling frontend

---

## Monitoring & Maintenance

### Set Up CloudWatch (EC2 Monitoring)

```bash
# Install CloudWatch agent on EC2
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i amazon-cloudwatch-agent.deb

# Configure basic monitoring (CPU, Memory, Disk)
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
  -a fetch-config \
  -m ec2 \
  -s -c default
```

**Set up alerts:**
- CPU > 80% for 5 minutes
- Memory > 80%
- Disk > 90%

### Set Up Uptime Monitoring

Use free services:
- **UptimeRobot** (https://uptimerobot.com) - Free, 5-minute checks
- **Better Uptime** - Free tier available

Monitor:
- https://api.tradefly.io/api/health (every 5 minutes)
- https://app.tradefly.io (every 5 minutes)

Get alerts via:
- Email
- Slack
- SMS (paid)

---

## Security Checklist

- [ ] Systemd service running (not nohup)
- [ ] Nginx reverse proxy installed
- [ ] SSL certificate installed (if custom domain)
- [ ] EC2 security group: Only 22, 80, 443 open (remove 8002)
- [ ] SSH key-based auth only (no passwords)
- [ ] Environment variables not committed to git
- [ ] Supabase Row Level Security enabled
- [ ] Regular security updates: `sudo apt update && sudo apt upgrade`
- [ ] Cloudwatch monitoring active
- [ ] Uptime monitoring configured

---

## Deployment Workflow (After Setup)

### Update Backend (EC2)
```bash
# SSH to EC2
ssh -i your-key.pem ubuntu@3.144.234.232

# Pull latest code
cd /var/www/tradefly
git pull

# Install any new dependencies
source venv/bin/activate
pip install -r requirements.txt

# Restart service
sudo systemctl restart tradefly

# Check logs
sudo journalctl -u tradefly -f
```

### Update Frontend (Vercel)
```bash
# Just push to GitHub
git add .
git commit -m "Update frontend"
git push

# Vercel auto-deploys (takes 1-2 minutes)
```

---

## Next Steps (Priority Order)

1. **NOW: Set up systemd service** (20 minutes) - Critical for stability
2. **NOW: Install Nginx** (15 minutes) - Better performance
3. **THIS WEEK: Push code to GitHub** (30 minutes) - Version control
4. **THIS WEEK: Deploy frontend to Vercel** (1 hour) - Faster, cheaper
5. **OPTIONAL: Buy custom domain** (2 hours) - Professional look
6. **OPTIONAL: Set up monitoring** (1 hour) - Peace of mind

---

## Questions?

**Q: Do I need a custom domain?**
A: No, but recommended for production. You can use IP address or Vercel's free subdomain.

**Q: Can I stay on EC2 only?**
A: Yes, but Vercel is faster, cheaper, and easier for the frontend.

**Q: How do I update the backend without downtime?**
A: Systemd will restart the service automatically. Or use blue-green deployment (advanced).

**Q: What if EC2 crashes?**
A: Systemd auto-restarts. Add CloudWatch + SNS for alerts.

**Q: Can I scale this for 1000s of users?**
A: Frontend scales automatically on Vercel. Backend: Upgrade EC2 instance or add load balancer.
