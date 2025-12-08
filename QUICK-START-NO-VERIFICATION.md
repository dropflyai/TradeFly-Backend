# 🚀 Quick Start (No Verification Required)

## Problem

Alpaca wants business verification → Too complicated!

## Solution

Use **Yahoo Finance** instead → 100% FREE, no signup, no API keys!

---

## ✅ Simple 3-Step Setup

### 1. Install Dependencies

```bash
cd /path/to/TradeFly-Backend
pip install -r requirements.txt
```

This now includes `yfinance` (Yahoo Finance library).

### 2. Update Your .env File

```bash
# .env

# OpenAI (REQUIRED - for GPT-5 signal analysis)
OPENAI_API_KEY=your_openai_key_here

# Supabase (REQUIRED - for database)
SUPABASE_URL=https://nplgxhthjwwyywbnvxzt.supabase.co
SUPABASE_SERVICE_KEY=your_supabase_key_here

# Market Data - CHOOSE ONE:

# Option 1: Yahoo Finance (FREE, no signup)
USE_YAHOO_FINANCE=true

# Option 2: Alpaca (if you have keys)
# ALPACA_API_KEY=your_key
# ALPACA_SECRET_KEY=your_secret

# News APIs (OPTIONAL)
# BENZINGA_API_KEY=
# NEWS_API_KEY=

# App Settings
ENVIRONMENT=development
LOG_LEVEL=INFO
SIGNAL_CHECK_INTERVAL=60
TICKERS_TO_WATCH=NVDA,TSLA,AAPL,AMD,MSFT,GOOGL,AMZN,META
```

### 3. Update main.py to Use Yahoo Finance

At the top of `main.py`, change:

```python
# OLD:
from market_data import MarketDataService

# NEW:
from market_data_yahoo import YahooMarketDataService as MarketDataService
```

That's it! No verification, no signup, 100% free.

---

## 🎯 What Each Service Costs

| Service | Cost | Verification Required | Used For |
|---------|------|----------------------|----------|
| **Yahoo Finance** | FREE | ❌ No | Market data (OHLCV) |
| Alpaca | FREE | ❌ No (data only) | Market data (alternative) |
| Polygon.io | FREE | ❌ No | Market data (alternative) |
| **OpenAI GPT-5** | ~$2/day | ❌ No | Signal analysis (REQUIRED) |
| **Supabase** | FREE | ❌ No | Database (REQUIRED) |
| Benzinga | $99/mo | ❌ No | News (optional) |
| NewsAPI | $49/mo | ❌ No | News (optional) |

---

## 🔑 Only 2 Keys Actually Required

### 1. OpenAI API Key (REQUIRED)

**What it does:** Analyzes signals with GPT-5
**Cost:** ~$2/day ($60/month) for moderate usage
**Sign up:** https://platform.openai.com/api-keys

```bash
# Get key:
1. Go to https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Copy key (starts with sk-...)
4. Add to .env:
   OPENAI_API_KEY=sk-...
```

### 2. Supabase Keys (REQUIRED)

**What it does:** Stores signals in PostgreSQL database
**Cost:** FREE (up to 500MB database)
**Sign up:** https://supabase.com

```bash
# Get keys:
1. Go to https://supabase.com/dashboard
2. Create new project
3. Go to Settings → API
4. Copy URL and service_role key
5. Add to .env:
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_SERVICE_KEY=eyJ...
```

---

## 🏃 Run TradeFly

```bash
# Install dependencies
pip install -r requirements.txt

# Run backend
python main.py

# Should see:
# 🚀 Starting TradeFly Backend...
# Environment: development
# Watching tickers: ['NVDA', 'TSLA', 'AAPL', ...]
# ✅ Background scheduler started
# ✅ Yahoo Finance data service initialized (FREE)
# 📊 Scanning 8 tickers for signals...
```

---

## 📊 Yahoo Finance vs Alpaca

| Feature | Yahoo Finance | Alpaca |
|---------|--------------|--------|
| **Cost** | FREE | FREE |
| **Signup** | ❌ No | ❌ No (data only) |
| **Verification** | ❌ No | ❌ No (data only) |
| **API Key** | ❌ Not needed | ✅ Needed |
| **Rate Limits** | 2000 requests/hour | Unlimited |
| **Data Quality** | ⭐⭐⭐⭐ Good | ⭐⭐⭐⭐⭐ Excellent |
| **Latency** | ~1-2 seconds | <500ms |
| **Best For** | Development, Testing | Production |

**Recommendation:**
- **Development:** Use Yahoo Finance (easier setup)
- **Production:** Use Alpaca (better data)

---

## 🔄 Switching from Yahoo to Alpaca Later

When you're ready for production:

1. Get Alpaca data-only API keys (no verification):
   - https://alpaca.markets/data
   - Just email signup

2. Add keys to `.env`:
   ```bash
   ALPACA_API_KEY=your_key
   ALPACA_SECRET_KEY=your_secret
   ```

3. Update `main.py`:
   ```python
   # Change from:
   from market_data_yahoo import YahooMarketDataService as MarketDataService

   # Back to:
   from market_data import MarketDataService
   ```

4. Restart backend:
   ```bash
   python main.py
   ```

Done! No code changes needed, just swap the import.

---

## ❓ FAQ

### Q: Is Yahoo Finance reliable?
**A:** Yes! Used by millions. Slight delay (~1-2 seconds) vs real-time, but perfect for development.

### Q: Will signals work with Yahoo Finance?
**A:** Yes! All patterns (VWAP, EMA, ORB) work exactly the same.

### Q: What about options data?
**A:** Yahoo Finance has options, but if you need advanced options data, use Alpaca or Polygon.

### Q: Can I use Yahoo in production?
**A:** Yes, but Alpaca is better (faster, more reliable). Yahoo is perfect for development/testing.

### Q: Does this affect win rates?
**A:** No! Data is the same, just from different sources.

---

## ✅ Complete Setup Checklist

- [ ] Install Python dependencies: `pip install -r requirements.txt`
- [ ] Get OpenAI API key (https://platform.openai.com/api-keys)
- [ ] Get Supabase keys (https://supabase.com/dashboard)
- [ ] Update `.env` file with keys
- [ ] Set `USE_YAHOO_FINANCE=true` in `.env`
- [ ] Change `main.py` import to `market_data_yahoo`
- [ ] Run database migration: `supabase-add-news-columns.sql`
- [ ] Start backend: `python main.py`
- [ ] Test: `curl http://localhost:8000/health`
- [ ] Check for signals: `curl http://localhost:8000/signals/active`

---

## 🎉 Summary

**Before:** Alpaca wants verification → Too complicated!

**After:** Yahoo Finance → No verification, no API keys, works immediately!

**Required:**
1. OpenAI key (~$60/month)
2. Supabase keys (FREE)
3. That's it!

**Optional:**
- News APIs (Benzinga/NewsAPI) - for better signals
- Alpaca keys (for production) - better data quality

**Result:** TradeFly works perfectly with minimal setup! 🚀
