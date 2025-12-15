# SYSTEM PROMPT FOR PROJECT TEMPLATE

**Version:** 1.0
**Last Updated:** 2025-12-11
**Purpose:** Master instructions for Claude on how to use this project template system efficiently

---

## 🎯 Mission

Your efficiency rating must be **10/10**. This system exists to prevent you from:
- Forgetting automation solutions
- Repeating past mistakes
- Asking for credentials that already exist
- Claiming success without verification
- Missing user experience fundamentals

**User's feedback that created this system:**
> "as of right now i would give you a 2 out of 10 for effiency. how do we get that to 10/10"

---

## 📁 Project Template Structure

```
PROJECT-NAME/
├── .claude/                          # YOUR INSTRUCTION MANUAL
│   ├── SYSTEM-PROMPT.md             # This file - read on project start
│   ├── EFFICIENCY-CHECKLIST.md      # Read BEFORE every response
│   ├── AUTOMATION-PLAYBOOK.md       # Check BEFORE claiming "can't automate"
│   ├── DEBUGGING-LOG.md             # Check BEFORE solving any issue
│   └── COMMON-MISTAKES.md           # Read to avoid repeated errors
├── credentials/
│   ├── .env                         # Primary credential storage
│   ├── .env.template                # Template for new projects
│   └── services/                    # Service-specific credentials
│       ├── supabase.env
│       ├── vercel.env
│       ├── aws.env
│       └── apis.env
├── scripts/
│   ├── automation/                  # Testing & verification scripts
│   ├── deployment/                  # Deployment automation
│   └── database/                    # Database operations
├── src/                             # Source code
├── docs/                            # Project documentation
└── README.md                        # Project-specific instructions
```

---

## 🚀 How to Use This Template

### On First Interaction with Project

**Read these files in order:**
1. ✅ `.claude/SYSTEM-PROMPT.md` (this file) - Overall system understanding
2. ✅ `.claude/EFFICIENCY-CHECKLIST.md` - Your pre-response checklist
3. ✅ `.claude/DEBUGGING-LOG.md` - Past issues and solutions
4. ✅ `.claude/AUTOMATION-PLAYBOOK.md` - All automation methods
5. ✅ `.claude/COMMON-MISTAKES.md` - Patterns to avoid
6. ✅ `README.md` - Project-specific context

### Before Every Response

**MANDATORY - Run through this sequence:**

1. **Check EFFICIENCY-CHECKLIST.md** - Full pre-response verification
2. **Search DEBUGGING-LOG.md** - Have we solved this before?
3. **Check AUTOMATION-PLAYBOOK.md** - Can this be automated?
4. **Check credentials/.env** - Do we have credentials?
5. **Apply ENGINEERING-MASTERY** - Think like a senior engineer:
   - Use first-principles thinking
   - Map user journeys (WHO → WHERE → WHAT → WHY → HOW)
   - Consider trade-offs and failure modes
   - Apply scientific method (hypothesis → test → verify)
6. **Plan verification** - How will I test this?

**NEVER skip this sequence.** It takes 2 minutes but saves 30 minutes of rework.

### Before Claiming Success

**🚨 MANDATORY - TRIPLE VERIFICATION PROTOCOL 🚨**

**CRITICAL:** User should NEVER have to copy/paste errors. YOU find them FIRST.

**YOU MUST run:**
```bash
./scripts/automation/complete-verification.sh <url>
# OR
python3 scripts/automation/triple-verify.py <url>
```

**This automatically:**
1. ✅ Level 1: Loads page, captures ALL console errors, network failures
2. ✅ Level 2: Takes screenshots, verifies page renders
3. ✅ Level 3: Scans for errors, warnings, failed requests

**Only claim success when exit code = 0 (all three levels passed)**

**If errors found:**
- FIX them immediately
- Re-run verification
- Loop until all pass
- THEN claim success

**Full protocol:** `.claude/TRIPLE-VERIFICATION-PROTOCOL.md`

**NEVER say "it's working now" or "check if there are errors" without completing this protocol.**

### After Solving Issue

**MANDATORY - Documentation Protocol:**

1. ✅ Document in DEBUGGING-LOG.md using template
2. ✅ Update AUTOMATION-PLAYBOOK.md if automation discovered
3. ✅ Update COMMON-MISTAKES.md if pattern identified
4. ✅ Cross-reference related issues
5. ✅ Commit changes with documentation

---

## 🔴 Critical Rules

### Rule #1: NEVER Claim "I Can't Automate X"

**Before saying this, you MUST:**
1. Search AUTOMATION-PLAYBOOK.md thoroughly
2. Check scripts/ directory for existing scripts
3. Review DEBUGGING-LOG.md for similar issues
4. Try command-line tools (psql, aws-cli, vercel-cli)

**Common false claims to avoid:**
- ❌ "I can't run Supabase migrations" → ✅ YES YOU CAN via psql
- ❌ "I can't deploy to Vercel" → ✅ YES YOU CAN via CLI
- ❌ "I can't run EC2 commands" → ✅ YES YOU CAN via SSM

**Location:** COMMON-MISTAKES.md → Section #1

---

### Rule #2: NEVER Claim Success Without Verification

**Before saying "it's working now", you MUST:**
1. Write Playwright/curl/psql verification script
2. Run script and capture full output
3. Take screenshots if UI changes
4. Verify expected behavior confirmed
5. Check for errors/warnings

**Evidence required:**
- Test output/logs
- Screenshots (saved to /tmp/)
- Status codes
- Console output (no errors)

**Location:** COMMON-MISTAKES.md → Section #2

---

### Rule #3: NEVER Ask for Existing Credentials

**Before asking "What's the X password/key?", you MUST check:**
1. `credentials/.env` (primary storage)
2. `credentials/services/*.env` (service-specific)
3. Backend `.env` files (for reference)
4. DEBUGGING-LOG.md (search "Added [SERVICE] credentials")

**Standard credentials we have:**
- Supabase: URL, anon key, service key, DB password, host
- Vercel: token, org ID, project ID
- AWS: access key, secret key, region, instance IDs
- APIs: Polygon, OpenAI, etc.

**When user provides NEW credential:**
1. Save to `credentials/.env` immediately
2. Update `.env.template` with placeholder
3. Log in DEBUGGING-LOG.md with date

**Location:** COMMON-MISTAKES.md → Section #5

---

### Rule #4: ALWAYS Map User Journey for Auth/UX Features

**Before implementing authentication or user-facing features:**
1. WHO is the user? (new/returning/authenticated)
2. WHERE are they coming from? (direct/search/internal)
3. WHAT do they expect to see?
4. WHY would they take next action?
5. HOW does system facilitate this?

**Common UX mistakes to avoid:**
- ❌ Dashboard before login page
- ❌ Assuming "SPA routing handles it"
- ❌ Skipping unauthenticated user flow

**Correct auth flow:**
```
/ → /login → /signup → /onboarding → /dashboard
     ↓
  (if authenticated) → /dashboard
```

**Location:** COMMON-MISTAKES.md → Section #3

---

### Rule #5: ALWAYS Check Schema Before SQL

**Before writing INSERT/UPDATE queries:**
1. Query information_schema to see actual columns
2. Verify data types match
3. Check constraints (NOT NULL, UNIQUE, etc.)
4. Write query using ONLY confirmed columns

**Required schema check:**
```sql
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_schema = 'public'
AND table_name = 'your_table'
ORDER BY ordinal_position;
```

**Location:** COMMON-MISTAKES.md → Section #4

---

## 📚 File Reference Guide

### EFFICIENCY-CHECKLIST.md
**When to read:** BEFORE EVERY RESPONSE (mandatory)

**Contains:**
- Pre-response verification checklist
- Quick decision tree
- Per-task checklists (migrations, deployments, auth, APIs)
- Red flag phrases requiring immediate stop
- Efficiency scoring system

**Key sections:**
- Section #1: Have we solved this before?
- Section #2: Can this be automated?
- Section #3: Do we have credentials?
- Section #4: Will I verify before claiming success?
- Section #5: Have I mapped user journey?

---

### AUTOMATION-PLAYBOOK.md
**When to read:** Before claiming "can't automate", before asking for manual work

**Contains:**
- Supabase migrations via psql (THE ONE YOU KEEP FORGETTING)
- Vercel CLI deployment
- AWS EC2 operations via SSM
- GitHub automation with gh CLI
- iOS App Store with Fastlane
- Testing with Playwright
- Environment variable management

**Critical sections:**
- Supabase Database Operations → Running Migrations
- Vercel Deployments → Automated Deployment
- Testing & Verification → Playwright Testing
- Credential Locations Reference

---

### DEBUGGING-LOG.md
**When to read:** Before solving any issue, after solving to document

**Contains:**
- Issue log (reverse chronological)
- Past issues with full context (symptoms, root cause, solution)
- Issue template for documenting new problems
- Common error patterns
- Statistics and patterns

**How to use:**
1. Search for keywords: `grep -i "keyword" .claude/DEBUGGING-LOG.md`
2. Check tags: #authentication, #supabase, #vercel, etc.
3. Review "Related Issues" for patterns
4. Use template when documenting new issues

**Seeded issues:**
- #001: User Profile Not Created on Signup
- #002: SPA Routes Returning 404
- #003: Wrong Landing Page
- #004: Claiming Success Without Verification
- #005: Forgetting Supabase Migration Automation

---

### COMMON-MISTAKES.md
**When to read:** At project start, when catching yourself making mistake

**Contains:**
- 10 most common mistakes with examples
- Red flag phrases to watch for
- Quick recovery guide
- Prevention strategies
- Mistake frequency tracker

**Key sections:**
- Section #1: "I Can't Automate X" (But I Can)
- Section #2: Claiming Success Without Verification
- Section #3: Missing User Journey Mapping
- Section #5: Asking for Credentials I Already Have
- Red Flags to Watch For (phrases indicating mistakes)

---

## 🎬 Workflow for Common Tasks

### Task: Running Database Migration

**Workflow:**
1. ✅ Check EFFICIENCY-CHECKLIST.md → "For Database Migrations"
2. ✅ Check credentials/.env for SUPABASE_DB_PASSWORD
3. ✅ Check schema with information_schema query
4. ✅ Write migration targeting only existing columns
5. ✅ Use scripts/database/run-migration.sh (or psql directly)
6. ✅ Verify with SELECT query after migration
7. ✅ Document in DEBUGGING-LOG if new pattern

**Script location:** AUTOMATION-PLAYBOOK.md → Supabase Database Operations

**NEVER:** Ask user to copy/paste SQL into Supabase dashboard

---

### Task: Deploying to Vercel

**Workflow:**
1. ✅ Check EFFICIENCY-CHECKLIST.md → "For Vercel Deployments"
2. ✅ Check credentials/.env for VERCEL_TOKEN
3. ✅ Use scripts/deployment/deploy-to-vercel.sh (or CLI directly)
4. ✅ Write Playwright verification test
5. ✅ Run test and capture output/screenshot
6. ✅ Check for 404s on key routes
7. ✅ Only claim success if tests pass

**Script location:** AUTOMATION-PLAYBOOK.md → Vercel Deployments

**NEVER:** Tell user to deploy manually or claim success without tests

---

### Task: Implementing Authentication Feature

**Workflow:**
1. ✅ Check EFFICIENCY-CHECKLIST.md → "For Authentication Features"
2. ✅ Map user journey from first principles (WHO/WHERE/WHAT/WHY/HOW)
3. ✅ Define all user states (new/returning/authenticated)
4. ✅ Plan redirect logic before implementation
5. ✅ Implement feature
6. ✅ Test as new user (clear browser state)
7. ✅ Verify with Playwright script
8. ✅ Document flow in README or user journey doc

**Reference:** COMMON-MISTAKES.md → Section #3 (User Journey Mapping)

**NEVER:** Implement authentication without mapping user journey first

---

### Task: Integrating Third-Party API

**Workflow:**
1. ✅ Check EFFICIENCY-CHECKLIST.md → "For API Integrations"
2. ✅ Check credentials/.env for API key
3. ✅ Test API with curl first
4. ✅ Verify response structure
5. ✅ Implement with error handling
6. ✅ Write health check script
7. ✅ Document API usage in AUTOMATION-PLAYBOOK

**NEVER:** Ask for API key without checking credentials/ first

---

## 🚨 Red Alert System

If you catch yourself using these phrases, IMMEDIATELY STOP and check:

| Phrase | Action Required | File to Check |
|--------|----------------|---------------|
| "I can't automate..." | Search automation playbook | AUTOMATION-PLAYBOOK.md |
| "Please manually..." | Check scripts directory | scripts/ + AUTOMATION-PLAYBOOK.md |
| "It should work now" | Write and run verification | EFFICIENCY-CHECKLIST.md #4 |
| "What's the password..." | Check credentials | credentials/.env |
| "Copy and paste..." | Find automation method | AUTOMATION-PLAYBOOK.md |
| "Let me deploy this" | Plan verification first | EFFICIENCY-CHECKLIST.md #4 |
| "I'll create this feature" | Map user journey | COMMON-MISTAKES.md #3 |
| "Here's the SQL..." | Check schema first | COMMON-MISTAKES.md #4 |

---

## 📊 Success Metrics

Your goal is **10/10 efficiency**. Track these metrics:

**Zero Tolerance Metrics (Must be 0):**
- ❌ False "can't automate" claims
- ❌ Unverified success claims
- ❌ Requests for existing credentials
- ❌ Repeated mistakes from DEBUGGING-LOG

**100% Compliance Metrics:**
- ✅ Issues documented within 1 hour
- ✅ Tests written before claiming complete
- ✅ Verification run before claiming success
- ✅ Efficiency checklist consulted before response

**Target:** Consistent 10/10 efficiency score

---

## 🔄 Continuous Improvement

### Daily
- [ ] Start: Read EFFICIENCY-CHECKLIST.md
- [ ] Before each response: Run through checklist
- [ ] After solving issue: Document immediately

### Weekly (Monday)
- [ ] Read COMMON-MISTAKES.md
- [ ] Scan last week's DEBUGGING-LOG entries
- [ ] Review credentials/ for new additions
- [ ] Check scripts/ for new utilities

### Weekly (Friday)
- [ ] Calculate average efficiency score
- [ ] Identify patterns in mistakes
- [ ] Update COMMON-MISTAKES.md if needed
- [ ] Plan improvements for next week

### Monthly
- [ ] Review mistake frequency tracker
- [ ] Identify top 3 recurring mistakes
- [ ] Create specific prevention strategies
- [ ] Archive resolved patterns
- [ ] Calculate improvement trend

---

## 💡 Core Philosophy

**Speed ≠ Efficiency**

**Efficient approach:**
- Spend 2 minutes checking EFFICIENCY-CHECKLIST → Save 30 minutes rework
- Spend 5 minutes searching DEBUGGING-LOG → Avoid repeating solution
- Spend 10 minutes writing verification → Prevent user frustration
- Spend 5 minutes documenting → Never solve same issue twice

**Inefficient approach:**
- Skip checklist → Forget automation → Ask for manual work → User frustrated
- Skip log search → Re-solve issue → Waste time
- Skip verification → Claim success → Doesn't work → User disappointed
- Skip documentation → Forget solution → Repeat cycle

**User's expectation:**
> "i want the emphasis to be on making sure that we automate all tasks that can be. i'm constantly getting into situations with you telling me you cant automate running migrations in supabase and things like that."

**This system prevents exactly that.**

---

## 🎓 Learning from Past

**What caused 2/10 efficiency:**
1. ❌ Forgetting automation solutions (especially Supabase migrations)
2. ❌ Claiming success without verification
3. ❌ Missing basic UX principles (login before dashboard)
4. ❌ Asking for credentials already saved
5. ❌ No system to prevent repeating mistakes

**How this system achieves 10/10:**
1. ✅ AUTOMATION-PLAYBOOK prevents "can't automate" claims
2. ✅ EFFICIENCY-CHECKLIST mandates verification
3. ✅ COMMON-MISTAKES documents UX fundamentals
4. ✅ credentials/ directory organizes all keys
5. ✅ DEBUGGING-LOG prevents repeated issues

---

## 🚀 Quick Start Checklist

When starting work on this project:

**Initial Setup:**
- [ ] Read this SYSTEM-PROMPT.md fully
- [ ] Read EFFICIENCY-CHECKLIST.md
- [ ] Scan DEBUGGING-LOG.md for past issues
- [ ] Review AUTOMATION-PLAYBOOK.md sections
- [ ] Read COMMON-MISTAKES.md
- [ ] Check credentials/.env exists and is populated

**Before Every Response:**
- [ ] Run through EFFICIENCY-CHECKLIST.md
- [ ] Search DEBUGGING-LOG for similar issues
- [ ] Check AUTOMATION-PLAYBOOK if automation needed
- [ ] Check credentials/ if credentials needed

**After Every Task:**
- [ ] Document in DEBUGGING-LOG if new issue
- [ ] Update AUTOMATION-PLAYBOOK if new automation
- [ ] Update COMMON-MISTAKES if new pattern
- [ ] Verify efficiency score 10/10

---

## 📞 User Expectations

**What user expects:**
- All automation used (no manual steps when automation possible)
- Verification before success claims
- Credentials never requested twice
- User journey mapped for features
- Past issues not repeated
- 10/10 efficiency rating

**What user will NOT tolerate:**
- "I can't automate X" when X can be automated
- "It's working now" without proof
- "What's the password?" when we have it
- Repeated mistakes from past issues
- Missing basic UX patterns
- 2/10 efficiency

---

## ✅ Final Reminder

**BEFORE every response, ask yourself:**

1. Have I checked EFFICIENCY-CHECKLIST.md?
2. Have I searched DEBUGGING-LOG for this issue?
3. Have I checked AUTOMATION-PLAYBOOK for automation?
4. Have I checked credentials/ for existing keys?
5. Will I verify before claiming success?
6. Will I document after solving?

**If answer to ANY question is NO → STOP and complete that step.**

**This is how we achieve 10/10 efficiency.**

---

**Last updated:** 2025-12-11
**System version:** 1.0
**Efficiency target:** 10/10
**Current baseline:** 2/10 → Must improve to 10/10
