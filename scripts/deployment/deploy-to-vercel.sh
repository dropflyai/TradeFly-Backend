#!/bin/bash
# ================================
# Deploy to Vercel Script
# ================================
# Usage: ./deploy-to-vercel.sh [--prod]
# Last updated: 2025-12-11

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Load environment variables
if [ -f "../../credentials/.env" ]; then
    echo -e "${GREEN}Loading credentials...${NC}"
    export $(grep -v '^#' ../../credentials/.env | xargs)
else
    echo -e "${RED}Error: credentials/.env not found${NC}"
    exit 1
fi

# Check required environment variables
if [ -z "$VERCEL_TOKEN" ]; then
    echo -e "${RED}Error: VERCEL_TOKEN not set${NC}"
    exit 1
fi

# Check if production deployment
PROD_FLAG=""
if [ "$1" == "--prod" ]; then
    PROD_FLAG="--prod"
    echo -e "${YELLOW}Deploying to PRODUCTION${NC}"
else
    echo -e "${YELLOW}Deploying to PREVIEW${NC}"
fi

echo -e "${YELLOW}==================================${NC}"
echo -e "${YELLOW}Deploying to Vercel${NC}"
echo -e "${YELLOW}==================================${NC}"
echo ""

# Run deployment
echo -e "${GREEN}Starting deployment...${NC}"
VERCEL_TOKEN="$VERCEL_TOKEN" npx vercel $PROD_FLAG --yes

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}==================================${NC}"
    echo -e "${GREEN}Deployment completed successfully!${NC}"
    echo -e "${GREEN}==================================${NC}"
else
    echo ""
    echo -e "${RED}==================================${NC}"
    echo -e "${RED}Deployment failed!${NC}"
    echo -e "${RED}==================================${NC}"
    exit 1
fi
