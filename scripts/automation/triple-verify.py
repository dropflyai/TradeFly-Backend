#!/usr/bin/env python3
"""
TRIPLE VERIFICATION - Single Script Version
============================================
Auto-detects ALL errors without user copy/paste
Usage: python3 triple-verify.py <url>
Last updated: 2025-12-11
"""

import asyncio
import sys
import json
from datetime import datetime
from playwright.async_api import async_playwright


async def triple_verify(url):
    """
    Comprehensive verification that finds ALL errors automatically.
    User should NEVER need to copy/paste error messages.
    """

    # Storage for all findings
    findings = {
        "url": url,
        "timestamp": datetime.now().isoformat(),
        "console_logs": [],
        "page_errors": [],
        "network_failures": [],
        "warnings": [],
        "level1_passed": False,
        "level2_passed": False,
        "level3_passed": False
    }

    print("\n" + "="*70)
    print("TRIPLE VERIFICATION PROTOCOL")
    print("="*70)
    print(f"\nTarget: {url}")
    print(f"Started: {findings['timestamp']}\n")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()

        # ==========================================
        # EVENT LISTENERS - Capture Everything
        # ==========================================

        def handle_console(msg):
            """Capture all console messages"""
            findings["console_logs"].append({
                "type": msg.type,
                "text": msg.text,
                "location": str(msg.location) if msg.location else "unknown"
            })

        def handle_page_error(error):
            """Capture JavaScript errors"""
            findings["page_errors"].append({
                "error": str(error),
                "type": "page_error"
            })

        async def handle_response(response):
            """Capture network failures"""
            if not response.ok:
                findings["network_failures"].append({
                    "url": response.url,
                    "status": response.status,
                    "method": response.request.method,
                    "statusText": response.status_text
                })

        def handle_request_failed(request):
            """Capture completely failed requests"""
            findings["network_failures"].append({
                "url": request.url,
                "status": "FAILED",
                "method": request.method,
                "failure": request.failure
            })

        # Attach listeners
        page.on("console", handle_console)
        page.on("pageerror", handle_page_error)
        page.on("response", handle_response)
        page.on("requestfailed", handle_request_failed)

        # ==========================================
        # LEVEL 1: AUTOMATED TESTING
        # ==========================================
        print("─"*70)
        print("🔍 LEVEL 1: AUTOMATED TESTING")
        print("─"*70)

        try:
            print(f"Loading {url}...")
            response = await page.goto(url, wait_until="networkidle", timeout=30000)

            # Wait for page to settle
            await asyncio.sleep(3)

            status = response.status
            print(f"  Status Code: {status}")

            if status == 200:
                print("  ✅ Page loaded successfully")
                findings["level1_passed"] = True
            else:
                print(f"  ❌ Unexpected status: {status}")
                findings["level1_passed"] = False

        except Exception as e:
            print(f"  ❌ Failed to load page: {e}")
            findings["page_errors"].append({
                "error": str(e),
                "type": "navigation_error"
            })
            findings["level1_passed"] = False

        # ==========================================
        # LEVEL 2: VISUAL VERIFICATION
        # ==========================================
        print("\n" + "─"*70)
        print("📸 LEVEL 2: VISUAL VERIFICATION")
        print("─"*70)

        try:
            # Take screenshots
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_full = f"/tmp/verify-full-{timestamp_str}.png"
            screenshot_viewport = f"/tmp/verify-viewport-{timestamp_str}.png"

            await page.screenshot(path=screenshot_full, full_page=True)
            print(f"  ✅ Full page screenshot: {screenshot_full}")

            await page.screenshot(path=screenshot_viewport)
            print(f"  ✅ Viewport screenshot: {screenshot_viewport}")

            # Get page info
            title = await page.title()
            current_url = page.url
            print(f"  Page Title: {title}")
            print(f"  Current URL: {current_url}")

            findings["level2_passed"] = True

        except Exception as e:
            print(f"  ❌ Visual verification failed: {e}")
            findings["level2_passed"] = False

        # ==========================================
        # LEVEL 3: ERROR SCANNING
        # ==========================================
        print("\n" + "─"*70)
        print("🔎 LEVEL 3: ERROR SCANNING")
        print("─"*70)

        # Analyze console logs
        console_errors = [
            log for log in findings["console_logs"]
            if log["type"] in ["error"]
        ]
        console_warnings = [
            log for log in findings["console_logs"]
            if log["type"] in ["warning"]
        ]

        print(f"\n  Console Messages: {len(findings['console_logs'])} total")
        print(f"    - Errors: {len(console_errors)}")
        print(f"    - Warnings: {len(console_warnings)}")
        print(f"    - Other: {len(findings['console_logs']) - len(console_errors) - len(console_warnings)}")

        # Show console errors
        if console_errors:
            print(f"\n  ❌ CONSOLE ERRORS DETECTED ({len(console_errors)}):")
            for i, err in enumerate(console_errors[:5], 1):
                print(f"    {i}. [{err['type'].upper()}] {err['text']}")
                if err['location'] != 'unknown':
                    print(f"       Location: {err['location']}")
            if len(console_errors) > 5:
                print(f"    ... and {len(console_errors) - 5} more")

        # Show warnings
        if console_warnings:
            print(f"\n  ⚠️  CONSOLE WARNINGS ({len(console_warnings)}):")
            for i, warn in enumerate(console_warnings[:3], 1):
                print(f"    {i}. {warn['text']}")
            if len(console_warnings) > 3:
                print(f"    ... and {len(console_warnings) - 3} more")

        # Show network failures
        if findings["network_failures"]:
            print(f"\n  ❌ NETWORK FAILURES DETECTED ({len(findings['network_failures'])}):")
            for i, fail in enumerate(findings["network_failures"][:10], 1):
                status = fail.get('status', 'UNKNOWN')
                method = fail.get('method', 'GET')
                url_short = fail['url'][:80] + "..." if len(fail['url']) > 80 else fail['url']
                print(f"    {i}. [{method}] {status} - {url_short}")
            if len(findings["network_failures"]) > 10:
                print(f"    ... and {len(findings['network_failures']) - 10} more")

        # Show page errors
        if findings["page_errors"]:
            print(f"\n  ❌ PAGE ERRORS DETECTED ({len(findings['page_errors'])}):")
            for i, err in enumerate(findings["page_errors"][:5], 1):
                print(f"    {i}. {err['error']}")
            if len(findings["page_errors"]) > 5:
                print(f"    ... and {len(findings['page_errors']) - 5} more")

        # Determine Level 3 status
        has_critical_errors = (
            len(console_errors) > 0 or
            len(findings["page_errors"]) > 0 or
            len(findings["network_failures"]) > 0
        )

        if not has_critical_errors:
            print("\n  ✅ No critical errors detected")
            findings["level3_passed"] = True
        else:
            print("\n  ❌ Critical errors detected")
            findings["level3_passed"] = False

        await browser.close()

    # ==========================================
    # FINAL VERDICT
    # ==========================================
    print("\n" + "="*70)
    print("FINAL VERDICT")
    print("="*70)

    all_passed = (
        findings["level1_passed"] and
        findings["level2_passed"] and
        findings["level3_passed"]
    )

    print(f"\nLevel 1 (Automated Testing): {'✅ PASSED' if findings['level1_passed'] else '❌ FAILED'}")
    print(f"Level 2 (Visual Verification): {'✅ PASSED' if findings['level2_passed'] else '❌ FAILED'}")
    print(f"Level 3 (Error Scanning): {'✅ PASSED' if findings['level3_passed'] else '❌ FAILED'}")

    print("\n" + "="*70)
    if all_passed:
        print("✅ ALL VERIFICATIONS PASSED")
        print("="*70)
        print("\n🎉 IT IS NOW SAFE TO CLAIM SUCCESS\n")
        return 0
    else:
        print("❌ VERIFICATION FAILED")
        print("="*70)
        print("\n⚠️  DO NOT CLAIM SUCCESS")
        print("⚠️  FIX THE ERRORS IDENTIFIED ABOVE")
        print("⚠️  THEN RE-RUN THIS SCRIPT\n")
        return 1


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 triple-verify.py <url>")
        print("Example: python3 triple-verify.py https://www.example.com")
        sys.exit(1)

    url = sys.argv[1]
    exit_code = asyncio.run(triple_verify(url))
    sys.exit(exit_code)
