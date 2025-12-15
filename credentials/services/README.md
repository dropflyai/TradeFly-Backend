# Service-Specific Credentials

This directory holds credentials organized by service for complex projects.

## Purpose

Some projects need many credentials. Organizing them by service makes them easier to manage.

## Structure

```
services/
├── supabase.env        # Supabase-specific credentials
├── vercel.env          # Vercel deployment credentials
├── aws.env             # AWS credentials
├── apis.env            # Third-party API keys
└── README.md           # This file
```

## Usage

### Option 1: Single .env file (Recommended for most projects)

Keep all credentials in `../credentials/.env` - simpler and works for most projects.

### Option 2: Multiple service files (For complex projects)

Create separate files for each service:

```bash
# credentials/services/supabase.env
SUPABASE_URL=...
SUPABASE_ANON_KEY=...
SUPABASE_SERVICE_KEY=...

# credentials/services/vercel.env
VERCEL_TOKEN=...
VERCEL_ORG_ID=...
```

Then load them as needed:

```bash
# Load all service credentials
export $(cat credentials/services/*.env | xargs)

# Load specific service
export $(cat credentials/services/supabase.env | xargs)
```

## Security Rules

1. **NEVER commit these files to git**
2. All files here should be in `.gitignore`
3. Create `.env.template` versions (without actual values)
4. Share templates, not actual credentials

## Git Safety

Verify `.gitignore` includes:

```
# In root .gitignore
credentials/.env
credentials/services/*.env
```

Check with:

```bash
git status --ignored
```

If any `.env` files appear as tracked, remove them:

```bash
git rm --cached credentials/services/*.env
git commit -m "Remove credential files from tracking"
```
