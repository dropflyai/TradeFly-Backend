#!/bin/bash
# ================================
# Full System Health Check
# ================================
# Runs ALL automated checks in sequence
# Usage: ./full-system-check.sh <frontend-url>
# Last updated: 2025-12-11

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
NC='\033[0m'

FRONTEND_URL="${1:-https://www.tradeflyai.com}"

echo -e "${MAGENTA}╔════════════════════════════════════════╗${NC}"
echo -e "${MAGENTA}║     FULL SYSTEM HEALTH CHECK          ║${NC}"
echo -e "${MAGENTA}╚════════════════════════════════════════╝${NC}"
echo -e "\nFrontend URL: ${BLUE}$FRONTEND_URL${NC}\n"

CHECKS_PASSED=0
CHECKS_FAILED=0

# Function to run check and track results
run_check() {
    local name="$1"
    local command="$2"

    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}Running: $name${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    if eval "$command"; then
        echo -e "${GREEN}✅ PASSED: $name${NC}"
        CHECKS_PASSED=$((CHECKS_PASSED + 1))
        return 0
    else
        echo -e "${RED}❌ FAILED: $name${NC}"
        CHECKS_FAILED=$((CHECKS_FAILED + 1))
        return 1
    fi
}

# Check 1: Frontend errors
run_check "Frontend Console Errors" \
    "python3 $(dirname "$0")/check-frontend-errors.py $FRONTEND_URL" || true

# Check 2: Frontend deployment test
run_check "Frontend Deployment Test" \
    "python3 $(dirname "$0")/test-deployment.py $FRONTEND_URL" || true

# Check 3: Backend logs (if they exist)
run_check "Backend Log Errors" \
    "$(dirname "$0")/check-backend-logs.sh" || true

# Check 4: Vercel deployment (if configured)
if [ -n "$VERCEL_TOKEN" ]; then
    run_check "Vercel Deployment Status" \
        "$(dirname "$0")/check-vercel-deployment.sh" || true
else
    echo -e "\n${YELLOW}⚠️  Skipping Vercel check (no VERCEL_TOKEN)${NC}"
fi

# Final Summary
echo -e "\n${MAGENTA}╔════════════════════════════════════════╗${NC}"
echo -e "${MAGENTA}║           FINAL SUMMARY                ║${NC}"
echo -e "${MAGENTA}╚════════════════════════════════════════╝${NC}"
echo -e "\n${GREEN}Checks passed: $CHECKS_PASSED${NC}"
echo -e "${RED}Checks failed: $CHECKS_FAILED${NC}"

TOTAL_CHECKS=$((CHECKS_PASSED + CHECKS_FAILED))
if [ $TOTAL_CHECKS -gt 0 ]; then
    PASS_RATE=$(( (CHECKS_PASSED * 100) / TOTAL_CHECKS ))
    echo -e "Pass rate: ${BLUE}${PASS_RATE}%${NC}\n"
fi

if [ $CHECKS_FAILED -eq 0 ]; then
    echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║   ✅ ALL CHECKS PASSED!                ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════╝${NC}\n"
    exit 0
else
    echo -e "${RED}╔════════════════════════════════════════╗${NC}"
    echo -e "${RED}║   ❌ SOME CHECKS FAILED                ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════╝${NC}\n"
    echo -e "${YELLOW}Review the output above for details${NC}\n"
    exit 1
fi
