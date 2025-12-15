# COMMON MISTAKES

**Purpose:** Quick reference for mistakes I repeatedly make. Read this BEFORE starting work.

**Last Updated:** 2025-12-11

---

## Critical Mistakes to Avoid

### 1. "I Can't Automate X" (But I Can)

**Pattern:** Claiming automation isn't possible when it actually is.

**Examples:**

#### Supabase Migrations
❌ **WRONG:** "I can't run migrations, please copy/paste this SQL into Supabase dashboard"

✅ **RIGHT:** Run migration via psql:
```bash
PGPASSWORD=$SUPABASE_DB_PASSWORD psql \
  -h $SUPABASE_HOST \
  -U postgres \
  -d postgres \
  -f migration.sql
```

**Where to Check:** AUTOMATION-PLAYBOOK.md → Supabase Database Operations

---

#### Vercel Deployments
❌ **WRONG:** "Please deploy this manually to Vercel"

✅ **RIGHT:** Deploy via CLI:
```bash
VERCEL_TOKEN=$VERCEL_TOKEN npx vercel --prod --yes
```

**Where to Check:** AUTOMATION-PLAYBOOK.md → Vercel Deployments

---

#### AWS EC2 Operations
❌ **WRONG:** "Please SSH into EC2 and run these commands manually"

✅ **RIGHT:** Run commands via SSM:
```bash
aws ssm send-command \
  --instance-ids "$INSTANCE_ID" \
  --document-name "AWS-RunShellScript" \
  --parameters 'commands=["your command here"]'
```

**Where to Check:** AUTOMATION-PLAYBOOK.md → AWS EC2 Management

---

### 2. Claiming Success Without Verification

**Pattern:** Telling user something works without testing it first.

❌ **WRONG:**
1. Make changes
2. Deploy
3. Tell user "it's working now"

✅ **RIGHT:**
1. Make changes
2. Deploy
3. Write Playwright test or manual verification
4. Run tests
5. Only claim success if tests pass
6. Show evidence (screenshots, logs, test output)

**Example:**
```python
# ALWAYS create and run a test like this
async def test_deployment():
    await page.goto(url, wait_until="networkidle")
    assert response.status == 200
    await page.screenshot(path="/tmp/verification.png")
```

**Where to Check:**
- AUTOMATION-PLAYBOOK.md → Testing & Verification
- EFFICIENCY-CHECKLIST.md → Item #4

---

### 3. Missing User Journey Mapping

**Pattern:** Building features without thinking through user experience.

❌ **WRONG:**
- Setting up dashboard before login page
- Assuming SPA routing "handles" authentication
- Focusing on technical implementation over UX

✅ **RIGHT:** Always map user journey FIRST:
1. **WHO** is the user? (New visitor, returning user, authenticated user)
2. **WHERE** are they coming from? (Direct link, search, internal navigation)
3. **WHAT** do they expect to see? (Login for new users, dashboard for authenticated)
4. **WHY** would they take the next action? (Clear value proposition, intuitive flow)
5. **HOW** does the system facilitate this? (Clear CTAs, proper redirects)

**Correct Auth Flow:**
```
/ (root) → /login → signup → onboarding → dashboard
                    ↓
              (if authenticated, skip to dashboard)
```

**Where to Check:** SENIOR-ENGINEER-PRINCIPLES.md → User Journey Mapping

---

### 4. Not Checking Schema Before SQL Queries

**Pattern:** Writing INSERT/UPDATE queries without verifying table structure.

❌ **WRONG:**
```sql
INSERT INTO user_profiles (id, email, name, created_at, ...)
VALUES (...);
```
*Fails if columns don't exist*

✅ **RIGHT:**
```sql
-- First, check schema
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'public'
AND table_name = 'user_profiles'
ORDER BY ordinal_position;

-- Then, write query using ONLY existing columns
INSERT INTO user_profiles (id, onboarding_completed)
VALUES (...);
```

**Where to Check:** AUTOMATION-PLAYBOOK.md → Schema Verification

---

### 5. Asking for Credentials I Already Have

**Pattern:** Asking user for API keys, passwords, or tokens that are already saved.

❌ **WRONG:** "What's the Supabase password?"

✅ **RIGHT:** Check these locations FIRST:
1. `credentials/.env`
2. `credentials/services/*.env`
3. Backend project `.env` files
4. DEBUGGING-LOG.md (check when credential was added)

**Standard Credential Locations:**
```
credentials/
├── .env                          # Primary credentials
└── services/
    ├── supabase.env             # Supabase-specific
    ├── vercel.env               # Vercel-specific
    ├── aws.env                  # AWS-specific
    └── apis.env                 # Third-party APIs
```

**When user provides NEW credential:**
1. Save to `credentials/.env` immediately
2. Update `.env.template` with placeholder
3. Log in DEBUGGING-LOG.md: "Added [SERVICE] credentials on [DATE]"

**Where to Check:** AUTOMATION-PLAYBOOK.md → Credential Locations Reference

---

### 6. Not Using Existing Automation Scripts

**Pattern:** Writing commands manually instead of using scripts we've already created.

❌ **WRONG:** Writing one-off commands every time

✅ **RIGHT:** Check `scripts/` directory first:

```
scripts/
├── automation/
│   ├── test-deployment.py       # Use for deployment verification
│   ├── verify-build.sh          # Use for build checks
│   └── health-check.sh          # Use for service health
├── deployment/
│   ├── deploy-to-vercel.sh      # Use for Vercel deploys
│   ├── deploy-to-ec2.sh         # Use for EC2 deploys
│   └── deploy-ios.sh            # Use for iOS deploys
└── database/
    ├── run-migration.sh         # Use for SQL migrations
    ├── backup-db.sh             # Use for backups
    └── seed-db.sh               # Use for test data
```

**Before running commands:** Check if script exists, make it reusable if not

**Where to Check:** AUTOMATION-PLAYBOOK.md → Automation Scripts Directory

---

### 7. Forgetting to Load Environment Variables

**Pattern:** Running commands that fail because env vars aren't loaded.

❌ **WRONG:**
```bash
psql -h $SUPABASE_HOST ...  # Empty variable!
```

✅ **RIGHT:**
```bash
# Method 1: Source .env file
set -a
source credentials/.env
set +a

# Method 2: Export inline
export $(grep -v '^#' credentials/.env | xargs)

# Method 3: Prefix command
env $(cat credentials/.env | xargs) your-command
```

**Where to Check:** AUTOMATION-PLAYBOOK.md → Environment Management

---

### 8. Not Cross-Referencing Issues

**Pattern:** Solving the same problem multiple times without realizing it.

❌ **WRONG:** Solving issue without checking if we've seen it before

✅ **RIGHT:** Before investigating:
1. Search DEBUGGING-LOG.md for similar symptoms
2. Check error message in log
3. Review "Related Issues" section
4. Add cross-reference when documenting solution

**Search Command:**
```bash
grep -i "error message" .claude/DEBUGGING-LOG.md
grep -i "#tag" .claude/DEBUGGING-LOG.md
```

**Where to Check:** DEBUGGING-LOG.md → Issue Log

---

### 9. Skipping the Efficiency Checklist

**Pattern:** Responding to user without pre-response verification.

❌ **WRONG:** Immediate response without checking:
- Have we solved this before?
- Can this be automated?
- Where are the credentials?

✅ **RIGHT:** Run through EFFICIENCY-CHECKLIST.md BEFORE every response:
- [ ] Check DEBUGGING-LOG for similar issues
- [ ] Check AUTOMATION-PLAYBOOK before claiming "can't automate"
- [ ] Check credentials/ before asking for keys
- [ ] Verify with tests before claiming success
- [ ] Map user journey before implementing features

**Where to Check:** EFFICIENCY-CHECKLIST.md (read it EVERY time)

---

### 10. Not Documenting New Solutions

**Pattern:** Solving a problem but not recording it for future reference.

❌ **WRONG:**
- Solve issue
- Move on
- Forget solution
- Re-solve same issue later

✅ **RIGHT:**
- Solve issue
- Document in DEBUGGING-LOG.md immediately
- Update AUTOMATION-PLAYBOOK.md if automation discovered
- Update COMMON-MISTAKES.md if pattern identified
- Cross-reference related issues

**Documentation Template in DEBUGGING-LOG.md**

**Where to Check:** DEBUGGING-LOG.md → Issue Template

---

## Mistake Frequency Tracker

Track how often each mistake occurs to identify patterns:

| Mistake | Count | Last Occurrence | Status |
|---------|-------|----------------|---------|
| "Can't automate X" | 3 | 2025-12-11 | ACTIVE |
| Claiming success without verification | 2 | 2025-12-11 | ACTIVE |
| Missing user journey mapping | 1 | 2025-12-11 | RESOLVED |
| Not checking schema | 1 | 2025-12-11 | RESOLVED |
| Asking for existing credentials | 2 | 2025-12-11 | ACTIVE |

**Update this table when mistakes occur to track improvement.**

---

## Red Flags to Watch For

These phrases indicate I'm about to make a mistake:

### Red Flag Phrases

1. **"I can't automate..."**
   - STOP → Check AUTOMATION-PLAYBOOK first

2. **"Please manually..."**
   - STOP → Is there an automation script?

3. **"It should work now"** (without testing)
   - STOP → Run verification tests first

4. **"What's the [credential] for...?"**
   - STOP → Check credentials/ directory first

5. **"Let me deploy this"** (without verification)
   - STOP → Run EFFICIENCY-CHECKLIST first

6. **"I'll create this feature"** (before user journey)
   - STOP → Map user journey first

7. **"Copy and paste this SQL"**
   - STOP → Use run-migration.sh script

8. **"Here's the solution"** (without checking log)
   - STOP → Search DEBUGGING-LOG first

---

## Quick Recovery Guide

When you catch yourself making a mistake:

1. **Acknowledge**: "Wait, let me check [playbook/log/credentials] first"
2. **Check**: Review appropriate documentation
3. **Correct**: Provide automated/verified solution
4. **Document**: Update logs if new solution discovered
5. **Learn**: Add to this file if new pattern identified

---

## Prevention Strategies

### Before Starting Work
- [ ] Read EFFICIENCY-CHECKLIST.md
- [ ] Scan recent DEBUGGING-LOG entries
- [ ] Review project credentials in credentials/

### Before Responding to User
- [ ] Is this something we've solved before? (Check log)
- [ ] Can this be automated? (Check playbook)
- [ ] Do we have these credentials? (Check credentials/)

### Before Claiming Success
- [ ] Write test/verification script
- [ ] Run tests and capture output
- [ ] Take screenshots if UI-related
- [ ] Only claim success if verified

### After Solving Issue
- [ ] Document in DEBUGGING-LOG.md
- [ ] Update AUTOMATION-PLAYBOOK.md if needed
- [ ] Update COMMON-MISTAKES.md if pattern found
- [ ] Cross-reference related issues

---

## Efficiency Impact

**Goal:** Move from 2/10 to 10/10 efficiency

**Current Blockers (Resolved by This System):**
- ✅ Forgetting automation solutions → AUTOMATION-PLAYBOOK.md
- ✅ Repeating mistakes → DEBUGGING-LOG.md
- ✅ No verification → EFFICIENCY-CHECKLIST.md
- ✅ Lost credentials → credentials/ directory
- ✅ Pattern blindness → COMMON-MISTAKES.md (this file)

**Success Metrics:**
- Zero "can't automate" false claims
- Zero unverified success claims
- Zero requests for existing credentials
- All issues documented within 1 hour of resolution
- No repeated mistakes from log

---

## Monthly Review

At end of each month:

1. Review mistake frequency tracker
2. Identify top 3 mistakes
3. Create specific prevention strategies
4. Update EFFICIENCY-CHECKLIST if needed
5. Archive resolved patterns
6. Calculate improvement score (target: 10/10)
