# EFFICIENCY CHECKLIST

**Purpose:** Pre-response verification checklist. Read this BEFORE every response to prevent common mistakes.

**Last Updated:** 2025-12-11

---

## 🚨 MANDATORY PRE-RESPONSE CHECKLIST

Run through this checklist BEFORE responding to every user request:

### 1. Have We Solved This Before?

- [ ] Search DEBUGGING-LOG.md for similar symptoms/errors
- [ ] Check tags: #authentication, #supabase, #vercel, #deployment, etc.
- [ ] Review "Related Issues" section for patterns
- [ ] If found: Use previous solution, don't reinvent

**Command to search:**
```bash
grep -i "keyword" .claude/DEBUGGING-LOG.md
```

**Common searches:**
- Error codes: "PGRST116", "404", "JWT"
- Technologies: "supabase", "vercel", "aws"
- Features: "authentication", "routing", "deployment"

---

### 2. Can This Be Automated?

**STOP and check AUTOMATION-PLAYBOOK.md if you're about to:**
- [ ] Ask user to manually run migrations
- [ ] Ask user to manually deploy to Vercel
- [ ] Ask user to copy/paste commands
- [ ] Ask user to manually SSH into servers
- [ ] Say "I can't automate X"

**Red flag phrases that trigger this check:**
- "Please manually..."
- "I can't automate..."
- "Copy and paste this..."
- "Run this in the dashboard..."
- "SSH into the server and..."

**Where to check:**
- AUTOMATION-PLAYBOOK.md → Supabase Operations
- AUTOMATION-PLAYBOOK.md → Vercel Deployments
- AUTOMATION-PLAYBOOK.md → AWS EC2 Management
- scripts/ directory for existing scripts

---

### 3. Do We Have These Credentials?

**STOP and check credentials/ directory if you're about to:**
- [ ] Ask user "What's the [service] password/key/token?"
- [ ] Request API keys we've used before
- [ ] Ask for database credentials
- [ ] Request deployment tokens

**Check these locations IN ORDER:**
1. `credentials/.env` (primary storage)
2. `credentials/services/[service].env` (service-specific)
3. Backend project `.env` files (for reference)
4. DEBUGGING-LOG.md (search for "Added [SERVICE] credentials")

**Standard credentials we should have:**
- SUPABASE_DB_PASSWORD
- SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_KEY
- VERCEL_TOKEN, VERCEL_ORG_ID, VERCEL_PROJECT_ID
- AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION
- GITHUB_TOKEN
- Third-party API keys (POLYGON_API_KEY, OPENAI_API_KEY, etc.)

---

### 4. Will I Verify Before Claiming Success?

**🚨 MANDATORY TRIPLE VERIFICATION PROTOCOL 🚨**

**ABSOLUTE RULE:** NEVER claim "it's done" or "it's working" until ALL THREE verification levels pass.

**STOP if you're about to:**
- [ ] Say "it's working now" without testing
- [ ] Deploy without verification
- [ ] Claim "this should work" without proof
- [ ] Ask user to "check if there are any errors" (YOU check first!)
- [ ] Ask user to copy/paste error messages (YOU find them first!)

**Required: Run Triple Verification Script**

```bash
# For frontend/web applications
./scripts/automation/complete-verification.sh https://www.yourapp.com

# OR use Python version
python3 scripts/automation/triple-verify.py https://www.yourapp.com

# ONLY claim success if exit code = 0
# If exit code = 1, FIX ERRORS and re-run
```

**What Triple Verification Does:**

**Level 1: Automated Testing**
- Loads page with Playwright
- Captures all console messages (errors, warnings, logs)
- Detects JavaScript exceptions
- Records network failures (404s, 500s, etc.)
- Takes screenshots
- EXIT CRITERIA: Status 200, no console errors, no network failures

**Level 2: Visual Verification**
- Screenshots entire page
- Verifies page loads completely
- Checks page title
- Confirms URL is correct
- EXIT CRITERIA: Page renders without crashing

**Level 3: Error Scanning**
- Scans for console.error
- Scans for console.warn
- Checks for unhandled promise rejections
- Verifies no 404s on critical resources
- EXIT CRITERIA: Zero critical errors detected

**Only claim success when:**
```
✅ Level 1 PASSED
✅ Level 2 PASSED
✅ Level 3 PASSED
```

**Full documentation:** `.claude/TRIPLE-VERIFICATION-PROTOCOL.md`

---

### 5. Have I Mapped the User Journey?

**STOP if you're about to build authentication/user-facing features without:**
- [ ] Identifying WHO the user is
- [ ] Understanding WHERE they're coming from
- [ ] Defining WHAT they expect to see
- [ ] Explaining WHY they'd take next action
- [ ] Planning HOW the system facilitates this

**User Journey Template:**
```
1. WHO: [New visitor | Returning user | Authenticated user]
2. WHERE: [Direct link | Search | Internal navigation]
3. WHAT: [Expected first screen/action]
4. WHY: [Motivation for next step]
5. HOW: [System design to facilitate]

Flow:
[Start] → [Step 1] → [Step 2] → [Goal]
          ↓
       [Alternative path if condition X]
```

**Example (Authentication):**
```
1. WHO: New visitor
2. WHERE: Direct link to site root
3. WHAT: Expects to see login/signup page
4. WHY: Wants to access platform features
5. HOW: Redirect / → /login.html

Flow:
/ → /login → /signup → /onboarding → /dashboard
     ↓
  (if authenticated, skip to /dashboard)
```

**Where to check:** SENIOR-ENGINEER-PRINCIPLES.md → User Journey Mapping

---

### 6. Have I Checked the Schema?

**STOP if you're about to write SQL INSERT/UPDATE without:**
- [ ] Querying information_schema to see actual columns
- [ ] Verifying data types match
- [ ] Confirming constraints (NOT NULL, UNIQUE, etc.)

**Required schema check:**
```sql
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_schema = 'public'
AND table_name = 'YOUR_TABLE'
ORDER BY ordinal_position;
```

**Then write query using ONLY confirmed columns.**

---

### 7. Will I Document the Solution?

**If solving a NEW issue, commit to:**
- [ ] Document in DEBUGGING-LOG.md using template
- [ ] Update AUTOMATION-PLAYBOOK.md if automation discovered
- [ ] Update COMMON-MISTAKES.md if pattern identified
- [ ] Cross-reference related issues

**When to document:**
- Immediately after solving issue
- Before moving to next task
- While details are fresh

**Use template from:** DEBUGGING-LOG.md → Issue Template

---

### 8. Is There an Existing Script?

**STOP and check scripts/ directory if you're about to:**
- [ ] Write one-off commands
- [ ] Repeat similar commands from before
- [ ] Run deployment/migration/test manually

**Standard scripts directory:**
```
scripts/
├── automation/
│   ├── test-deployment.py
│   ├── verify-build.sh
│   └── health-check.sh
├── deployment/
│   ├── deploy-to-vercel.sh
│   ├── deploy-to-ec2.sh
│   └── deploy-ios.sh
└── database/
    ├── run-migration.sh
    ├── backup-db.sh
    └── seed-db.sh
```

**If script doesn't exist:**
1. Create reusable script
2. Make executable: `chmod +x script.sh`
3. Document in AUTOMATION-PLAYBOOK.md
4. Use script instead of one-off command

---

## 🎯 Quick Decision Tree

Use this flowchart for every user request:

```
User Request Received
       ↓
[1] Have we solved this? → YES → Use previous solution
       ↓ NO                            ↓
[2] Can this be automated? → YES → Check AUTOMATION-PLAYBOOK
       ↓ NO                             ↓
[3] Need credentials? → YES → Check credentials/ directory
       ↓ NO                             ↓
[4] Building user feature? → YES → Map user journey first
       ↓ NO                             ↓
[5] Writing SQL? → YES → Check schema first
       ↓ NO                             ↓
[6] Existing script? → YES → Use script from scripts/
       ↓ NO                             ↓
Implement Solution
       ↓
[7] Verify with tests → Must pass before claiming success
       ↓
[8] Document solution → Update logs/playbook/mistakes
       ↓
Respond to User (with evidence)
```

---

## 📋 Per-Task Checklists

### For Database Migrations

- [ ] Check credentials/.env for DB password
- [ ] Check schema with information_schema query
- [ ] Write migration targeting only existing columns
- [ ] Use scripts/database/run-migration.sh
- [ ] Verify with SELECT query after migration
- [ ] Document in DEBUGGING-LOG if new pattern

### For Vercel Deployments

- [ ] Check credentials/.env for VERCEL_TOKEN
- [ ] Use scripts/deployment/deploy-to-vercel.sh
- [ ] Write Playwright verification test
- [ ] Run test and capture output/screenshot
- [ ] Check for 404s on key routes
- [ ] Only claim success if tests pass

### For Authentication Features

- [ ] Map user journey from first principles
- [ ] Define all user states (new/returning/authenticated)
- [ ] Plan redirect logic before implementation
- [ ] Test as new user (clear browser state)
- [ ] Verify with Playwright script
- [ ] Document flow in README or user journey doc

### For API Integrations

- [ ] Check credentials/.env for API keys
- [ ] Test API with curl first
- [ ] Verify response structure
- [ ] Handle errors gracefully
- [ ] Write health check script
- [ ] Document API usage in AUTOMATION-PLAYBOOK

### For New Features

- [ ] Check DEBUGGING-LOG for similar implementations
- [ ] Map user journey if user-facing
- [ ] Check for existing scripts/utilities
- [ ] Write tests before claiming complete
- [ ] Verify tests pass
- [ ] Document any new patterns

---

## 🚫 Red Flags Requiring Immediate Stop

If you catch yourself using these phrases, STOP and check this list:

| Red Flag Phrase | What to Check | Where to Look |
|----------------|---------------|---------------|
| "I can't automate..." | Can it actually be automated? | AUTOMATION-PLAYBOOK.md |
| "Please manually..." | Is there a script for this? | scripts/ directory |
| "It should work now" | Have you verified? | This checklist #4 |
| "What's the password for..." | Do we have it already? | credentials/.env |
| "Copy and paste this..." | Can we run it directly? | AUTOMATION-PLAYBOOK.md |
| "Let me deploy this" | Have you planned verification? | This checklist #4 |
| "I'll create this feature" | Have you mapped user journey? | This checklist #5 |
| "Here's the SQL..." | Have you checked schema? | This checklist #6 |

---

## 📊 Efficiency Scoring

After each task, score yourself:

**10/10 Efficiency:**
- [ ] Checked all relevant sections of checklist
- [ ] Found and reused previous solution OR documented new one
- [ ] Automated everything that could be automated
- [ ] Verified before claiming success
- [ ] Documented solution for future reference

**7-9/10 Efficiency:**
- [ ] Checked most sections of checklist
- [ ] Used some automation but missed opportunities
- [ ] Verified major functionality
- [ ] Documented most important parts

**4-6/10 Efficiency:**
- [ ] Checked some sections
- [ ] Mixed automation and manual steps
- [ ] Partial verification
- [ ] Incomplete documentation

**1-3/10 Efficiency:**
- [ ] Skipped checklist
- [ ] Asked for manual work that could be automated
- [ ] No verification
- [ ] No documentation

**0/10 Efficiency:**
- [ ] Claimed success without verification
- [ ] Asked for credentials we already have
- [ ] Repeated previous mistakes from DEBUGGING-LOG
- [ ] No documentation

**Target:** Consistent 10/10 scores

---

## 🔄 Weekly Review

Every week, review efficiency:

**Monday Morning:**
- [ ] Read COMMON-MISTAKES.md
- [ ] Scan last week's DEBUGGING-LOG entries
- [ ] Review credentials/ for new additions
- [ ] Check scripts/ for new utilities

**Friday Afternoon:**
- [ ] Calculate average efficiency score for week
- [ ] Identify patterns in mistakes
- [ ] Update COMMON-MISTAKES.md if needed
- [ ] Plan improvements for next week

---

## ✅ Success Metrics

Track these to measure improvement:

| Metric | Target | How to Measure |
|--------|--------|----------------|
| False "can't automate" claims | 0 | Count per week |
| Unverified success claims | 0 | Count per week |
| Requests for existing credentials | 0 | Count per week |
| Repeated mistakes from log | 0 | Count per month |
| Issues documented within 1 hour | 100% | Log timestamps |
| Tests written before claiming done | 100% | Count per task |
| Average efficiency score | 10/10 | Weekly average |

---

## 🎓 Learning Mode

When encountering a new technology or pattern:

**Before using:**
- [ ] Search DEBUGGING-LOG for previous usage
- [ ] Check AUTOMATION-PLAYBOOK for patterns
- [ ] Read official documentation
- [ ] Test in isolation first

**After using:**
- [ ] Document in AUTOMATION-PLAYBOOK
- [ ] Create reusable script if applicable
- [ ] Note gotchas in COMMON-MISTAKES
- [ ] Add to verification checklist

---

## 💡 Remember

**The goal is NOT speed, it's EFFICIENCY:**
- Taking 2 minutes to check this list → Saves 30 minutes of rework
- Verifying before claiming success → Prevents user frustration
- Documenting solutions → Prevents solving same issue twice
- Using automation → Scales better than manual work

**User's feedback:**
> "as of right now i would give you a 2 out of 10 for effiency. how do we get that to 10/10"

**This checklist is how we get to 10/10.**

---

## 📱 Quick Reference Card

Print this and keep visible:

```
BEFORE EVERY RESPONSE:
☐ Check DEBUGGING-LOG (have we solved this?)
☐ Check AUTOMATION-PLAYBOOK (can we automate?)
☐ Check credentials/ (do we have keys?)
☐ Plan verification (how will I test?)

BEFORE CLAIMING SUCCESS:
☐ Write test
☐ Run test
☐ Capture evidence
☐ Tests pass?

AFTER SOLVING:
☐ Document in DEBUGGING-LOG
☐ Update AUTOMATION-PLAYBOOK if new automation
☐ Update COMMON-MISTAKES if new pattern
☐ Cross-reference related issues

RED FLAGS:
"I can't automate..." → Check playbook
"Please manually..." → Check scripts
"It should work..." → Run verification
"What's the password..." → Check credentials
```
