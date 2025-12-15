#!/bin/bash
# ================================
# COMPLETE TRIPLE VERIFICATION
# ================================
# Runs ALL THREE verification levels before claiming success
# Usage: ./complete-verification.sh <url>
# Last updated: 2025-12-11
#
# EXIT CODES:
#   0 = All verifications passed
#   1 = One or more verifications failed

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
URL="${1:-https://www.yourapp.com}"
VERIFICATION_PASSED=true
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RESULTS_DIR="/tmp/verification_${TIMESTAMP}"

# Create results directory
mkdir -p "$RESULTS_DIR"

echo -e "${MAGENTA}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${MAGENTA}║         TRIPLE VERIFICATION PROTOCOL                       ║${NC}"
echo -e "${MAGENTA}╚════════════════════════════════════════════════════════════╝${NC}"
echo -e ""
echo -e "${CYAN}Target URL:${NC} $URL"
echo -e "${CYAN}Results Dir:${NC} $RESULTS_DIR"
echo -e "${CYAN}Timestamp:${NC} $TIMESTAMP"
echo -e ""

# ===========================================
# LEVEL 1: AUTOMATED TESTING
# ===========================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🔍 LEVEL 1: AUTOMATED TESTING${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if python3 "$(dirname "$0")/test-deployment.py" "$URL" > "$RESULTS_DIR/level1-output.txt" 2>&1; then
    echo -e "${GREEN}✅ Level 1 PASSED${NC}"
    cat "$RESULTS_DIR/level1-output.txt"
else
    echo -e "${RED}❌ Level 1 FAILED${NC}"
    echo -e "${YELLOW}Output:${NC}"
    cat "$RESULTS_DIR/level1-output.txt"
    VERIFICATION_PASSED=false
fi
echo ""

# ===========================================
# LEVEL 2: VISUAL VERIFICATION
# ===========================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📸 LEVEL 2: VISUAL VERIFICATION${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

python3 << EOF > "$RESULTS_DIR/level2-output.txt" 2>&1
from playwright.sync_api import sync_playwright
import sys

try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Navigate and wait
        print(f"Loading {sys.argv[1]}...")
        response = page.goto("$URL", wait_until="networkidle", timeout=30000)
        print(f"Status: {response.status}")

        # Take screenshots
        page.screenshot(path="$RESULTS_DIR/full-page.png", full_page=True)
        print(f"✅ Full page screenshot: $RESULTS_DIR/full-page.png")

        page.screenshot(path="$RESULTS_DIR/viewport.png")
        print(f"✅ Viewport screenshot: $RESULTS_DIR/viewport.png")

        # Check page title
        title = page.title()
        print(f"Page title: {title}")

        # Check if page loaded
        if response.status == 200:
            print("✅ Page loaded successfully")
            sys.exit(0)
        else:
            print(f"❌ Unexpected status code: {response.status}")
            sys.exit(1)

        browser.close()

except Exception as e:
    print(f"❌ Error during verification: {e}")
    sys.exit(1)
EOF

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Level 2 PASSED${NC}"
    cat "$RESULTS_DIR/level2-output.txt"
else
    echo -e "${RED}❌ Level 2 FAILED${NC}"
    echo -e "${YELLOW}Output:${NC}"
    cat "$RESULTS_DIR/level2-output.txt"
    VERIFICATION_PASSED=false
fi
echo ""

# ===========================================
# LEVEL 3: ERROR SCANNING
# ===========================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🔎 LEVEL 3: ERROR SCANNING${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if python3 "$(dirname "$0")/check-frontend-errors.py" "$URL" > "$RESULTS_DIR/level3-output.txt" 2>&1; then
    echo -e "${GREEN}✅ Level 3 PASSED (No errors detected)${NC}"
    cat "$RESULTS_DIR/level3-output.txt"
else
    echo -e "${RED}❌ Level 3 FAILED (Errors detected)${NC}"
    echo -e "${YELLOW}Output:${NC}"
    cat "$RESULTS_DIR/level3-output.txt"
    VERIFICATION_PASSED=false
fi
echo ""

# ===========================================
# SUMMARY & FINAL VERDICT
# ===========================================
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${MAGENTA}VERIFICATION SUMMARY${NC}"
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "URL Tested: ${CYAN}$URL${NC}"
echo -e "Results Location: ${CYAN}$RESULTS_DIR${NC}"
echo ""
echo -e "Level 1 (Automated Testing): $([ -f "$RESULTS_DIR/level1-output.txt" ] && echo -e "${GREEN}✅${NC}" || echo -e "${RED}❌${NC}")"
echo -e "Level 2 (Visual Verification): $([ -f "$RESULTS_DIR/level2-output.txt" ] && echo -e "${GREEN}✅${NC}" || echo -e "${RED}❌${NC}")"
echo -e "Level 3 (Error Scanning): $([ -f "$RESULTS_DIR/level3-output.txt" ] && echo -e "${GREEN}✅${NC}" || echo -e "${RED}❌${NC}")"
echo ""

# List all artifacts
echo -e "${CYAN}Artifacts Created:${NC}"
ls -lh "$RESULTS_DIR" | tail -n +2 | while read -r line; do
    echo -e "  $line"
done
echo ""

# Final verdict
echo -e "${MAGENTA}╔════════════════════════════════════════════════════════════╗${NC}"
if [ "$VERIFICATION_PASSED" = true ]; then
    echo -e "${GREEN}║  ✅ ALL VERIFICATIONS PASSED                               ║${NC}"
    echo -e "${MAGENTA}╚════════════════════════════════════════════════════════════╝${NC}"
    echo -e ""
    echo -e "${GREEN}🎉 IT IS NOW SAFE TO CLAIM SUCCESS${NC}"
    echo -e ""
    echo -e "${CYAN}Evidence:${NC}"
    echo -e "  - Level 1 Test Output: $RESULTS_DIR/level1-output.txt"
    echo -e "  - Level 2 Screenshots: $RESULTS_DIR/full-page.png"
    echo -e "  - Level 3 Error Scan: $RESULTS_DIR/level3-output.txt"
    echo -e ""
    exit 0
else
    echo -e "${RED}║  ❌ VERIFICATION FAILED                                    ║${NC}"
    echo -e "${MAGENTA}╚════════════════════════════════════════════════════════════╝${NC}"
    echo -e ""
    echo -e "${RED}⚠️  DO NOT CLAIM SUCCESS${NC}"
    echo -e "${RED}⚠️  FIX THE ERRORS IDENTIFIED ABOVE${NC}"
    echo -e "${RED}⚠️  THEN RE-RUN THIS SCRIPT${NC}"
    echo -e ""
    echo -e "${YELLOW}Review detailed output in:${NC}"
    echo -e "  $RESULTS_DIR/"
    echo -e ""
    exit 1
fi
