#!/usr/bin/env python3
"""
Playwright Deployment Test Script
==================================
Tests deployed application with Playwright
Usage: python3 test-deployment.py <url>
Last updated: 2025-12-11
"""

import asyncio
import sys
from playwright.async_api import async_playwright

async def test_deployment(url):
    """Test deployment with comprehensive checks"""

    errors = []
    console_logs = []
    network_requests = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Capture console messages
        page.on("console", lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))

        # Capture page errors
        page.on("pageerror", lambda err: errors.append(f"Page error: {err}"))

        # Capture network responses
        async def handle_response(response):
            network_requests.append({
                "url": response.url,
                "status": response.status,
                "ok": response.ok,
                "method": response.request.method
            })

        page.on("response", handle_response)

        # Test 1: Load main page
        print(f"\n🌐 Loading {url}...")
        try:
            response = await page.goto(url, wait_until="networkidle", timeout=30000)
            print(f"✅ Page loaded (status: {response.status})")
        except Exception as e:
            print(f"❌ Failed to load page: {e}")
            await browser.close()
            return False

        # Wait for page to settle
        await asyncio.sleep(3)

        # Test 2: Check current state
        current_url = page.url
        title = await page.title()
        print(f"📄 Current URL: {current_url}")
        print(f"📄 Page Title: {title}")

        # Test 3: Check for 404s
        failed_requests = [r for r in network_requests if r['status'] == 404]
        if failed_requests:
            print(f"\n❌ Found {len(failed_requests)} 404 errors:")
            for req in failed_requests[:5]:  # Show first 5
                print(f"  - {req['url']}")
        else:
            print("\n✅ No 404 errors found")

        # Test 4: Check console errors
        error_logs = [log for log in console_logs if 'error' in log.lower() or 'failed' in log.lower()]
        if error_logs:
            print(f"\n🔴 Found {len(error_logs)} console errors:")
            for log in error_logs[:5]:  # Show first 5
                print(f"  {log}")
        else:
            print("\n✅ No console errors")

        # Test 5: Check API calls
        api_calls = [r for r in network_requests if '/api/' in r['url']]
        if api_calls:
            print(f"\n📊 API calls detected: {len(api_calls)}")
            for req in api_calls[:5]:  # Show first 5
                status_emoji = "✅" if req['ok'] else "❌"
                print(f"  {status_emoji} [{req['method']}] {req['status']} - {req['url']}")

        # Test 6: Take screenshot
        screenshot_path = "/tmp/deployment-test.png"
        await page.screenshot(path=screenshot_path, full_page=True)
        print(f"\n📸 Screenshot saved to {screenshot_path}")

        await browser.close()

        # Summary
        print("\n" + "="*60)
        print(f"Total network requests: {len(network_requests)}")
        print(f"Failed requests (404): {len(failed_requests)}")
        print(f"Console errors: {len(error_logs)}")
        print(f"Page errors: {len(errors)}")
        print("="*60)

        # Determine success
        success = (
            response.status == 200 and
            len(failed_requests) == 0 and
            len(error_logs) == 0 and
            len(errors) == 0
        )

        if success:
            print("\n✅ All tests passed!")
        else:
            print("\n⚠️  Some tests failed. Review output above.")

        return success

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 test-deployment.py <url>")
        print("Example: python3 test-deployment.py https://www.example.com")
        sys.exit(1)

    url = sys.argv[1]
    success = asyncio.run(test_deployment(url))
    sys.exit(0 if success else 1)
