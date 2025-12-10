#!/bin/bash
# TradeFly Production Setup Script
# Run this on EC2: bash setup-production.sh

set -e  # Exit on any error

echo "🚀 TradeFly Production Setup for api.tradeflyai.com"
echo "=================================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Stop any existing nohup processes
echo -e "${YELLOW}📛 Stopping existing backend processes...${NC}"
pkill -f "python3 main_options.py" || echo "No existing processes found"
sleep 2

# 2. Install Nginx and Certbot
echo -e "${YELLOW}📦 Installing Nginx and Certbot...${NC}"
sudo apt update
sudo apt install -y nginx certbot python3-certbot-nginx

# 3. Create systemd service
echo -e "${YELLOW}⚙️  Creating systemd service...${NC}"
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

# 4. Enable and start service
echo -e "${YELLOW}🔄 Starting TradeFly service...${NC}"
sudo systemctl daemon-reload
sudo systemctl enable tradefly
sudo systemctl start tradefly

# Wait for service to start
sleep 3

# Check if service is running
if sudo systemctl is-active --quiet tradefly; then
    echo -e "${GREEN}✅ Service started successfully!${NC}"
else
    echo -e "${RED}❌ Service failed to start. Check logs:${NC}"
    echo "sudo journalctl -u tradefly -n 50"
    exit 1
fi

# 5. Test local endpoint
echo -e "${YELLOW}🧪 Testing local endpoint...${NC}"
if curl -s http://localhost:8002/api/health | grep -q "operational"; then
    echo -e "${GREEN}✅ Backend responding correctly${NC}"
else
    echo -e "${RED}❌ Backend not responding. Check logs:${NC}"
    echo "sudo journalctl -u tradefly -n 50"
    exit 1
fi

# 6. Create Nginx configuration
echo -e "${YELLOW}🌐 Configuring Nginx...${NC}"
sudo tee /etc/nginx/sites-available/tradefly > /dev/null << 'EOF'
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
sudo ln -sf /etc/nginx/sites-available/tradefly /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx config
echo -e "${YELLOW}🧪 Testing Nginx configuration...${NC}"
if sudo nginx -t; then
    echo -e "${GREEN}✅ Nginx config valid${NC}"
    sudo systemctl restart nginx
else
    echo -e "${RED}❌ Nginx config invalid${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. Configure DNS (in your domain registrar):"
echo "   Type: A Record"
echo "   Name: api"
echo "   Value: $(curl -s ifconfig.me)"
echo "   TTL: 300"
echo ""
echo "2. Wait for DNS to propagate (5-10 minutes)"
echo "   Test with: nslookup api.tradeflyai.com"
echo ""
echo "3. Once DNS is working, install SSL certificate:"
echo "   sudo certbot --nginx -d api.tradeflyai.com"
echo ""
echo "📊 Service Management Commands:"
echo "   Status:  sudo systemctl status tradefly"
echo "   Logs:    sudo journalctl -u tradefly -f"
echo "   Restart: sudo systemctl restart tradefly"
echo "   Stop:    sudo systemctl stop tradefly"
echo ""
echo "🔍 Test Your API:"
echo "   Local:  curl http://localhost:8002/api/health"
echo "   Public: curl http://$(curl -s ifconfig.me)/api/health"
echo "   Domain: curl http://api.tradeflyai.com/api/health (after DNS)"
echo ""
