#!/bin/bash
# TradeFly EC2 Quick Deploy Script
# Run this ON YOUR EC2 INSTANCE after SSH'ing in

set -e  # Exit on error

echo "🚀 TradeFly Backend Deployment Script"
echo "======================================"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
   echo -e "${RED}❌ Don't run as root. Run as ubuntu user.${NC}"
   exit 1
fi

# Install system dependencies
echo -e "${YELLOW}📦 Installing system dependencies...${NC}"
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3-pip git nginx certbot python3-certbot-nginx

# Create app directory
echo -e "${YELLOW}📁 Setting up application directory...${NC}"
sudo mkdir -p /var/www/tradefly
sudo chown $USER:$USER /var/www/tradefly
cd /var/www/tradefly

# Clone or pull latest code
if [ -d ".git" ]; then
    echo -e "${YELLOW}🔄 Pulling latest code...${NC}"
    git pull
else
    echo -e "${YELLOW}📥 Cloning repository...${NC}"
    echo -e "${RED}⚠️  Replace with your actual repo URL!${NC}"
    # git clone https://github.com/YOUR_USERNAME/TradeFly-Backend.git .
    echo "Skipping git clone - add your code manually"
fi

# Create Python virtual environment
echo -e "${YELLOW}🐍 Setting up Python environment...${NC}"
if [ ! -d "venv" ]; then
    python3.11 -m venv venv
fi

source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚙️  Creating .env file...${NC}"
    cat > .env << 'ENVEOF'
# Polygon/Massive API
POLYGON_API_KEY=REPLACE_WITH_YOUR_KEY

# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_KEY=REPLACE_WITH_YOUR_KEY

# App Config
ACCOUNT_BALANCE=10000
PORT=8002
ENVEOF
    chmod 600 .env
    echo -e "${RED}⚠️  Don't forget to edit .env with your actual keys!${NC}"
fi

# Create systemd service
echo -e "${YELLOW}⚙️  Creating systemd service...${NC}"
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

# Reload and start service
echo -e "${YELLOW}🔄 Starting service...${NC}"
sudo systemctl daemon-reload
sudo systemctl enable tradefly
sudo systemctl restart tradefly

# Check service status
sleep 2
if sudo systemctl is-active --quiet tradefly; then
    echo -e "${GREEN}✅ Service is running!${NC}"
else
    echo -e "${RED}❌ Service failed to start. Check logs:${NC}"
    echo "sudo journalctl -u tradefly -n 50"
    exit 1
fi

# Configure Nginx
echo -e "${YELLOW}🌐 Configuring Nginx...${NC}"
sudo cat > /etc/nginx/sites-available/tradefly << 'NGINX_EOF'
server {
    listen 80;
    server_name _;  # Accept all domains for now

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

sudo ln -sf /etc/nginx/sites-available/tradefly /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl restart nginx

echo ""
echo -e "${GREEN}✅ Deployment complete!${NC}"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file: nano /var/www/tradefly/.env"
echo "2. Restart service: sudo systemctl restart tradefly"
echo "3. Check logs: sudo journalctl -u tradefly -f"
echo "4. Test API: curl http://localhost:8002/api/health"
echo ""
echo "🌐 Your API is now available at: http://$(curl -s ifconfig.me):80"
echo ""
echo "For SSL setup, run: sudo certbot --nginx -d your-domain.com"
