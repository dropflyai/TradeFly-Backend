#!/bin/bash
# ================================
# Backend Log Checker
# ================================
# Automatically checks backend logs for errors
# Usage: ./check-backend-logs.sh [log-file-path]
# Last updated: 2025-12-11

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Default log locations to check
DEFAULT_LOGS=(
    "*.log"
    "logs/*.log"
    "../*.log"
    "../../*.log"
)

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}BACKEND LOG ERROR CHECKER${NC}"
echo -e "${BLUE}================================${NC}"

# If log file specified, use it
if [ -n "$1" ]; then
    LOG_FILES=("$1")
else
    # Find log files in common locations
    LOG_FILES=()
    for pattern in "${DEFAULT_LOGS[@]}"; do
        for file in $pattern; do
            if [ -f "$file" ]; then
                LOG_FILES+=("$file")
            fi
        done
    done
fi

if [ ${#LOG_FILES[@]} -eq 0 ]; then
    echo -e "${YELLOW}⚠️  No log files found${NC}"
    echo "Checked:"
    for pattern in "${DEFAULT_LOGS[@]}"; do
        echo "  - $pattern"
    done
    echo ""
    echo "Usage: ./check-backend-logs.sh path/to/logfile.log"
    exit 1
fi

echo -e "\n${GREEN}Found ${#LOG_FILES[@]} log file(s)${NC}\n"

TOTAL_ERRORS=0
TOTAL_WARNINGS=0

for LOG_FILE in "${LOG_FILES[@]}"; do
    echo -e "${BLUE}─────────────────────────────────${NC}"
    echo -e "${BLUE}File: $LOG_FILE${NC}"
    echo -e "${BLUE}─────────────────────────────────${NC}"

    if [ ! -f "$LOG_FILE" ]; then
        echo -e "${RED}❌ File not found${NC}\n"
        continue
    fi

    # Count errors
    ERROR_COUNT=$(grep -i "error" "$LOG_FILE" 2>/dev/null | wc -l | tr -d ' ')
    WARNING_COUNT=$(grep -i "warn" "$LOG_FILE" 2>/dev/null | wc -l | tr -d ' ')

    TOTAL_ERRORS=$((TOTAL_ERRORS + ERROR_COUNT))
    TOTAL_WARNINGS=$((TOTAL_WARNINGS + WARNING_COUNT))

    # Show errors
    if [ "$ERROR_COUNT" -gt 0 ]; then
        echo -e "\n${RED}🔴 ERRORS (${ERROR_COUNT}):${NC}"
        grep -i "error" "$LOG_FILE" | tail -10 | while IFS= read -r line; do
            echo -e "  ${RED}>${NC} $line"
        done
        if [ "$ERROR_COUNT" -gt 10 ]; then
            echo -e "  ${YELLOW}... and $((ERROR_COUNT - 10)) more${NC}"
        fi
    else
        echo -e "\n${GREEN}✅ No errors${NC}"
    fi

    # Show warnings
    if [ "$WARNING_COUNT" -gt 0 ]; then
        echo -e "\n${YELLOW}⚠️  WARNINGS (${WARNING_COUNT}):${NC}"
        grep -i "warn" "$LOG_FILE" | tail -5 | while IFS= read -r line; do
            echo -e "  ${YELLOW}>${NC} $line"
        done
        if [ "$WARNING_COUNT" -gt 5 ]; then
            echo -e "  ${YELLOW}... and $((WARNING_COUNT - 5)) more${NC}"
        fi
    else
        echo -e "\n${GREEN}✅ No warnings${NC}"
    fi

    # Show last 5 lines
    echo -e "\n${BLUE}📄 Last 5 lines:${NC}"
    tail -5 "$LOG_FILE" | while IFS= read -r line; do
        echo -e "  $line"
    done

    echo ""
done

# Summary
echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}SUMMARY${NC}"
echo -e "${BLUE}================================${NC}"
echo -e "Files checked: ${#LOG_FILES[@]}"
echo -e "Total errors: ${RED}$TOTAL_ERRORS${NC}"
echo -e "Total warnings: ${YELLOW}$TOTAL_WARNINGS${NC}"
echo -e "${BLUE}================================${NC}"

# Exit with error if errors found
if [ "$TOTAL_ERRORS" -gt 0 ]; then
    exit 1
else
    exit 0
fi
