# Credentials Directory

**Purpose:** Central storage for ALL project credentials and API keys

**Last Updated:** 2025-12-11

---

## 🔐 Security Rules

1. **NEVER commit `.env` to git** - Already in .gitignore
2. **ALWAYS use `.env.template` for structure** - Commit this, not actual values
3. **ROTATE credentials regularly** - Especially after team changes
4. **ONE source of truth** - All credentials in this directory

---

## 📁 Directory Structure

```
credentials/
├── .env                    # PRIMARY: All credentials (DO NOT COMMIT)
├── .env.template           # Template with placeholders (SAFE TO COMMIT)
├── README.md               # This file
└── services/               # Service-specific credentials (optional)
    ├── supabase.env        # Supabase credentials
    ├── vercel.env          # Vercel credentials
    ├── aws.env             # AWS credentials
    └── apis.env            # Third-party API keys
```

---

## 🚀 Quick Start

### For New Projects

1. **Copy template to actual file:**
   ```bash
   cp credentials/.env.template credentials/.env
   ```

2. **Fill in actual values:**
   - Open `credentials/.env` in editor
   - Replace all `your_*_here` placeholders with real values
   - Save and close

3. **Verify .gitignore:**
   ```bash
   # Should show .env in .gitignore
   grep ".env" .gitignore
   ```

4. **Test loading:**
   ```bash
   # Load environment variables
   export $(grep -v '^#' credentials/.env | xargs)

   # Verify
   echo $SUPABASE_URL
   ```

---

## 📋 Credential Checklist

When setting up new project, ensure you have:

### Required for Most Projects
- [ ] Supabase URL and keys
- [ ] Supabase database password
- [ ] Vercel token (if deploying to Vercel)
- [ ] GitHub token (for CI/CD)

### Optional Based on Project
- [ ] AWS credentials (if using EC2/S3)
- [ ] Third-party API keys (Polygon, OpenAI, etc.)
- [ ] Payment processing (Stripe)
- [ ] Communication (SendGrid, Twilio)

---

## 🔍 Finding Credentials

### Supabase
1. Go to https://supabase.com/dashboard
2. Select your project
3. **Settings → API** for URL and keys
4. **Settings → Database** for DB password

### Vercel
1. Go to https://vercel.com/account/tokens
2. Create new token or use existing
3. Copy token to `.env`

**For org/team ID:**
```bash
# List projects (will show org/team ID)
npx vercel ls
```

### AWS
1. Go to https://console.aws.amazon.com/iam/
2. **Users → Security credentials**
3. Create access key
4. **IMPORTANT:** Download immediately, cannot retrieve later

### GitHub
1. Go to https://github.com/settings/tokens
2. Generate new token (classic)
3. Select scopes: `repo`, `workflow`, `read:org`
4. Copy token immediately

---

## 📝 Adding New Credentials

When user provides NEW credential:

1. **Add to `.env` immediately:**
   ```bash
   echo "SERVICE_API_KEY=actual_key_value" >> credentials/.env
   ```

2. **Update `.env.template` with placeholder:**
   ```bash
   # In .env.template
   SERVICE_API_KEY=your_service_api_key_here
   ```

3. **Document in DEBUGGING-LOG:**
   ```markdown
   Added [SERVICE] credentials on [DATE]
   Location: credentials/.env
   ```

4. **Test it works:**
   ```bash
   export $(grep -v '^#' credentials/.env | xargs)
   echo $SERVICE_API_KEY
   ```

---

## 🔄 Loading Environment Variables

### Method 1: Export All (Bash)
```bash
export $(grep -v '^#' credentials/.env | xargs)
```

### Method 2: Source with set (Bash)
```bash
set -a
source credentials/.env
set +a
```

### Method 3: Prefix Command
```bash
env $(cat credentials/.env | xargs) npm run dev
```

### Method 4: In Scripts
```bash
#!/bin/bash
# At top of script
source ../credentials/.env
# Or
export $(grep -v '^#' ../credentials/.env | xargs)
```

### Method 5: Node.js (with dotenv)
```javascript
require('dotenv').config({ path: './credentials/.env' });
console.log(process.env.SUPABASE_URL);
```

---

## 🛠️ Service-Specific Files (Optional)

For complex projects, you may split credentials:

### credentials/services/supabase.env
```bash
SUPABASE_URL=https://yourproject.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_key
SUPABASE_DB_PASSWORD=your_password
SUPABASE_HOST=db.yourproject.supabase.co
```

### credentials/services/vercel.env
```bash
VERCEL_TOKEN=your_token
VERCEL_ORG_ID=your_org_id
VERCEL_PROJECT_ID=your_project_id
```

### credentials/services/aws.env
```bash
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-east-2
AWS_EC2_INSTANCE_ID=i-yourinstance
```

### Loading service-specific:
```bash
source credentials/services/supabase.env
source credentials/services/vercel.env
```

---

## 🚨 Common Issues

### "Permission Denied" Error
```bash
# Fix: Make credentials directory readable
chmod 700 credentials/
chmod 600 credentials/.env
```

### "Variable Not Found" Error
```bash
# Check variable exists
grep "VARIABLE_NAME" credentials/.env

# Check loaded
echo $VARIABLE_NAME

# Reload if needed
export $(grep -v '^#' credentials/.env | xargs)
```

### "Invalid Character" Error
```bash
# Ensure no spaces around =
# WRONG: API_KEY = value
# RIGHT: API_KEY=value
```

---

## 📊 Credential Audit

Run this monthly to verify credentials:

```bash
#!/bin/bash
echo "=== Credential Audit ==="

# Check .env exists
if [ -f "credentials/.env" ]; then
    echo "✅ .env file found"
else
    echo "❌ .env file missing"
fi

# Check critical credentials
REQUIRED=(
    "SUPABASE_URL"
    "SUPABASE_ANON_KEY"
    "SUPABASE_DB_PASSWORD"
)

for var in "${REQUIRED[@]}"; do
    if grep -q "^${var}=" credentials/.env; then
        echo "✅ $var configured"
    else
        echo "❌ $var missing"
    fi
done

# Check for placeholder values
if grep -q "your_.*_here" credentials/.env; then
    echo "⚠️  Warning: Found placeholder values in .env"
    grep "your_.*_here" credentials/.env
fi

echo "=== Audit Complete ==="
```

---

## 🔒 Security Best Practices

1. **Rotate Credentials:**
   - After team member leaves
   - Every 90 days for production
   - Immediately if exposed

2. **Use Different Credentials Per Environment:**
   - `.env` for development
   - `.env.production` for production (not in git)
   - `.env.staging` for staging (not in git)

3. **Monitor Usage:**
   - Check Supabase dashboard for unusual activity
   - Review AWS billing for unexpected charges
   - Monitor API rate limits

4. **Backup Securely:**
   - Use password manager for credential backup
   - Don't email credentials
   - Don't post in Slack/Discord

---

## 📱 Quick Reference

**Before asking "What's the X credential?":**
1. ✅ Check `credentials/.env`
2. ✅ Check `credentials/services/*.env`
3. ✅ Search `DEBUGGING-LOG.md` for "Added [SERVICE]"
4. ✅ Check backend project `.env` files

**When user provides credential:**
1. ✅ Save to `credentials/.env` immediately
2. ✅ Update `.env.template` with placeholder
3. ✅ Log in `DEBUGGING-LOG.md` with date
4. ✅ Test it works

**Loading credentials:**
```bash
# Quick load
export $(grep -v '^#' credentials/.env | xargs)

# Verify
echo $SUPABASE_URL
```

---

## ⚠️ NEVER DO THIS

❌ Commit `.env` to git
❌ Email credentials in plain text
❌ Post credentials in Slack/Discord/chat
❌ Use production credentials in development
❌ Share credentials via screenshot
❌ Store credentials in code comments
❌ Use same password for multiple services

---

## ✅ ALWAYS DO THIS

✅ Use `.env.template` for structure
✅ Store actual values in `.env` (gitignored)
✅ Use environment-specific files
✅ Rotate credentials regularly
✅ Audit credentials monthly
✅ Document when credentials added
✅ Use password manager for backup

---

**Last Updated:** 2025-12-11
**Owner:** Project Team
**Review Schedule:** Monthly
