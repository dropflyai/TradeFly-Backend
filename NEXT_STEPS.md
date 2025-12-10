# TradeFly Production Deployment - Next Steps

## ✅ What's Been Completed

1. **Systemd Service** - TradeFly backend runs as a proper service
   - Auto-restarts on crash
   - Starts on server reboot
   - Centralized logging with `journalctl`

2. **Nginx Reverse Proxy** - Installed and configured
   - Ready to serve traffic on port 80
   - Configured for `api.tradeflyai.com`
   - Long timeouts for market scans (600s)

3. **Backend Running** - Python API is active
   - Service status: Active (running)
   - Port: 8002 (internal)
   - Health check working locally

---

## 🚨 Action Required: Manual Steps

### Step 1: Open Ports in AWS Security Group (YOU MUST DO THIS)

**Go to AWS Console:**
1. Navigate to EC2 → Security Groups
2. Find security group: `sg-06b940034b2b8abfb`
3. Click "Edit inbound rules"
4. Add these two rules:

| Type  | Protocol | Port | Source    | Description              |
|-------|----------|------|-----------|--------------------------|
| HTTP  | TCP      | 80   | 0.0.0.0/0 | Public web traffic       |
| HTTPS | TCP      | 443  | 0.0.0.0/0 | Secure web traffic (SSL) |

5. Click "Save rules"

**After this, your API will be accessible at:**
- http://3.144.234.232/api/health (test this first)

---

### Step 2: Configure DNS for tradeflyai.com

**In your domain registrar (where you bought tradeflyai.com):**

Add this A record:
```
Type: A
Name: api
Value: 3.144.234.232
TTL: 300 (5 minutes)
```

**This will make your API available at:**
- http://api.tradeflyai.com

**Wait 5-10 minutes for DNS to propagate, then test:**
```bash
# Check DNS
nslookup api.tradeflyai.com

# Test API
curl http://api.tradeflyai.com/api/health
```

---

### Step 3: Install SSL Certificate (After DNS is working)

**SSH into your EC2 instance:**
```bash
ssh -i your-key.pem ubuntu@3.144.234.232
```

**Run certbot to get free SSL certificate:**
```bash
sudo certbot --nginx -d api.tradeflyai.com
```

**Follow the prompts:**
- Enter your email
- Agree to terms
- Choose "2" (redirect HTTP to HTTPS)

**After this, your API will be:**
- https://api.tradeflyai.com (secure!)

---

### Step 4: Test Everything

```bash
# Test health check
curl https://api.tradeflyai.com/api/health

# Test market data
curl https://api.tradeflyai.com/api/market/dynamic-watchlist

# Test options signals
curl "https://api.tradeflyai.com/api/options/signals?min_confidence=0.7&max_results=5"
```

---

## 📦 Frontend Deployment to Vercel

### Step 1: Find Frontend Files

Your frontend is currently embedded in the backend. Check:
```bash
ls /Users/rioallen/Documents/DropFly-OS-App-Builder/DropFly-PROJECTS/TradeFly-Backend/frontend/
# OR
ls /Users/rioallen/Documents/DropFly-OS-App-Builder/DropFly-PROJECTS/TradeFly-Backend/static/
```

### Step 2: Update API URLs in Frontend

Find all API calls in your frontend JavaScript and update them:

**Before (relative URLs):**
```javascript
fetch('/api/market/dynamic-watchlist')
```

**After (absolute URLs):**
```javascript
const API_URL = 'https://api.tradeflyai.com';
fetch(`${API_URL}/api/market/dynamic-watchlist`)
```

### Step 3: Create New Frontend Repository

```bash
# Create frontend directory
cd /Users/rioallen/Documents/DropFly-OS-App-Builder/DropFly-PROJECTS
mkdir TradeFly-Frontend
cd TradeFly-Frontend

# Copy frontend files
cp -r ../TradeFly-Backend/frontend/* .
# OR if they're in static/
cp -r ../TradeFly-Backend/static/* .

# Initialize git
git init
git add .
git commit -m "Initial commit: TradeFly frontend"
```

### Step 4: Push to GitHub

1. Go to https://github.com/new
2. Create a new repository called "TradeFly-Frontend"
3. Don't initialize with README
4. Run these commands:

```bash
git remote add origin https://github.com/YOUR_USERNAME/TradeFly-Frontend.git
git branch -M main
git push -u origin main
```

### Step 5: Deploy to Vercel

1. Go to https://vercel.com/new
2. Import your GitHub repository "TradeFly-Frontend"
3. Configure:
   - **Framework Preset:** Auto-detect (or select your framework)
   - **Root Directory:** ./
   - **Build Command:** (leave default or specify if needed)
   - **Output Directory:** (leave default or specify if needed)
4. **Environment Variables:** (if needed)
   - `VITE_API_URL=https://api.tradeflyai.com`
5. Click "Deploy"

### Step 6: Configure Custom Domain in Vercel

After deployment succeeds:

1. In Vercel dashboard, go to your project
2. Click "Settings" → "Domains"
3. Add domain: `app.tradeflyai.com` (or `www.tradeflyai.com`)
4. Vercel will show you DNS instructions

**In your domain registrar, add:**
```
Type: CNAME
Name: app (or www)
Value: cname.vercel-dns.com (Vercel will provide exact value)
TTL: 300
```

**After DNS propagates (5-10 minutes), your app will be live at:**
- https://app.tradeflyai.com

---

## 🎯 Final Architecture

```
User
  ↓
app.tradeflyai.com (Vercel - Frontend)
  ↓
api.tradeflyai.com (EC2 - Backend API)
  ↓
Supabase (Database)
```

---

## 📊 Service Management Commands

```bash
# Check service status
sudo systemctl status tradefly

# View real-time logs
sudo journalctl -u tradefly -f

# Restart service
sudo systemctl restart tradefly

# Stop service
sudo systemctl stop tradefly

# Start service
sudo systemctl start tradefly
```

---

## 🔄 Updating Backend Code

```bash
# SSH to EC2
ssh -i your-key.pem ubuntu@3.144.234.232

# Go to app directory
cd /var/www/tradefly

# Pull latest code (once pushed to GitHub)
git pull

# Activate venv and install dependencies
source venv/bin/activate
pip install -r requirements.txt

# Restart service
sudo systemctl restart tradefly

# Check logs
sudo journalctl -u tradefly -f
```

---

## 🔒 Security Checklist

- [ ] Port 80 opened in security group
- [ ] Port 443 opened in security group
- [ ] Port 8002 CLOSED to public (only accessible via Nginx)
- [ ] DNS configured for api.tradeflyai.com
- [ ] SSL certificate installed
- [ ] Frontend deployed to Vercel
- [ ] DNS configured for app.tradeflyai.com
- [ ] Test all API endpoints work over HTTPS
- [ ] Test frontend connects to backend

---

## 💰 Cost Estimate

- EC2 t3.medium: $30/month (can downgrade to t3.small for $15/month later)
- Vercel: $0 (free tier)
- Supabase: $0 (free tier)
- Domain: $12/year ($1/month)
- **Total: $31/month** (or $16/month with t3.small)

---

## 📞 Support

If you need help:
1. Check logs: `sudo journalctl -u tradefly -f`
2. Test health check: `curl http://localhost:8002/api/health`
3. Check Nginx: `sudo nginx -t`
4. Check service: `sudo systemctl status tradefly`

---

## 🚀 Current Status

- ✅ Backend deployed with systemd
- ✅ Nginx installed and configured
- ⏳ Waiting for you to open ports 80 and 443
- ⏳ Waiting for DNS configuration
- ⏳ SSL certificate pending (after DNS)
- ⏳ Frontend deployment pending

**Next immediate step:** Open ports 80 and 443 in AWS security group!
