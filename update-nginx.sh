#!/bin/bash
# Update nginx configuration for TradeFly API proxy

echo "Updating nginx configuration..."
sudo cp /var/www/tradefly/nginx-api.conf /etc/nginx/sites-available/default
sudo nginx -t && sudo systemctl reload nginx
echo "✅ Nginx configuration updated and reloaded"
