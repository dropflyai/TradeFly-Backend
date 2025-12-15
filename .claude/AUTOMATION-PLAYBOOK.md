# AUTOMATION PLAYBOOK

**Purpose:** Comprehensive reference for ALL automation solutions. Read this BEFORE claiming "I can't automate X."

**Last Updated:** 2025-12-13

---

## Table of Contents
1. [Supabase Database Operations](#supabase-database-operations)
2. [Vercel Deployments](#vercel-deployments)
3. [AWS EC2 Management](#aws-ec2-management)
4. [GitHub Operations](#github-operations)
5. [iOS App Store Automation](#ios-app-store-automation)
6. [Testing & Verification](#testing--verification)
7. [Error Monitoring & Log Checking](#error-monitoring--log-checking)
8. [Triple Verification System](#triple-verification-system)
9. [Massive.com Portfolio Updates](#massivecom-portfolio-updates)
10. [Financial Data APIs](#financial-data-apis)
11. [Docker Operations](#docker-operations)
12. [Project Migration](#project-migration)
13. [n8n Workflow Automation](#n8n-workflow-automation) **← NEW**
14. [MCP (Model Context Protocol)](#mcp-model-context-protocol) **← NEW**
15. [Environment Management](#environment-management)

---

## Supabase Database Operations

### Running Migrations (THE ONE I KEEP FORGETTING)

**NEVER say "I can't run migrations" - YES YOU CAN via multiple methods!**

#### Method 1: Python + Supabase Client (For Complex Migrations)

**Best for:** DDL changes, multiple statements, complex migrations

```python
#!/usr/bin/env python3
from supabase import create_client
import os

# Load from credentials/.env
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

# Read SQL file
with open('migration.sql', 'r') as f:
    SQL = f.read()

print("🔄 Running SQL migration...")

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

try:
    # Execute SQL via RPC (requires exec_sql function in Supabase)
    result = supabase.rpc('exec_sql', {'query': SQL}).execute()
    print("✅ Migration completed!")
except Exception as e:
    # May show misleading error even on success
    if "Query executed successfully" in str(e):
        print("✅ Migration completed (ignore error message)")
    else:
        print(f"❌ Migration failed: {e}")
        raise

# Verify migration worked
result = supabase.table('your_table').select('new_column').limit(1).execute()
print(f"✅ Verified: {result.data}")
```

#### Method 2: Direct psql Command (For Simple SQL)

**Best for:** INSERT, UPDATE, SELECT, simple schema changes

```bash
PGPASSWORD='YOUR_DB_PASSWORD' psql \
  -h db.YOUR_PROJECT_ID.supabase.co \
  -U postgres \
  -d postgres \
  -f migration.sql
```

#### Method 3: Using Environment Variables
```bash
# Store credentials in .env first
export SUPABASE_DB_PASSWORD="YOUR_DB_PASSWORD"
export SUPABASE_HOST="db.YOUR_PROJECT_ID.supabase.co"

# Then run migration
PGPASSWORD=$SUPABASE_DB_PASSWORD psql \
  -h $SUPABASE_HOST \
  -U postgres \
  -d postgres \
  -f migration.sql
```

#### Method 3: Using Script (Preferred)
Create `scripts/database/run-migration.sh`:
```bash
#!/bin/bash
set -e

source ../../credentials/.env

if [ -z "$1" ]; then
    echo "Error: No migration file specified"
    echo "Usage: ./run-migration.sh path/to/migration.sql"
    exit 1
fi

MIGRATION_FILE="$1"

echo "Running migration: $MIGRATION_FILE"
PGPASSWORD="$SUPABASE_DB_PASSWORD" psql \
    -h "$SUPABASE_HOST" \
    -U "$SUPABASE_USER" \
    -d "$SUPABASE_DB" \
    -f "$MIGRATION_FILE"

echo "Migration completed successfully"
```

Usage:
```bash
chmod +x scripts/database/run-migration.sh
./scripts/database/run-migration.sh migrations/001_create_users.sql
```

### Schema Verification Before Migration

**ALWAYS verify schema before running INSERT/UPDATE migrations:**

```sql
-- Check what columns exist
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'public'
AND table_name = 'YOUR_TABLE_NAME'
ORDER BY ordinal_position;
```

### Checking Auth Users
```bash
PGPASSWORD=$SUPABASE_DB_PASSWORD psql \
  -h $SUPABASE_HOST \
  -U postgres \
  -d postgres \
  -c "SELECT id, email FROM auth.users;"
```

### Checking User Profiles
```bash
PGPASSWORD=$SUPABASE_DB_PASSWORD psql \
  -h $SUPABASE_HOST \
  -U postgres \
  -d postgres \
  -c "SELECT * FROM public.user_profiles;"
```

---

## Vercel Deployments

### Automated Deployment (Don't Ask User to Deploy Manually)

#### Method 1: Using Vercel Token
```bash
VERCEL_TOKEN="YOUR_TOKEN" npx vercel --prod --yes
```

#### Method 2: Using Vercel CLI (If Logged In)
```bash
npx vercel --prod --yes
```

#### Method 3: Push to GitHub (If Auto-Deploy Configured)
```bash
git add .
git commit -m "Deploy changes"
git push origin main
```

### Vercel Environment Variables
```bash
# List environment variables
npx vercel env ls

# Add environment variable
npx vercel env add SUPABASE_URL production

# Pull environment variables locally
npx vercel env pull .env.local
```

### Vercel Logs
```bash
# View deployment logs
npx vercel logs YOUR_DEPLOYMENT_URL

# Stream logs in real-time
npx vercel logs --follow
```

---

## AWS EC2 Management

### Starting/Stopping Instances
```bash
export AWS_ACCESS_KEY_ID="YOUR_ACCESS_KEY"
export AWS_SECRET_ACCESS_KEY="YOUR_SECRET_KEY"
export AWS_DEFAULT_REGION="us-east-2"

# Start instance
aws ec2 start-instances --instance-ids i-YOUR_INSTANCE_ID

# Stop instance
aws ec2 stop-instances --instance-ids i-YOUR_INSTANCE_ID

# Wait for instance to be running
aws ec2 wait instance-running --instance-ids i-YOUR_INSTANCE_ID
```

### Running Commands on EC2 via SSM
```bash
# Send command
COMMAND_ID=$(aws ssm send-command \
  --instance-ids "i-YOUR_INSTANCE_ID" \
  --document-name "AWS-RunShellScript" \
  --parameters 'commands=["cd /path/to/app && git pull && pm2 restart all"]' \
  --query 'Command.CommandId' \
  --output text)

# Get command output
aws ssm get-command-invocation \
  --command-id "$COMMAND_ID" \
  --instance-id "i-YOUR_INSTANCE_ID" \
  --query 'StandardOutputContent' \
  --output text
```

### Deploying to EC2
Create `scripts/deployment/deploy-to-ec2.sh`:
```bash
#!/bin/bash
set -e

source ../../credentials/.env

INSTANCE_ID="$AWS_EC2_INSTANCE_ID"
APP_PATH="/home/ubuntu/app"

echo "Deploying to EC2 instance: $INSTANCE_ID"

# Send deployment commands
COMMAND_ID=$(aws ssm send-command \
  --instance-ids "$INSTANCE_ID" \
  --document-name "AWS-RunShellScript" \
  --parameters "commands=[
    'cd $APP_PATH',
    'git pull origin main',
    'npm install',
    'npm run build',
    'pm2 restart all'
  ]" \
  --query 'Command.CommandId' \
  --output text)

echo "Command sent: $COMMAND_ID"
echo "Waiting for completion..."

# Wait and get output
sleep 10
aws ssm get-command-invocation \
  --command-id "$COMMAND_ID" \
  --instance-id "$INSTANCE_ID"
```

---

## GitHub Operations

### Creating and Pushing Commits
```bash
git add .
git commit -m "$(cat <<'EOF'
Your commit message here

Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
git push origin main
```

### Creating Pull Requests
```bash
# Create PR using GitHub CLI
gh pr create \
  --title "Your PR Title" \
  --body "$(cat <<'EOF'
## Summary
- Bullet points of changes

## Test Plan
- How to test

Generated with Claude Code
EOF
)"
```

### Checking GitHub Actions Status
```bash
# List recent workflow runs
gh run list --limit 5

# View specific run
gh run view RUN_ID

# Watch run in real-time
gh run watch RUN_ID
```

---

## iOS App Store Automation

### Building and Deploying with Fastlane
```bash
# Navigate to iOS directory
cd ios

# Build and upload to TestFlight
bundle exec fastlane beta

# Or if using system Ruby
/opt/homebrew/opt/ruby/bin/bundle exec fastlane beta
```

### Incrementing Build Number
```bash
cd ios

# Get current version
agvtool what-version

# Increment build number
agvtool next-version -all
```

### Managing Provisioning Profiles
```bash
# List installed profiles
ls ~/Library/MobileDevice/Provisioning\ Profiles/

# Install profile (save with UUID filename)
cp profile.mobileprovision ~/Library/MobileDevice/Provisioning\ Profiles/PROFILE_UUID.mobileprovision
```

---

## Testing & Verification

### Playwright Testing (MUST DO BEFORE CLAIMING SUCCESS)

Create `scripts/automation/test-deployment.py`:
```python
#!/usr/bin/env python3
import asyncio
from playwright.async_api import async_playwright

async def test_deployment(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Navigate to URL
        response = await page.goto(url, wait_until="networkidle")

        # Check status
        print(f"Status: {response.status}")
        print(f"URL: {page.url}")
        print(f"Title: {await page.title()}")

        # Take screenshot
        await page.screenshot(path="/tmp/deployment-test.png")

        await browser.close()

        return response.status == 200

if __name__ == "__main__":
    import sys
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:3000"
    success = asyncio.run(test_deployment(url))
    sys.exit(0 if success else 1)
```

Usage:
```bash
python3 scripts/automation/test-deployment.py https://www.yourapp.com
```

### Health Check Endpoints
```bash
# Check API health
curl -s http://localhost:8000/api/health | python3 -m json.tool

# Check with timeout
timeout 10 curl -s http://localhost:8000/api/health
```

---

## Error Monitoring & Log Checking

**CRITICAL:** Instead of user copy/pasting errors, I can check them DIRECTLY.

### Check Frontend Console Errors (No Copy/Paste Needed!)

**Problem:** User shouldn't have to copy/paste console errors

**Solution:** Use Playwright to automatically capture ALL console errors

```bash
cd scripts/automation
python3 check-frontend-errors.py https://www.tradeflyai.com
```

**What it does:**
- Loads page with Playwright
- Captures ALL console errors, warnings, page errors
- Detects failed network requests (404s, 500s, etc.)
- Takes screenshot for reference
- Shows complete error report without user intervention

**Output Example:**
```
🔴 CONSOLE ERRORS (3):
  [1] Failed to load resource: the server responded with a status of 404
      Location: https://www.tradeflyai.com/api/signals
  [2] Uncaught TypeError: Cannot read property 'map' of undefined
      Location: app.js:42
...
```

**Script Location:** `scripts/automation/check-frontend-errors.py`

---

### Check Backend Logs (No Copy/Paste Needed!)

**Problem:** User shouldn't have to copy/paste backend log errors

**Solution:** Automatically search log files for errors and warnings

```bash
cd scripts/automation
./check-backend-logs.sh

# Or check specific log file
./check-backend-logs.sh /path/to/app.log
```

**What it does:**
- Searches common log locations (*.log, logs/*.log, etc.)
- Counts errors and warnings
- Shows last 10 errors (most recent)
- Shows last 5 warnings
- Displays last 5 log lines for context

**Output Example:**
```
🔴 ERRORS (12):
  > [ERROR] Database connection failed: ECONNREFUSED
  > [ERROR] API endpoint /api/signals returned 500
...

⚠️  WARNINGS (3):
  > [WARN] Deprecated function used in auth.js:45
...
```

**Script Location:** `scripts/automation/check-backend-logs.sh`

---

### Check Vercel Deployment Logs (No Copy/Paste Needed!)

**Problem:** User shouldn't have to navigate to Vercel dashboard

**Solution:** Automatically fetch deployment status and logs via CLI

```bash
cd scripts/automation
./check-vercel-deployment.sh
```

**What it does:**
- Gets latest Vercel deployment URL
- Checks HTTP status (should be 200)
- Fetches recent deployment logs
- Searches logs for errors
- Reports any issues found

**Output Example:**
```
✅ Latest: https://project-abc123.vercel.app
✅ Deployment is live (HTTP 200)

📋 Recent deployment logs:
  [Build] Installing dependencies...
  [Build] Build complete
  [Deploy] Deployment ready

✅ No errors in deployment logs
```

**Script Location:** `scripts/automation/check-vercel-deployment.sh`

---

### Full System Health Check (Run Everything!)

**Problem:** Need to check multiple things manually

**Solution:** One script that runs ALL checks

```bash
cd scripts/automation
./full-system-check.sh https://www.tradeflyai.com
```

**What it does:**
- Runs frontend error check
- Runs deployment test
- Runs backend log check
- Runs Vercel deployment check
- Gives overall pass/fail summary

**Output Example:**
```
╔════════════════════════════════════════╗
║     FULL SYSTEM HEALTH CHECK          ║
╚════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Running: Frontend Console Errors
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ PASSED: Frontend Console Errors

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Running: Backend Log Errors
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ PASSED: Backend Log Errors

╔════════════════════════════════════════╗
║           FINAL SUMMARY                ║
╚════════════════════════════════════════╝

Checks passed: 4
Checks failed: 0
Pass rate: 100%

╔════════════════════════════════════════╗
║   ✅ ALL CHECKS PASSED!                ║
╚════════════════════════════════════════╝
```

**Script Location:** `scripts/automation/full-system-check.sh`

---

## Triple Verification System

**CRITICAL:** Use this BEFORE claiming "it's done" or "it's working"

### Problem
User should NEVER have to copy/paste error messages. You find them FIRST.

### Solution: Triple Verify Script

```bash
# Run complete 3-level verification
python3 scripts/automation/triple-verify.py https://www.yourapp.com

# Or use bash wrapper
./scripts/automation/complete-verification.sh https://www.yourapp.com
```

### What It Does Automatically

**Level 1: Automated Testing**
- Loads page with Playwright
- Captures ALL console messages (errors, warnings, logs)
- Detects JavaScript exceptions
- Records network failures (404s, 500s, etc.)
- Takes full-page screenshot
- Verifies status code = 200

**Level 2: Visual Verification**
- Screenshots entire page
- Screenshots viewport
- Checks page title
- Verifies URL correctness
- Confirms page renders

**Level 3: Error Scanning**
- Scans for console.error
- Scans for console.warn
- Checks unhandled promise rejections
- Verifies no 404s on critical resources
- Exit criteria: ZERO critical errors

### Exit Codes
- `0` = All verifications passed, safe to claim success
- `1` = Errors detected, DO NOT claim success yet

### Workflow

```bash
# 1. Complete implementation
# ... your code changes ...

# 2. Deploy if needed
./scripts/deployment/deploy-to-vercel.sh --prod

# 3. MANDATORY: Run triple verification
python3 scripts/automation/triple-verify.py https://www.yourapp.com

# 4. Check exit code
if [ $? -eq 0 ]; then
    echo "✅ All verifications passed - safe to tell user"
else
    echo "❌ Errors found - FIX THEM and re-verify"
    # DON'T claim success yet!
fi
```

### Example Output (Success)

```
======================================================================
TRIPLE VERIFICATION PROTOCOL
======================================================================

Level 1 (Automated Testing): ✅ PASSED
Level 2 (Visual Verification): ✅ PASSED
Level 3 (Error Scanning): ✅ PASSED

======================================================================
✅ ALL VERIFICATIONS PASSED
======================================================================

🎉 IT IS NOW SAFE TO CLAIM SUCCESS
```

### Example Output (Failure)

```
🔎 LEVEL 3: ERROR SCANNING

  ❌ CONSOLE ERRORS DETECTED (3):
    1. [ERROR] TypeError: Cannot read property 'user' of undefined
       Location: app.js:45:12
    2. [ERROR] Failed to fetch: GET /api/user/profile
    3. [ERROR] Unhandled Promise Rejection: Authentication required

  ❌ NETWORK FAILURES DETECTED (1):
    1. [GET] 404 - /api/user/profile

======================================================================
❌ VERIFICATION FAILED
======================================================================

⚠️  DO NOT CLAIM SUCCESS
⚠️  FIX THE ERRORS IDENTIFIED ABOVE
⚠️  THEN RE-RUN THIS SCRIPT
```

**When this happens:**
1. Read the errors
2. Fix ALL of them
3. Re-run triple-verify.py
4. Loop until exit code = 0
5. ONLY THEN tell user it's done

**See Also:** `.claude/TRIPLE-VERIFICATION-PROTOCOL.md` for complete documentation

---

## Massive.com Portfolio Updates

### Auto-Update Stock Positions in Massive Portfolio

**Problem:** User's Massive.com portfolio needs to stay in sync with actual positions

**Solution:** Automated portfolio sync using Massive API

```python
#!/usr/bin/env python3
import requests
import os

MASSIVE_API_KEY = os.getenv('MASSIVE_API_KEY')
MASSIVE_URL = "https://api.massive.com/v1/portfolios"

# Get current positions from your trading system
positions = [
    {"symbol": "AAPL", "shares": 100, "avg_cost": 150.25},
    {"symbol": "GOOGL", "shares": 50, "avg_cost": 2800.00}
]

# Update Massive portfolio
headers = {"Authorization": f"Bearer {MASSIVE_API_KEY}"}

for position in positions:
    response = requests.post(
        f"{MASSIVE_URL}/positions",
        headers=headers,
        json=position
    )
    print(f"✅ Updated {position['symbol']}: {response.status_code}")
```

**Frequency:** Run after each trade execution

---

## Financial Data APIs

### Polygon.io Stock Data

**Problem:** Need real-time stock prices, historical data, market data

**Solution:** Polygon.io API (you have subscription)

```python
#!/usr/bin/env python3
import requests
import os

POLYGON_API_KEY = os.getenv('POLYGON_API_KEY')  # From credentials/.env

# Get latest price
def get_stock_price(symbol):
    url = f"https://api.polygon.io/v2/last/trade/{symbol}"
    params = {"apiKey": POLYGON_API_KEY}
    response = requests.get(url, params=params)
    data = response.json()
    return data['results']['p']  # price

# Get historical data
def get_historical_data(symbol, from_date, to_date):
    url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/day/{from_date}/{to_date}"
    params = {"apiKey": POLYGON_API_KEY}
    response = requests.get(url, params=params)
    return response.json()['results']

# Get intraday data (1-minute bars)
def get_intraday_data(symbol, date):
    url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/minute/{date}/{date}"
    params = {"apiKey": POLYGON_API_KEY}
    response = requests.get(url, params=params)
    return response.json()['results']

# Usage
price = get_stock_price('AAPL')
print(f"AAPL current price: ${price}")

historical = get_historical_data('AAPL', '2024-01-01', '2024-12-31')
print(f"Retrieved {len(historical)} days of data")
```

**Rate Limits:** 5 requests/second on basic plan

### yfinance (Alternative - Free)

```python
import yfinance as yf

# Get stock data
stock = yf.Ticker("AAPL")

# Current price
price = stock.history(period="1d")['Close'].iloc[-1]

# Intraday data (1-minute)
intraday = stock.history(period="1d", interval="1m")

# Historical data
historical = stock.history(period="1y")
```

---

### IMPORTANT: When to Use These

**Instead of asking user for error messages:**

❌ **WRONG:** "Can you copy the console error and paste it here?"

✅ **RIGHT:**
```bash
# Run error check directly
python3 scripts/automation/check-frontend-errors.py https://www.tradeflyai.com

# See all errors immediately
```

**Instead of asking user to check logs:**

❌ **WRONG:** "Can you check the backend logs for errors?"

✅ **RIGHT:**
```bash
# Check logs directly
./scripts/automation/check-backend-logs.sh

# See all errors immediately
```

**Instead of manual verification:**

❌ **WRONG:** Deploy → Tell user "it's working" → Hope it works

✅ **RIGHT:**
```bash
# Deploy
./scripts/deployment/deploy-to-vercel.sh --prod

# THEN verify
./scripts/automation/full-system-check.sh https://www.tradeflyai.com

# ONLY claim success if checks pass
```

---

## Docker Operations

### Running Commands in Docker Containers

**Problem:** Need to execute commands inside running Docker containers

**Solution:** Use `docker exec`

```bash
# Execute single command
docker exec <container-id> npm run build

# Interactive shell
docker exec -it <container-id> /bin/bash

# As specific user
docker exec -u node <container-id> npm install

# With environment variables
docker exec -e NODE_ENV=production <container-id> npm start
```

### Copy Files To/From Docker Container

```bash
# Copy FROM container TO host
docker cp <container-id>:/path/in/container /path/on/host

# Copy FROM host TO container
docker cp /path/on/host <container-id>:/path/in/container

# Example: Copy built files from container
docker cp my-app:/app/dist ./dist
```

### Docker Container Management

```bash
# List running containers
docker ps

# List all containers (including stopped)
docker ps -a

# Restart container
docker restart <container-id>

# Stop container
docker stop <container-id>

# Start stopped container
docker start <container-id>

# View container logs
docker logs <container-id>

# Follow logs in real-time
docker logs -f <container-id>
```

---

## Project Migration

### Migrating Projects to Template Structure

**Problem:** Need to apply PROJECT-TEMPLATE structure to existing projects

**Solution:** Use automated migration scripts

#### Migrate Single Project

```bash
cd /path/to/PROJECT-TEMPLATE

# Migrate one project
./migrate-project.sh /path/to/your/project
```

**What it does:**
- Adds `.claude/` directory (6 instruction files)
- Sets up `credentials/` directory
- Adds `scripts/` directory (10 automation scripts)
- Creates `docs/` directory
- Updates `.gitignore`
- Migrates existing `.env` files to `credentials/.env`

#### Migrate All Projects

```bash
cd /path/to/PROJECT-TEMPLATE

# Migrate all projects in DropFly-PROJECTS/
./migrate-all-projects.sh
```

**What it does:**
- Prompts for confirmation
- Migrates all 32 projects automatically
- Shows progress for each project
- Creates log files: `/tmp/migration_<project-name>.log`
- Displays final summary

**Safety:**
- NON-DESTRUCTIVE (never deletes files)
- Backs up existing `.claude/` if found
- Preserves custom scripts
- Smart merging (no duplicates)

**After Migration:**
Per project, you need to:
1. Fill in `credentials/.env` with actual values
2. Tell Claude: "Read .claude/SYSTEM-PROMPT.md"
3. Start using 10/10 efficiency system

---

## n8n Workflow Automation

### What is n8n?

**n8n** is a workflow automation platform that lets you connect different services and automate tasks without writing code (or with code when needed). It's self-hosted and has both GUI and API interfaces.

### Running n8n Workflows via API

**Problem:** Need to trigger n8n workflows programmatically

**Solution:** Use n8n's REST API

```python
#!/usr/bin/env python3
import requests
import os

N8N_URL = os.getenv('N8N_URL')  # e.g., https://n8n.yourserver.com
N8N_API_KEY = os.getenv('N8N_API_KEY')

def trigger_workflow(workflow_id, data=None):
    """
    Trigger an n8n workflow via webhook or API

    Args:
        workflow_id: The workflow ID from n8n
        data: Optional data to pass to the workflow
    """
    url = f"{N8N_URL}/webhook/{workflow_id}"
    headers = {
        "Authorization": f"Bearer {N8N_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=data or {}, headers=headers)

    if response.status_code == 200:
        print(f"✅ Workflow triggered: {workflow_id}")
        return response.json()
    else:
        print(f"❌ Failed to trigger workflow: {response.status_code}")
        print(f"   Error: {response.text}")
        return None

# Example: Trigger data sync workflow
result = trigger_workflow(
    workflow_id="stock-data-sync",
    data={
        "symbols": ["AAPL", "GOOGL", "MSFT"],
        "timeframe": "1h"
    }
)
```

### Common n8n Workflow Patterns

#### Pattern 1: Data Sync Workflows
**Use case:** Sync data between Supabase, APIs, and third-party services

```bash
# Trigger via webhook
curl -X POST "https://n8n.yourserver.com/webhook/data-sync" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "polygon",
    "destination": "supabase",
    "table": "stock_prices"
  }'
```

#### Pattern 2: Scheduled Workflows
**Use case:** Run tasks on a schedule (cron jobs)

```python
# Check workflow execution status
def get_workflow_executions(workflow_id, limit=10):
    url = f"{N8N_URL}/api/v1/executions"
    headers = {"Authorization": f"Bearer {N8N_API_KEY}"}
    params = {
        "workflowId": workflow_id,
        "limit": limit
    }

    response = requests.get(url, headers=headers, params=params)
    executions = response.json()

    for execution in executions['data']:
        status = execution['status']
        started = execution['startedAt']
        print(f"{started}: {status}")

    return executions['data']
```

#### Pattern 3: Event-Driven Workflows
**Use case:** React to events (new user signup, trade execution, etc.)

```python
def trigger_user_onboarding(user_id, email):
    """Trigger n8n onboarding workflow when new user signs up"""
    return trigger_workflow(
        workflow_id="user-onboarding",
        data={
            "user_id": user_id,
            "email": email,
            "timestamp": datetime.now().isoformat()
        }
    )

def trigger_trade_notification(trade_data):
    """Notify via Slack/Discord when trade executes"""
    return trigger_workflow(
        workflow_id="trade-notification",
        data=trade_data
    )
```

### Managing n8n Workflows

#### List All Workflows
```python
def list_workflows():
    url = f"{N8N_URL}/api/v1/workflows"
    headers = {"Authorization": f"Bearer {N8N_API_KEY}"}

    response = requests.get(url, headers=headers)
    workflows = response.json()

    for workflow in workflows['data']:
        print(f"ID: {workflow['id']}")
        print(f"Name: {workflow['name']}")
        print(f"Active: {workflow['active']}")
        print("---")

    return workflows['data']
```

#### Activate/Deactivate Workflow
```python
def toggle_workflow(workflow_id, active=True):
    url = f"{N8N_URL}/api/v1/workflows/{workflow_id}"
    headers = {"Authorization": f"Bearer {N8N_API_KEY}"}

    response = requests.patch(
        url,
        headers=headers,
        json={"active": active}
    )

    status = "activated" if active else "deactivated"
    print(f"✅ Workflow {status}")
    return response.json()
```

### n8n + Supabase Integration

**Use case:** Automate database operations via n8n

```python
# Trigger n8n workflow to sync Supabase data
def sync_supabase_data(table_name, operation="sync"):
    return trigger_workflow(
        workflow_id="supabase-sync",
        data={
            "table": table_name,
            "operation": operation,
            "timestamp": datetime.now().isoformat()
        }
    )

# Example: Sync user profiles after bulk update
sync_supabase_data("user_profiles", operation="sync")
```

### n8n + Trading System Integration

**Use case:** Automate trading workflows

```python
def execute_trading_workflow(signal_type, symbols):
    """
    Trigger trading workflow:
    1. Fetch latest market data
    2. Run signal analysis
    3. Execute trades
    4. Update Massive.com portfolio
    5. Send notifications
    """
    return trigger_workflow(
        workflow_id="trading-execution",
        data={
            "signal_type": signal_type,
            "symbols": symbols,
            "timestamp": datetime.now().isoformat()
        }
    )

# Example
execute_trading_workflow(
    signal_type="momentum",
    symbols=["AAPL", "TSLA"]
)
```

### Credentials Setup

Add to `credentials/.env`:
```bash
# n8n Configuration
N8N_URL=https://n8n.yourserver.com
N8N_API_KEY=your_api_key_here
N8N_WEBHOOK_SECRET=your_webhook_secret
```

---

## MCP (Model Context Protocol)

### What is MCP?

**MCP (Model Context Protocol)** is Anthropic's standard for connecting AI assistants (like Claude) to external data sources and tools. It allows Claude to access databases, APIs, file systems, and other resources through standardized "servers."

### Using MCP Servers

**Problem:** Need to give Claude access to external data/tools

**Solution:** Use MCP servers that expose resources via standardized protocol

### Common MCP Server Types

#### 1. File System MCP Server
**Purpose:** Give Claude access to read/write files in specific directories

```bash
# Install MCP file system server
npm install -g @anthropic/mcp-server-filesystem

# Run server
mcp-server-filesystem /path/to/allowed/directory
```

**Claude can then:**
- Read files in that directory
- Write new files
- Search for files
- Get directory listings

#### 2. Database MCP Server
**Purpose:** Give Claude access to query databases

```bash
# Install PostgreSQL MCP server
npm install -g @anthropic/mcp-server-postgres

# Run server with connection string
mcp-server-postgres postgres://user:pass@localhost:5432/dbname
```

**Claude can then:**
- Run SELECT queries
- View schema information
- Execute stored procedures
- Get table metadata

#### 3. API MCP Server
**Purpose:** Give Claude access to REST APIs

```bash
# Install generic API MCP server
npm install -g @anthropic/mcp-server-fetch

# Run server (allows fetching from specified domains)
mcp-server-fetch --allowed-domains="api.example.com,api.polygon.io"
```

**Claude can then:**
- Make HTTP requests to allowed APIs
- Parse JSON responses
- Handle authentication headers

### Creating Custom MCP Servers

**Problem:** Need to expose custom functionality to Claude

**Solution:** Build custom MCP server in Python or Node.js

#### Example: Trading Data MCP Server (Python)

```python
#!/usr/bin/env python3
"""
Custom MCP server for trading data access
Exposes: stock prices, portfolio data, trading signals
"""

from mcp.server import Server
from mcp.types import Resource, Tool
import yfinance as yf
import os

# Initialize MCP server
server = Server("trading-data-server")

@server.resource("stock-price/{symbol}")
async def get_stock_price(symbol: str) -> Resource:
    """Get current stock price"""
    stock = yf.Ticker(symbol)
    price = stock.history(period="1d")['Close'].iloc[-1]

    return Resource(
        uri=f"stock-price/{symbol}",
        name=f"{symbol} Current Price",
        mimeType="application/json",
        text=json.dumps({
            "symbol": symbol,
            "price": float(price),
            "timestamp": datetime.now().isoformat()
        })
    )

@server.tool("get-portfolio")
async def get_portfolio() -> Tool:
    """Get current portfolio holdings"""
    # Load from Supabase or Massive.com
    supabase = create_client(
        os.getenv('SUPABASE_URL'),
        os.getenv('SUPABASE_SERVICE_KEY')
    )

    result = supabase.table('portfolio').select('*').execute()

    return Tool(
        name="get-portfolio",
        description="Current portfolio holdings",
        inputSchema={},
        result=result.data
    )

@server.tool("execute-trade")
async def execute_trade(symbol: str, action: str, quantity: int) -> Tool:
    """Execute a trade (buy/sell)"""
    # Your trading logic here
    trade_result = {
        "symbol": symbol,
        "action": action,
        "quantity": quantity,
        "status": "executed",
        "timestamp": datetime.now().isoformat()
    }

    return Tool(
        name="execute-trade",
        description="Execute trade order",
        inputSchema={
            "symbol": {"type": "string"},
            "action": {"type": "string", "enum": ["buy", "sell"]},
            "quantity": {"type": "integer"}
        },
        result=trade_result
    )

# Run server
if __name__ == "__main__":
    server.run()
```

**Run the server:**
```bash
python3 scripts/mcp/trading-data-server.py
```

**Claude can now:**
- Query stock prices via `stock-price/{symbol}` resource
- Get portfolio via `get-portfolio` tool
- Execute trades via `execute-trade` tool

### MCP + n8n Integration

**Use case:** Let Claude trigger n8n workflows via MCP

```python
@server.tool("trigger-n8n-workflow")
async def trigger_n8n_workflow(workflow_id: str, data: dict) -> Tool:
    """Trigger n8n workflow from Claude"""
    import requests

    response = requests.post(
        f"{os.getenv('N8N_URL')}/webhook/{workflow_id}",
        json=data,
        headers={"Authorization": f"Bearer {os.getenv('N8N_API_KEY')}"}
    )

    return Tool(
        name="trigger-n8n-workflow",
        description="Trigger n8n automation workflow",
        inputSchema={
            "workflow_id": {"type": "string"},
            "data": {"type": "object"}
        },
        result={
            "status": response.status_code,
            "workflow_id": workflow_id,
            "response": response.json() if response.ok else response.text
        }
    )
```

### MCP Server Management

#### Start MCP Server on System Boot

Create `scripts/mcp/start-all-mcp-servers.sh`:
```bash
#!/bin/bash
# Start all MCP servers

# Trading data server
python3 scripts/mcp/trading-data-server.py &
echo $! > /tmp/mcp-trading-server.pid

# Database server
mcp-server-postgres "$SUPABASE_CONNECTION_STRING" &
echo $! > /tmp/mcp-db-server.pid

# File system server
mcp-server-filesystem /Users/rioallen/Documents/DropFly-OS-App-Builder &
echo $! > /tmp/mcp-fs-server.pid

echo "✅ All MCP servers started"
```

#### Stop MCP Servers
```bash
#!/bin/bash
# Stop all MCP servers

for pidfile in /tmp/mcp-*.pid; do
    if [ -f "$pidfile" ]; then
        kill $(cat "$pidfile")
        rm "$pidfile"
    fi
done

echo "✅ All MCP servers stopped"
```

### MCP + Supabase Integration

**Use case:** Give Claude direct Supabase access via MCP

```python
@server.resource("supabase-table/{table_name}")
async def get_table_data(table_name: str) -> Resource:
    """Query Supabase table"""
    from supabase import create_client

    supabase = create_client(
        os.getenv('SUPABASE_URL'),
        os.getenv('SUPABASE_SERVICE_KEY')
    )

    result = supabase.table(table_name).select('*').limit(100).execute()

    return Resource(
        uri=f"supabase-table/{table_name}",
        name=f"Supabase: {table_name}",
        mimeType="application/json",
        text=json.dumps(result.data, indent=2)
    )
```

### Pre-Built MCP Templates (Ready to Use)

**Problem:** Need to quickly set up MCP servers without custom code

**Solution:** Use pre-built MCP templates from the community

#### 1. n8n-mcp (Official n8n MCP Integration)

**Purpose:** Automate CREATING and TESTING n8n workflows directly from Claude

**Primary Use Cases:**
- ✅ **Create new workflows** - Claude can build complete workflows programmatically
- ✅ **Test workflows** - Execute and verify workflow functionality
- ✅ **Debug workflows** - Get execution results and troubleshoot
- ✅ **Update workflows** - Modify existing workflow configurations
- ✅ **Deploy workflows** - Activate/deactivate production workflows

**Installation:**
```bash
npm install -g n8n-mcp
```

**Configuration (.mcp-config.json):**
```json
{
  "mcpServers": {
    "n8n-mcp": {
      "command": "npx",
      "args": ["n8n-mcp"],
      "env": {
        "MCP_MODE": "stdio",
        "LOG_LEVEL": "error",
        "DISABLE_CONSOLE_OUTPUT": "true",
        "N8N_API_URL": "https://your-n8n-instance.com",
        "N8N_API_KEY": "your_n8n_api_key"
      }
    }
  }
}
```

**What Claude can do:**
- **CREATE** new workflows from scratch
- **TEST** workflows with sample data
- **EXECUTE** workflows and get results
- **DEBUG** workflow errors
- **UPDATE** workflow nodes and logic
- **MANAGE** workflow activations

**Example Workflow Automation:**
```python
# Claude can now automate the entire workflow lifecycle:

# 1. CREATE: "Build a new n8n workflow for duplicate lead detection"
#    - Claude creates workflow JSON
#    - Adds webhook trigger
#    - Adds database query nodes
#    - Adds logic nodes for duplicate checking
#    - Saves workflow to n8n

# 2. TEST: "Test the duplicate-prevention workflow with this lead data"
#    - Claude executes workflow with test data
#    - Captures execution results
#    - Verifies expected behavior

# 3. DEBUG: "The workflow failed, show me the error"
#    - Claude retrieves execution logs
#    - Identifies failing node
#    - Suggests fixes

# 4. DEPLOY: "Activate the duplicate-prevention workflow"
#    - Claude activates workflow for production use
```

**Real Workflow Creation Example:**
```javascript
// Claude can create this complete workflow via MCP:
{
  "name": "Stock Data Sync",
  "nodes": [
    {
      "type": "webhook",
      "parameters": {
        "path": "stock-sync",
        "method": "POST"
      }
    },
    {
      "type": "polygon-api",
      "parameters": {
        "symbol": "={{$json.symbol}}",
        "apiKey": "={{$env.POLYGON_API_KEY}}"
      }
    },
    {
      "type": "supabase",
      "parameters": {
        "operation": "insert",
        "table": "stock_prices"
      }
    }
  ],
  "connections": {...}
}
```

#### 2. Context7 (Upstash Documentation MCP)

**Purpose:** Provide CONTEXT on HOW and WHY we build workflows the way we do

**Primary Use Cases:**
- ✅ **Best Practices** - Understand why we use specific patterns
- ✅ **Architecture Decisions** - Context on technical choices
- ✅ **Implementation Guidance** - How to properly implement features
- ✅ **Troubleshooting Context** - Why certain errors happen and how to fix them
- ✅ **Design Patterns** - Industry-standard approaches to common problems

**Installation:**
```bash
npm install -g mcp-remote
```

**Configuration (.mcp-config.json):**
```json
{
  "mcpServers": {
    "context7-docs": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "https://gitmcp.io/upstash/context7"
      ]
    }
  }
}
```

**What Claude uses Context7 for:**
- **WHY** we use certain n8n node types over others
- **HOW** to properly structure workflows for maintainability
- **WHEN** to use webhooks vs scheduled triggers
- **WHICH** authentication patterns are secure
- **WHY** specific error handling approaches are needed

**Example Context Queries:**
```python
# Before building a workflow, Claude queries Context7:

# QUESTION: "Why should I use error handling nodes in n8n workflows?"
# CONTEXT7: Returns best practices documentation explaining:
#   - Workflows fail silently without error handling
#   - Error nodes enable retry logic
#   - Proper logging requires error catching
#   - Production workflows need graceful degradation

# QUESTION: "How should I structure a duplicate detection workflow?"
# CONTEXT7: Returns architectural guidance:
#   - Multi-algorithm approach is more accurate
#   - Use fuzzy matching for phone/email normalization
#   - Risk scoring better than binary yes/no
#   - Fingerprinting prevents sophisticated duplicates

# QUESTION: "What's the proper way to handle Supabase authentication in n8n?"
# CONTEXT7: Returns implementation guidance:
#   - Use service_role key for backend operations
#   - Never expose service_role in client-side code
#   - anon key for client operations only
#   - RLS policies required for security
```

**Real Workflow Design Process:**
```javascript
// 1. User: "Build a workflow to sync stock data to Supabase"

// 2. Claude queries Context7:
//    Q: "What are n8n best practices for API rate limiting?"
//    A: Use batch processing, implement retry logic, add delays

// 3. Claude queries Context7:
//    Q: "How should database inserts handle duplicates in Supabase?"
//    A: Use upsert (ON CONFLICT), set proper unique constraints

// 4. Claude CREATES workflow using n8n-mcp with proper context:
{
  "name": "Stock Data Sync - Best Practices Applied",
  "nodes": [
    {
      "type": "schedule",
      "parameters": {
        "rule": "*/5 * * * *",  // Every 5 min (rate limit friendly)
        "note": "Context7: Avoid overwhelming API with too frequent calls"
      }
    },
    {
      "type": "batch",
      "parameters": {
        "batchSize": 10,  // Context7: Polygon.io allows 5 req/sec
        "note": "Batch processing prevents rate limit errors"
      }
    },
    {
      "type": "error-handler",
      "parameters": {
        "retry": true,
        "maxRetries": 3,  // Context7: Retry on transient failures
        "note": "Graceful error handling for production reliability"
      }
    },
    {
      "type": "supabase",
      "parameters": {
        "operation": "upsert",  // Context7: Handle duplicates gracefully
        "conflictTarget": "symbol,timestamp",
        "note": "Upsert prevents duplicate key errors"
      }
    }
  ]
}
```

**Context Categories:**
- **Security Context** - Why we use specific auth patterns
- **Performance Context** - Why certain optimizations matter
- **Reliability Context** - Why error handling is critical
- **Scalability Context** - Why certain architectures scale better
- **Maintainability Context** - Why code organization matters

#### 3. n8n-workflows (Community n8n Workflow Templates)

**Purpose:** REFERENCE templates to build our OWN working workflows

**Primary Use Cases:**
- ✅ **Workflow Blueprints** - See how others structure similar workflows
- ✅ **Node Configuration Examples** - Reference for proper node setup
- ✅ **Implementation Patterns** - Proven workflow patterns to adapt
- ✅ **Starting Points** - Base templates to customize for our needs
- ✅ **Problem-Solving Reference** - See how others solved similar challenges

**Installation:**
```bash
# Already included via mcp-remote
```

**Configuration (.mcp-config.json):**
```json
{
  "mcpServers": {
    "n8n-workflows-docs": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "https://gitmcp.io/Zie619/n8n-workflows"
      ]
    }
  }
}
```

**What Claude uses n8n-workflows for:**
- **REFERENCE** existing workflow structures before building
- **LEARN** from community implementations
- **ADAPT** proven patterns to our specific needs
- **AVOID** common mistakes others have solved
- **ACCELERATE** development by not reinventing the wheel

**Example Reference-Based Workflow Building:**
```python
# User: "Build a workflow that syncs Supabase data to Google Sheets"

# 1. Claude queries n8n-workflows-docs:
#    Q: "Find workflows that integrate Supabase and Google Sheets"
#    Returns: 3 community templates with different approaches

# 2. Claude analyzes templates:
#    Template A: Uses polling (checks every 5 min)
#    Template B: Uses webhooks (real-time)
#    Template C: Uses scheduled batch sync

# 3. Claude queries Context7:
#    Q: "When should I use webhooks vs polling for database sync?"
#    A: Webhooks for real-time, polling for batch operations

# 4. Claude CREATES our custom workflow using n8n-mcp:
#    - Takes webhook approach from Template B (best for real-time)
#    - Adds error handling from Template C (production-ready)
#    - Customizes for our specific Supabase schema
#    - Adds our custom business logic

{
  "name": "Supabase → Google Sheets (Custom Build)",
  "note": "Based on community template, adapted for our needs",
  "nodes": [
    {
      "type": "webhook",
      "note": "Adapted from n8n-workflows template #234"
    },
    {
      "type": "supabase-query",
      "note": "Our custom schema fields"
    },
    {
      "type": "data-transform",
      "note": "Our specific business logic"
    },
    {
      "type": "google-sheets",
      "note": "Based on template #234, customized columns"
    },
    {
      "type": "error-handler",
      "note": "Added from template #456 best practices"
    }
  ]
}
```

**Workflow Building Process:**
```javascript
// Step 1: REFERENCE (n8n-workflows-docs)
//   "Show me templates for duplicate detection workflows"
//   → Returns 5 community examples

// Step 2: CONTEXT (context7-docs)
//   "Why do these templates use fuzzy matching vs exact matching?"
//   → Explains WHY fuzzy matching is more robust

// Step 3: CREATE (n8n-mcp)
//   Claude builds OUR workflow:
//   - Structure from community template
//   - Logic informed by Context7
//   - Customized for our specific use case
//   - Tested and deployed via n8n-mcp

// Result: Working production workflow built in minutes, not hours
```

**Key Difference from Context7:**
- **Context7** = WHY and HOW (principles, best practices, reasoning)
- **n8n-workflows** = WHAT (actual workflow examples, node configs, patterns)

**Example Template Usage:**
```python
# REFERENCE: "Find workflows for API rate limiting"
# RETURNS: Template showing batch processing + delay nodes

# REFERENCE: "Show me error handling patterns in n8n"
# RETURNS: Templates with retry logic, fallback paths, error notifications

# REFERENCE: "Get workflows that use Polygon.io for stock data"
# RETURNS: Templates with API auth, data parsing, error handling

# Then Claude ADAPTS these patterns into OUR custom workflow
```

**Categories Available:**
- Data synchronization workflows
- API integration patterns
- Database operation workflows
- Notification and alerting workflows
- Data transformation workflows
- Scheduled automation workflows
- Event-driven workflows
- Multi-step business logic workflows

### The Three-MCP Workflow (How They Work Together)

**Complete Workflow Automation Process:**

```mermaid
graph TD
    A[User Request: Build workflow] --> B[n8n-workflows-docs]
    B --> C[REFERENCE: Find similar templates]
    C --> D[context7-docs]
    D --> E[CONTEXT: Understand WHY/HOW]
    E --> F[n8n-mcp]
    F --> G[CREATE: Build custom workflow]
    G --> H[TEST: Execute & verify]
    H --> I{Tests Pass?}
    I -->|No| J[DEBUG: Get errors]
    J --> D
    I -->|Yes| K[DEPLOY: Activate workflow]
```

**Real Example - Building Duplicate Detection Workflow:**

```python
# USER: "Build me a duplicate lead detection workflow"

# ===== STEP 1: REFERENCE (n8n-workflows-docs) =====
# Claude: "Show me duplicate detection workflow templates"
# Returns: 5 community templates
#   - Template #1: Email-only matching
#   - Template #2: Multi-field fuzzy matching ✓ (best approach)
#   - Template #3: Phone number matching
#   - Template #4: Company domain clustering
#   - Template #5: ML-based detection

# ===== STEP 2: CONTEXT (context7-docs) =====
# Claude: "Why use fuzzy matching over exact matching for duplicates?"
# Returns: Best practices explanation
#   - Names have typos/variations
#   - Phone formats differ (+1-555-1234 vs 5551234)
#   - Email domains can be same company (gmail vs company.com)
#   - Fuzzy matching catches 85% more duplicates

# Claude: "What's the proper risk scoring approach?"
# Returns: Industry standard patterns
#   - Binary yes/no misses edge cases
#   - Risk scores (0-1) allow manual review threshold
#   - Multi-algorithm consensus more accurate
#   - Weighted scoring based on data quality

# ===== STEP 3: CREATE (n8n-mcp) =====
# Claude builds the workflow using n8n-mcp:

workflow = {
  "name": "Duplicate Lead Detection - Production Ready",
  "metadata": {
    "based_on": "n8n-workflows template #2",
    "context_applied": "context7 fuzzy matching best practices",
    "customized_for": "LeadFly AI duplicate prevention"
  },
  "nodes": [
    {
      "type": "webhook",
      "name": "Lead Input",
      "parameters": {
        "path": "leadfly/duplicate-check",
        "method": "POST"
      },
      "note": "From template #2"
    },
    {
      "type": "supabase-query",
      "name": "Fetch Existing Leads",
      "parameters": {
        "operation": "select",
        "table": "leads",
        "filters": "email ILIKE {{$json.email}} OR phone SIMILAR TO {{$json.phone}}"
      },
      "note": "Context7: Use fuzzy operators for better matching"
    },
    {
      "type": "function",
      "name": "Multi-Algorithm Detection",
      "parameters": {
        "code": `
          // Algorithm 1: Exact email (weight: 0.4)
          // Algorithm 2: Phone fuzzy (weight: 0.3)
          // Algorithm 3: Company+Name fuzzy (weight: 0.2)
          // Algorithm 4: Domain clustering (weight: 0.1)
          // Context7: Multi-algorithm consensus approach
        `
      },
      "note": "From template #2, enhanced with Context7 best practices"
    },
    {
      "type": "function",
      "name": "Risk Scoring",
      "parameters": {
        "code": `
          const risk_score = (
            email_match * 0.4 +
            phone_match * 0.3 +
            name_match * 0.2 +
            domain_match * 0.1
          );
          // Context7: Weighted scoring based on data reliability
        `
      },
      "note": "Context7: Risk scores better than binary"
    },
    {
      "type": "if",
      "name": "Risk Assessment",
      "parameters": {
        "conditions": [
          ["{{$json.risk_score}}", ">", "0.8"],  // High risk - block
          ["{{$json.risk_score}}", ">", "0.5"],  // Medium - flag
          ["{{$json.risk_score}}", "<", "0.5"]   // Low - allow
        ]
      },
      "note": "Context7: Three-tier approach for edge cases"
    },
    {
      "type": "error-handler",
      "name": "Error Handling",
      "parameters": {
        "retry": true,
        "maxRetries": 3,
        "fallback": "allow_processing"
      },
      "note": "From template #5, Context7: Fail open for better UX"
    }
  ]
}

# ===== STEP 4: TEST (n8n-mcp) =====
# Claude: Execute workflow with test data
test_result = n8n_mcp.execute_workflow(
  workflow_id="duplicate-detection",
  test_data={
    "email": "john.doe@company.com",
    "phone": "+1-555-1234",
    "name": "John Doe",
    "company": "Acme Corp"
  }
)

# Verify: risk_score = 0.85 (high duplicate probability) ✓
# Verify: action_taken = "block_duplicate" ✓
# Verify: confidence = 0.95 ✓

# ===== STEP 5: DEPLOY (n8n-mcp) =====
# Claude: Activate workflow for production
n8n_mcp.activate_workflow("duplicate-detection")
# Status: LIVE ✓
```

**Summary of MCP Roles:**

| MCP | Purpose | When Used | Output |
|-----|---------|-----------|--------|
| **n8n-workflows-docs** | REFERENCE templates | Before building | Template examples, node configs |
| **context7-docs** | CONTEXT (WHY/HOW) | During design | Best practices, reasoning, patterns |
| **n8n-mcp** | CREATE/TEST/DEPLOY | Implementation | Working production workflow |

**Workflow:** REFERENCE → CONTEXT → CREATE → TEST → DEPLOY

### Complete MCP Configuration File

Create `.mcp-config.json` in your project root:

```json
{
  "mcpServers": {
    "n8n-mcp": {
      "command": "npx",
      "args": ["n8n-mcp"],
      "env": {
        "MCP_MODE": "stdio",
        "LOG_LEVEL": "error",
        "DISABLE_CONSOLE_OUTPUT": "true",
        "N8N_API_URL": "https://your-n8n-instance.com",
        "N8N_API_KEY": "your_n8n_api_key"
      }
    },
    "context7-docs": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "https://gitmcp.io/upstash/context7"
      ]
    },
    "n8n-workflows-docs": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "https://gitmcp.io/Zie619/n8n-workflows"
      ]
    },
    "supabase-db": {
      "command": "npx",
      "args": ["@anthropic/mcp-server-postgres"],
      "env": {
        "DATABASE_URL": "postgresql://postgres:PASSWORD@db.PROJECT.supabase.co:5432/postgres"
      }
    }
  }
}
```

### Credentials Setup

Add to `credentials/.env`:
```bash
# MCP Configuration
MCP_SERVERS_DIR=/path/to/mcp/servers
MCP_ALLOWED_DOMAINS=api.polygon.io,api.massive.com

# For database MCP server
SUPABASE_CONNECTION_STRING=postgresql://postgres:PASSWORD@db.PROJECT.supabase.co:5432/postgres

# n8n MCP Integration
N8N_API_URL=https://your-n8n-instance.com
N8N_API_KEY=your_n8n_api_key
```

### Real-World MCP + n8n Workflow Example

**Scenario:** Automated duplicate lead prevention with Claude oversight

**Components:**
1. **n8n workflow** - Duplicate detection algorithm (already built)
2. **n8n-mcp** - Let Claude trigger workflow
3. **context7-docs** - Claude can lookup best practices
4. **supabase-db MCP** - Claude can verify results in database

**Flow:**
```python
# 1. User submits lead via API
# 2. Claude receives lead data via MCP
# 3. Claude searches context7 for duplicate prevention best practices
# 4. Claude triggers n8n "duplicate-prevention" workflow via n8n-mcp
# 5. n8n workflow runs multi-algorithm detection
# 6. Claude queries Supabase via MCP to verify no duplicate saved
# 7. Claude returns result to user

# All automated, zero manual intervention!
```

**Implementation:**
```javascript
// n8n workflow triggered by Claude via MCP
{
  "workflow_id": "duplicate-prevention-agent",
  "trigger": "mcp_tool_call",
  "input": {
    "user_id": "uuid",
    "lead_data": {
      "email": "contact@company.com",
      "phone": "+1-555-123-4567",
      "company": "Acme Corp"
    }
  },
  "output": {
    "duplicate_found": false,
    "risk_level": "low",
    "action_taken": "allow_processing"
  }
}
```

### MCP Templates Quick Reference

| Template | Purpose | Key Capability |
|----------|---------|----------------|
| n8n-mcp | Control n8n workflows | Execute, monitor, manage workflows |
| context7-docs | Documentation search | Multi-source knowledge access |
| n8n-workflows-docs | Workflow templates | Pre-built workflow discovery |
| @anthropic/mcp-server-postgres | Database access | Direct SQL queries from Claude |
| @anthropic/mcp-server-filesystem | File system access | Read/write files from Claude |
| @anthropic/mcp-server-fetch | API access | HTTP requests from Claude |

### When to Use n8n vs MCP

| Use Case | Use n8n | Use MCP |
|----------|---------|---------|
| Scheduled tasks (cron jobs) | ✅ Yes | ❌ No |
| React to external webhooks | ✅ Yes | ❌ No |
| Multi-step workflows with branching | ✅ Yes | ❌ No |
| Give Claude direct data access | ❌ No | ✅ Yes |
| Claude needs to query databases | ❌ No | ✅ Yes |
| Claude needs to call APIs | ❌ No | ✅ Yes |
| No-code automation | ✅ Yes | ❌ No |
| Complex business logic | ✅ Yes | ❌ No |

**Best Practice:** Use both together
- **n8n** for automated workflows (scheduled syncs, event reactions)
- **MCP** to give Claude access to trigger those workflows or query data

**Example Combined Flow:**
1. Claude queries portfolio via MCP (get current positions)
2. Claude analyzes and decides to rebalance
3. Claude triggers n8n "rebalance-portfolio" workflow via MCP
4. n8n workflow executes trades, updates Massive.com, sends notifications
5. Claude queries portfolio again via MCP to verify

---

## Environment Management

### Loading Environment Variables
```bash
# Method 1: Export from .env file
export $(grep -v '^#' credentials/.env | xargs)

# Method 2: Source .env file
set -a
source credentials/.env
set +a

# Method 3: Use with specific command
env $(cat credentials/.env | xargs) npm run dev
```

### Credential File Template
Create `credentials/.env.template`:
```bash
# Supabase
SUPABASE_URL=https://YOUR_PROJECT_ID.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_key
SUPABASE_DB_PASSWORD=your_db_password
SUPABASE_HOST=db.YOUR_PROJECT_ID.supabase.co
SUPABASE_USER=postgres
SUPABASE_DB=postgres

# Vercel
VERCEL_TOKEN=your_vercel_token
VERCEL_ORG_ID=your_org_id
VERCEL_PROJECT_ID=your_project_id

# AWS
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-east-2
AWS_EC2_INSTANCE_ID=i-your_instance_id

# GitHub
GITHUB_TOKEN=your_github_token

# API Keys
POLYGON_API_KEY=your_polygon_key
OPENAI_API_KEY=your_openai_key
```

---

## Automation Scripts Directory Structure

```
scripts/
├── automation/
│   ├── test-deployment.py          # Playwright testing
│   ├── verify-build.sh             # Build verification
│   └── health-check.sh             # Service health checks
├── deployment/
│   ├── deploy-to-vercel.sh         # Vercel deployment
│   ├── deploy-to-ec2.sh            # EC2 deployment
│   └── deploy-ios.sh               # iOS TestFlight deployment
└── database/
    ├── run-migration.sh            # Run SQL migrations
    ├── backup-db.sh                # Database backups
    └── seed-db.sh                  # Seed test data
```

---

## Key Reminders

1. **NEVER say "I can't automate X"** - Check this playbook first
2. **Supabase migrations:** Use psql command-line, credentials are in `.env`
3. **Vercel deployments:** Use CLI with token, don't ask user to deploy manually
4. **Testing:** ALWAYS verify with Playwright before claiming success
5. **Credentials:** ALL keys/tokens stored in `credentials/` directory
6. **Scripts:** ALL automation scripts in `scripts/` directory with execute permissions

---

## Adding New Automation

When you discover a new automation solution:

1. Document it in this playbook under appropriate section
2. Create reusable script in `scripts/` directory
3. Update DEBUGGING-LOG.md with the problem it solves
4. Test the automation before documenting
5. Include example usage and output

**Format:**
```markdown
### Task Name

**Problem:** What manual task this automates

**Solution:**
```bash
# Command or script
```

**Usage:**
```bash
# Example with actual values
```

**Expected Output:**
```
Sample output here
```
```

---

## Credential Locations Reference

**CRITICAL:** Before asking "where is X credential?", check these locations:

1. `credentials/.env` - Primary credential storage
2. `credentials/services/supabase.env` - Supabase-specific
3. `credentials/services/vercel.env` - Vercel-specific
4. `credentials/services/aws.env` - AWS-specific
5. Backend `.env` files (for reference only, copy to template)

**Workflow:**
- User provides credential → Save to `credentials/.env` immediately
- Update `.env.template` with placeholder
- Document in DEBUGGING-LOG.md when credential was added
