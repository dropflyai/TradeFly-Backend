# TradeFly Backend - AWS EC2 Deployment Guide

Deploy TradeFly Backend to your EC2 instance running alongside n8n.

## Prerequisites

✅ EC2 instance with Docker installed
✅ Docker Compose installed
✅ Port 8000 available (or modify in `docker-compose.yml`)
✅ OpenAI API key
✅ Supabase credentials

## Quick Deploy (5 minutes)

### 1. SSH into your EC2 instance

```bash
ssh -i your-key.pem ec2-user@your-ec2-ip
```

### 2. Clone the repository

```bash
cd ~
git clone https://github.com/dropflyai/TradeFly-Backend.git
cd TradeFly-Backend
```

### 3. Set up environment variables

```bash
cp .env.example .env
nano .env
```

**Required variables:**
```bash
OPENAI_API_KEY=sk-proj-xxxxx           # Your OpenAI key
SUPABASE_URL=https://xxxxx.supabase.co # Your Supabase project URL
SUPABASE_SERVICE_KEY=xxxxx             # Service role key (not anon key!)
```

**Optional (defaults work fine):**
```bash
USE_YAHOO_FINANCE=true                 # Free market data
TICKERS_TO_WATCH=NVDA,TSLA,AAPL,AMD    # Stocks to monitor
SIGNAL_CHECK_INTERVAL=60               # Scan every 60 seconds
```

### 4. Deploy

```bash
./deploy.sh
```

That's it! 🎉

## Verify Deployment

### Check if running
```bash
docker ps | grep tradefly
```

### View logs
```bash
docker-compose logs -f
```

### Test API
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "supabase": "connected",
  "market_data": "connected",
  "scheduler": "running"
}
```

## Access from Internet

### Option 1: Direct Access (Quick)
Open port 8000 in EC2 Security Group, then access at:
```
http://your-ec2-ip:8000
```

### Option 2: Nginx Reverse Proxy (Recommended)

If you're using nginx for n8n, add this location block:

```nginx
# /etc/nginx/sites-available/default

server {
    listen 80;
    server_name api.tradefly.ai;  # Your domain

    # TradeFly Backend
    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

Reload nginx:
```bash
sudo nginx -t
sudo systemctl reload nginx
```

### Option 3: Use AWS Load Balancer
Add target group pointing to port 8000.

## Updates & Maintenance

### Pull latest changes and redeploy
```bash
cd ~/TradeFly-Backend
git pull origin main
./deploy.sh
```

### Restart service
```bash
docker-compose restart
```

### Stop service
```bash
docker-compose down
```

### View resource usage
```bash
docker stats tradefly-backend
```

## Monitoring

### Check logs
```bash
# Last 100 lines
docker-compose logs --tail=100

# Follow logs in real-time
docker-compose logs -f

# Specific time range
docker-compose logs --since 30m
```

### Test endpoints
```bash
# Health check
curl http://localhost:8000/health

# Active signals
curl http://localhost:8000/signals/active

# Market status
curl http://localhost:8000/market-status

# Backend stats
curl http://localhost:8000/stats
```

## Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose logs

# Rebuild image
docker-compose build --no-cache
docker-compose up -d
```

### Port 8000 already in use
Edit `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Use 8001 instead
```

### Out of memory
Check EC2 instance size. Recommended: t3.small or larger.

```bash
# Check memory usage
free -h

# Check Docker memory
docker stats
```

### Can't connect to Supabase
Verify Security Group allows outbound HTTPS (port 443).

## Security Checklist

- [ ] Use security groups to restrict port 8000 access
- [ ] Keep .env file secure (not committed to git)
- [ ] Use HTTPS in production (setup SSL with Let's Encrypt)
- [ ] Rotate API keys regularly
- [ ] Monitor logs for suspicious activity

## Running Alongside n8n

Both services can run on the same EC2 instance:

```
EC2 Instance
├── n8n (port 5678)
│   └── docker container
└── TradeFly Backend (port 8000)
    └── docker container
```

They share the same Docker network and won't conflict.

## Cost Estimate

**AWS EC2 (t3.small):** ~$15/month
**Data transfer:** ~$1-5/month
**Total:** ~$16-20/month

## Next Steps

1. Deploy backend with `./deploy.sh`
2. Test with `curl http://localhost:8000/health`
3. Configure iOS app to use backend URL
4. Set up GitHub Actions for auto-deployment (optional)
5. Add domain + SSL certificate (recommended)

## Support

- GitHub Issues: https://github.com/dropflyai/TradeFly-Backend/issues
- Logs: `docker-compose logs -f`
