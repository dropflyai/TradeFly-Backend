#!/usr/bin/bash
# ================================
# Vercel Deployment Checker
# ================================
# Automatically checks Vercel deployment status and logs
# Usage: ./check-vercel-deployment.sh
# Last updated: 2025-12-11

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Load credentials
if [ -f "../../credentials/.env" ]; then
    export $(grep -v '^#' ../../credentials/.env | xargs)
fi

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}VERCEL DEPLOYMENT CHECK${NC}"
echo -e "${BLUE}================================${NC}"

# Check Vercel CLI installed
if ! command -v vercel &> /dev/null; then
    echo -e "${RED}❌ Vercel CLI not installed${NC}"
    echo "Install: npm install -g vercel"
    exit 1
fi

# Get latest deployment
echo -e "\n${BLUE}📦 Fetching latest deployment...${NC}"
DEPLOYMENT_URL=$(npx vercel ls --token="$VERCEL_TOKEN" 2>/dev/null | grep -E "https://" | head -1 | awk '{print $1}')

if [ -z "$DEPLOYMENT_URL" ]; then
    echo -e "${RED}❌ No deployments found${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Latest: $DEPLOYMENT_URL${NC}"

# Check deployment status
echo -e "\n${BLUE}🔍 Checking deployment status...${NC}"
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$DEPLOYMENT_URL")

if [ "$HTTP_STATUS" == "200" ]; then
    echo -e "${GREEN}✅ Deployment is live (HTTP $HTTP_STATUS)${NC}"
else
    echo -e "${RED}❌ Deployment returned HTTP $HTTP_STATUS${NC}"
fi

# Get deployment logs
echo -e "\n${BLUE}📋 Recent deployment logs:${NC}"
npx vercel logs "$DEPLOYMENT_URL" --token="$VERCEL_TOKEN" 2>/dev/null | tail -20

# Check for errors in logs
ERROR_COUNT=$(npx vercel logs "$DEPLOYMENT_URL" --token="$VERCEL_TOKEN" 2>/dev/null | grep -i "error" | wc -l | tr -d ' ')

if [ "$ERROR_COUNT" -gt 0 ]; then
    echo -e "\n${RED}🔴 Found $ERROR_COUNT errors in logs${NC}"
    npx vercel logs "$DEPLOYMENT_URL" --token="$VERCEL_TOKEN" 2>/dev/null | grep -i "error" | tail -5
    exit 1
else
    echo -e "\n${GREEN}✅ No errors in deployment logs${NC}"
fi

echo -e "\n${BLUE}================================${NC}"
