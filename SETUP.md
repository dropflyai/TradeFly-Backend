# TradeFly Backend - 5-Minute Setup Guide

## ⚠️ SKIP ALPACA VERIFICATION!

**Having trouble with Alpaca asking for business info?**
→ Use Yahoo Finance instead (FREE, no signup needed)

---

## Step 1: Get Your API Keys (2 minutes)

### A) OpenAI API Key (REQUIRED)
1. Go to: https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Copy the key (starts with `sk-proj-...`)
4. **Cost:** ~$60/month for TradeFly usage

### B) Market Data: Choose ONE Option

**Option 1: Yahoo Finance (RECOMMENDED - No signup!)**
- ✅ FREE forever
- ✅ No verification
- ✅ Works immediately
- ✅ Perfect for development
- ❌ 1-2 second delay (doesn't matter for 60-sec scans)

**Option 2: Alpaca (Skip if signup is annoying)**
- Requires email signup
- Keeps pushing business verification (confusing!)
- Not worth the hassle right now

**→ Use Yahoo Finance!**

### C) Supabase Service Key (REQUIRED)
1. Already set up for you!
2. URL: `https://nplgxhthjwwyywbnvxzt.supabase.co`
3. Go to: https://app.supabase.com/project/nplgxhthjwwyywbnvxzt/settings/api
4. Copy the `service_role` key (the long one, NOT anon)

---

## Step 2: Install and Configure (2 minutes)

```bash
# Navigate to backend
cd /Users/rioallen/Documents/DropFly-OS-App-Builder/DropFly-PROJECTS/TradeFly-Backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
```

Now edit `.env`:
```bash
nano .env
```

Paste your keys:
```bash
# OpenAI (REQUIRED)
OPENAI_API_KEY=sk-proj-YOUR_KEY_HERE

# Supabase (REQUIRED)
SUPABASE_URL=https://nplgxhthjwwyywbnvxzt.supabase.co
SUPABASE_SERVICE_KEY=YOUR_SERVICE_ROLE_KEY_HERE

# Market Data: Yahoo Finance (FREE, no signup!)
USE_YAHOO_FINANCE=true

# If using Alpaca instead (optional):
# ALPACA_API_KEY=YOUR_KEY
# ALPACA_SECRET_KEY=YOUR_SECRET

# App Settings
ENVIRONMENT=development
LOG_LEVEL=INFO
SIGNAL_CHECK_INTERVAL=60
TICKERS_TO_WATCH=NVDA,TSLA,AAPL,AMD,MSFT,GOOGL,AMZN,META
```

Save and exit (Ctrl+O, Enter, Ctrl+X)

---

## Step 3: Run It! (30 seconds)

```bash
python main.py
```

You should see:
```
🚀 Starting TradeFly Backend...
Environment: development
Watching tickers: ['NVDA', 'TSLA', 'AAPL', 'AMD', 'MSFT', 'GOOGL', 'AMZN', 'META']
✅ Background scheduler started
📊 Scanning 8 tickers for signals...
```

---

## Step 4: Test It

Open a new terminal:
```bash
# Test health
curl http://localhost:8000/health

# Trigger manual scan
curl -X POST http://localhost:8000/signals/scan

# Check for signals
curl http://localhost:8000/signals/active
```

---

## ✅ You're Done!

The backend is now:
- ✅ Scanning 8 tickers every 60 seconds
- ✅ Detecting VWAP, EMA, and ORB patterns
- ✅ Using GPT-5 to analyze each signal
- ✅ Storing HIGH/MEDIUM signals in Supabase
- ✅ Your iOS app can fetch them in real-time

---

## 🚨 Troubleshooting

### "ModuleNotFoundError: No module named 'fastapi'"
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### "Market data unavailable"
- Alpaca only provides data during market hours (9:30 AM - 4:00 PM ET)
- Test during trading hours or use paper trading mode

### "Error saving to Supabase"
- Check your service_role key (not anon key!)
- Make sure you ran the SQL schema in Supabase

### "GPT-5 analysis failed"
- Check OpenAI API key is correct
- Verify you have credits: https://platform.openai.com/usage

---

## 🎯 Next Steps

1. **Run during market hours** (9:30 AM - 4:00 PM ET)
2. **Monitor logs** - watch for HIGH quality signals
3. **Test with iOS app** - signals should appear automatically
4. **Deploy to cloud** - Railway, Render, or Heroku for 24/7 operation

---

## 💡 Pro Tips

**For testing RIGHT NOW (even after hours):**

You can modify `main.py` to use sample data for testing:
```python
# In scan_for_signals(), add this at the top:
if settings.environment == "development":
    # Create fake signal for testing
    from datetime import datetime
    from models import TradingSignal, SignalType, SignalQuality

    test_signal = TradingSignal(
        ticker="NVDA",
        signal_type=SignalType.VWAP_RECLAIM_LONG,
        quality=SignalQuality.HIGH,
        timestamp=datetime.now(),
        current_price=188.50,
        entry_price=188.30,
        stop_loss=187.80,
        take_profit_1=189.50,
        vwap=188.00,
        ema9=188.20,
        ema20=187.90,
        ema50=187.50,
        volume=1500000,
        avg_volume=1200000,
        ai_reasoning="Test signal for development",
        confidence_score=85,
        risk_factors=["This is a test"]
    )
    supabase.save_signal(test_signal)
    return  # Skip real scanning
```

This lets you test the full flow even when markets are closed!

---

Ready to trade! 🚀
