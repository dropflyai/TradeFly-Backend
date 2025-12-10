#!/bin/bash
# TradeFly Backend Startup Script
# Run this on EC2: bash start-tradefly.sh

cd /var/www/tradefly || exit 1

# Create venv if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3.11 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

export POLYGON_API_KEY=3LJuAPplRFEeAlnMDHkmFVK93hcxEftF
export SUPABASE_URL=https://nplgxhthjwwyywbnvxzt.supabase.co
export SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5wbGd4aHRoand3eXl3Ym52eHp0Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDE5MjE3MSwiZXhwIjoyMDc5NzY4MTcxfQ.qGhvTBRJ1Q49JvCOQ5Gb5IciFhsNFzEiEYQQ5wDZj9I
export PORT=8002
export ACCOUNT_BALANCE=10000

echo "Starting TradeFly backend..."
nohup python3 main_options.py > app.log 2>&1 &

sleep 3
echo "Backend started! Check status:"
curl -s http://localhost:8002/api/health || echo "Not responding yet, check app.log for errors"
