#!/usr/bin/env python3
"""
Frontend Error Checker - Automatically detect console errors
==============================================================
Loads the frontend and captures ALL console errors, warnings, and network failures
Usage: python3 check-frontend-errors.py <url>
Last updated: 2025-12-11
"""

import asyncio
import sys
import json
from playwright.async_api import async_playwright

async def check_frontend_errors(url):
    """Check frontend for errors without user having to copy/paste"""

    console_messages = []
    page_errors = []
    network_errors = []
    failed_requests = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Capture ALL console messages
        def handle_console(msg):
            console_messages.append({
                "type": msg.type,
                "text": msg.text,
                "location": msg.location
            })

        page.on("console", handle_console)

        # Capture page errors (JavaScript errors)
        def handle_page_error(error):
            page_errors.append(str(error))

        page.on("pageerror", handle_page_error)

        # Capture network failures
        def handle_response(response):
            if not response.ok:
                failed_requests.append({
                    "url": response.url,
                    "status": response.status,
                    "method": response.request.method
                })

        page.on("response", handle_response)

        # Load page
        print(f"\n🌐 Loading {url}...")
        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
            print(f"✅ Page loaded")
        except Exception as e:
            print(f"❌ Failed to load page: {e}")
            await browser.close()
            return False

        # Wait for any async errors
        await asyncio.sleep(5)

        # Take screenshot for reference
        await page.screenshot(path="/tmp/frontend-error-check.png", full_page=True)

        await browser.close()

        # Analyze and display errors
        print("\n" + "="*80)
        print("FRONTEND ERROR REPORT")
        print("="*80)

        # Console errors
        errors = [m for m in console_messages if m['type'] == 'error']
        if errors:
            print(f"\n🔴 CONSOLE ERRORS ({len(errors)}):")
            for i, error in enumerate(errors, 1):
                print(f"\n  [{i}] {error['text']}")
                if error['location']:
                    print(f"      Location: {error['location']}")
        else:
            print("\n✅ No console errors")

        # Console warnings
        warnings = [m for m in console_messages if m['type'] == 'warning']
        if warnings:
            print(f"\n⚠️  CONSOLE WARNINGS ({len(warnings)}):")
            for i, warning in enumerate(warnings[:5], 1):  # Show first 5
                print(f"\n  [{i}] {warning['text']}")
        else:
            print("\n✅ No console warnings")

        # Page errors (uncaught exceptions)
        if page_errors:
            print(f"\n❌ PAGE ERRORS ({len(page_errors)}):")
            for i, error in enumerate(page_errors, 1):
                print(f"\n  [{i}] {error}")
        else:
            print("\n✅ No page errors")

        # Network failures
        if failed_requests:
            print(f"\n📡 FAILED REQUESTS ({len(failed_requests)}):")
            for i, req in enumerate(failed_requests, 1):
                print(f"\n  [{i}] {req['status']} - {req['method']} {req['url']}")
        else:
            print("\n✅ No failed requests")

        # Summary
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        print(f"Total console messages: {len(console_messages)}")
        print(f"Console errors: {len(errors)}")
        print(f"Console warnings: {len(warnings)}")
        print(f"Page errors: {len(page_errors)}")
        print(f"Failed requests: {len(failed_requests)}")
        print(f"\n📸 Screenshot saved to /tmp/frontend-error-check.png")
        print("="*80)

        # Return true if no errors
        has_errors = len(errors) > 0 or len(page_errors) > 0 or len(failed_requests) > 0
        return not has_errors

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 check-frontend-errors.py <url>")
        print("Example: python3 check-frontend-errors.py https://www.tradeflyai.com")
        sys.exit(1)

    url = sys.argv[1]
    success = asyncio.run(check_frontend_errors(url))
    sys.exit(0 if success else 1)
