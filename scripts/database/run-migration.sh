#!/bin/bash
# ================================
# Run Supabase Migration Script
# ================================
# Usage: ./run-migration.sh path/to/migration.sql
# Last updated: 2025-12-11

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Load environment variables
if [ -f "../../credentials/.env" ]; then
    echo -e "${GREEN}Loading credentials...${NC}"
    export $(grep -v '^#' ../../credentials/.env | xargs)
else
    echo -e "${RED}Error: credentials/.env not found${NC}"
    exit 1
fi

# Check migration file provided
if [ -z "$1" ]; then
    echo -e "${RED}Error: No migration file specified${NC}"
    echo "Usage: ./run-migration.sh path/to/migration.sql"
    exit 1
fi

MIGRATION_FILE="$1"

# Check migration file exists
if [ ! -f "$MIGRATION_FILE" ]; then
    echo -e "${RED}Error: Migration file not found: $MIGRATION_FILE${NC}"
    exit 1
fi

# Check required environment variables
if [ -z "$SUPABASE_DB_PASSWORD" ] || [ -z "$SUPABASE_HOST" ]; then
    echo -e "${RED}Error: Required environment variables not set${NC}"
    echo "Required: SUPABASE_DB_PASSWORD, SUPABASE_HOST"
    exit 1
fi

echo -e "${YELLOW}==================================${NC}"
echo -e "${YELLOW}Running Supabase Migration${NC}"
echo -e "${YELLOW}==================================${NC}"
echo "File: $MIGRATION_FILE"
echo "Host: $SUPABASE_HOST"
echo ""

# Run migration
echo -e "${GREEN}Executing migration...${NC}"
PGPASSWORD="$SUPABASE_DB_PASSWORD" psql \
    -h "$SUPABASE_HOST" \
    -U "${SUPABASE_USER:-postgres}" \
    -d "${SUPABASE_DB:-postgres}" \
    -f "$MIGRATION_FILE"

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}==================================${NC}"
    echo -e "${GREEN}Migration completed successfully!${NC}"
    echo -e "${GREEN}==================================${NC}"
else
    echo ""
    echo -e "${RED}==================================${NC}"
    echo -e "${RED}Migration failed!${NC}"
    echo -e "${RED}==================================${NC}"
    exit 1
fi
