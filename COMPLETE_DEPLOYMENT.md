# Complete TradeFly Deployment - New Instance

## ✅ What's Already Done

1. ✅ New EC2 instance launched: `i-0c5f4b6f89dc9ef3a` (18.223.164.188)
2. ✅ Python 3.12, Nginx, Certbot installed
3. ✅ Security group configured (ports 22, 80, 443)

---

## 🚀 Quick Deployment (5 minutes)

### Step 1: SSH to New Instance

```bash
ssh -i "Botthentic n8n.pem" ubuntu@18.223.164.188
```

### Step 2: Create App Directory

```bash
sudo mkdir -p /var/www/tradefly
sudo chown ubuntu:ubuntu /var/www/tradefly
cd /var/www/tradefly
```

### Step 3: Copy Code from Old Instance

```bash
# From the OLD instance (3.144.234.232), create a tarball
# SSH to old instance first:
ssh -i "Botthentic n8n.pem" ubuntu@3.144.234.232

# On old instance:
cd /var/www/tradefly
tar -czf /tmp/tradefly-code.tar.gz --exclude='venv' --exclude='__pycache__' --exclude='*.pyc' *.py requirements.txt
exit

# Back on your local machine, copy from old to local:
scp -i "Botthentic n8n.pem" ubuntu@3.144.234.232:/tmp/tradefly-code.tar.gz /tmp/

# Copy from local to new instance:
scp -i "Botthentic n8n.pem" /tmp/tradefly-code.tar.gz ubuntu@18.223.164.188:/var/www/tradefly/

# SSH back to new instance:
ssh -i "Botthentic n8n.pem" ubuntu@18.223.164.188

# Extract on new instance:
cd /var/www/tradefly
tar -xzf tradefly-code.tar.gz
rm tradefly-code.tar.gz
```

### Step 4: Install Python Dependencies

```bash
cd /var/www/tradefly
python3.12 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 5: Create Systemd Service

```bash
sudo tee /etc/systemd/system/tradefly.service > /dev/null <<EOF
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
Environment="SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5wbGd4aHRoand3eXl3Ym52eHp0Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDE5MjE3MSwiZXhwIjoyMDc5NzY4MTcxfQ.qGhvTBRJ1Q49JvCOQ5Gb5IciFhsNFzEiEYQQ5wDZj9I"
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
```

### Step 6: Configure Nginx

```bash
sudo tee /etc/nginx/sites-available/tradefly > /dev/null <<EOF
server {
    listen 80;
    server_name api.tradeflyai.com;

    # Increase timeouts for long-running market scans
    proxy_connect_timeout 600;
    proxy_send_timeout 600;
    proxy_read_timeout 600;
    send_timeout 600;

    location / {
        proxy_pass http://localhost:8002;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable site
sudo ln -sf /etc/nginx/sites-available/tradefly /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test and restart
sudo nginx -t
sudo systemctl restart nginx
```

### Step 7: Test Everything

```bash
# Test local
curl http://localhost:8002/api/health

# Test external
curl http://18.223.164.188/api/health
```

---

## Step 8: Configure DNS

**In your domain registrar (where you bought tradeflyai.com):**

Add this A record:
```
Type: A
Name: api
Value: 18.223.164.188
TTL: 300
```

Wait 5-10 minutes, then test:
```bash
curl http://api.tradeflyai.com/api/health
```

---

## Step 9: Install SSL Certificate

**After DNS is working:**

```bash
# SSH to instance
ssh -i "Botthentic n8n.pem" ubuntu@18.223.164.188

# Get SSL certificate
sudo certbot --nginx -d api.tradeflyai.com

# Follow prompts:
# - Enter your email
# - Agree to terms
# - Choose "2" (redirect HTTP to HTTPS)
```

**Test HTTPS:**
```bash
curl https://api.tradeflyai.com/api/health
```

---

## ✅ Final Checklist

- [ ] Code copied from old instance
- [ ] Python dependencies installed
- [ ] Systemd service running
- [ ] Nginx configured
- [ ] DNS A record added (api.tradeflyai.com → 18.223.164.188)
- [ ] SSL certificate installed
- [ ] Test API: `curl https://api.tradeflyai.com/api/health`

---

## Service Management

```bash
# View logs
sudo journalctl -u tradefly -f

# Restart service
sudo systemctl restart tradefly

# Check status
sudo systemctl status tradefly
```

---

## Your Production URLs

- **Backend API:** https://api.tradeflyai.com
- **Health Check:** https://api.tradeflyai.com/api/health
- **Market Data:** https://api.tradeflyai.com/api/market/dynamic-watchlist
- **Options Signals:** https://api.tradeflyai.com/api/options/signals

---

## Next: Deploy Frontend to Vercel

Once the backend is working, deploy your frontend to Vercel and point it to:
```javascript
const API_URL = 'https://api.tradeflyai.com';
```

See `NEXT_STEPS.md` for frontend deployment guide.
