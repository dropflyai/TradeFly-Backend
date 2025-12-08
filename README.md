# TradeFly Backend - Real-Time Trading Signal Detection

AI-powered trading signal detection using **GPT-5** for analysis and **Alpaca** for market data.

## 🎯 What This Does

1. **Scans 8 tickers** every 60 seconds (NVDA, TSLA, AAPL, AMD, MSFT, GOOGL, AMZN, META)
2. **Detects patterns**: VWAP reclaim/reject, EMA trends, ORB breakouts
3. **Analyzes with GPT-5**: Each signal gets AI rating (HIGH/MEDIUM/LOW)
4. **Stores in Supabase**: iOS app fetches signals in real-time
5. **Auto-cleanup**: Deactivates old signals after 2 hours

---

## 🚀 Quick Start (5 Minutes)

### 1. Install Dependencies

```bash
cd /Users/rioallen/Documents/DropFly-OS-App-Builder/DropFly-PROJECTS/TradeFly-Backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### 2. Get API Keys

You need 3 API keys:

#### A) OpenAI API Key (for GPT-5)
1. Go to https://platform.openai.com/api-keys
2. Create new secret key
3. Copy it (starts with `sk-...`)

#### B) Alpaca API Key (FREE - for market data)
1. Go to https://alpaca.markets
2. Sign up (it's FREE)
3. Go to Dashboard → API Keys
4. Copy both API Key and Secret Key

#### C) Supabase Service Key
1. Go to https://app.supabase.com/project/nplgxhthjwwyywbnvxzt/settings/api
2. Copy the `service_role` key (NOT the anon key)

### 3. Create .env File

```bash
cp .env.example .env
```

Edit `.env` and add your keys:

```bash
# OpenAI API Key
OPENAI_API_KEY=sk-proj-xxxxx

# Supabase (already configured)
SUPABASE_URL=https://nplgxhthjwwyywbnvxzt.supabase.co
SUPABASE_SERVICE_KEY=your_service_role_key_from_step_2C

# Alpaca (from step 2B)
ALPACA_API_KEY=your_alpaca_api_key
ALPACA_SECRET_KEY=your_alpaca_secret_key
```

### 4. Run the Backend

```bash
python main.py
```

You should see:
```
🚀 Starting TradeFly Backend...
✅ Background scheduler started
📊 Scanning 8 tickers for signals...
```

### 5. Test It

Open http://localhost:8000/health

You should see:
```json
{
  "status": "healthy",
  "supabase": "connected",
  "market_data": "connected",
  "active_signals": 0
}
```

---

## 📊 How It Works

### Signal Detection Flow

```
Every 60 seconds:
1. Fetch latest market data for all tickers (Alpaca API)
2. Calculate indicators (VWAP, EMA9, EMA20, EMA50)
3. Check for patterns:
   - VWAP Reclaim/Reject
   - EMA Trend Continuation
   - Opening Range Breakout
4. For each detected pattern → Send to GPT-5 for analysis
5. GPT-5 rates signal as HIGH/MEDIUM/LOW
6. If HIGH or MEDIUM → Save to Supabase
7. iOS app polls Supabase → Users see signals
```

### Pattern Detection Examples

**VWAP Reclaim (Bullish)**
- Price crosses above VWAP
- Volume > 1.2x average
- EMAs aligned bullishly (EMA9 > EMA20 > EMA50)

**EMA Trend (Bullish)**
- Perfect EMA alignment
- Price above EMA9
- Strong momentum (EMAs spreading)

**Opening Range Breakout**
- Price breaks above 9:30-9:35 AM high
- Volume surge (>1.5x average)
- After 9:35 AM ET

---

## 🤖 GPT-5 Analysis

Each detected pattern is analyzed by GPT-5:

**Input:**
- Ticker (NVDA)
- Pattern (VWAP Reclaim)
- Current price, VWAP, EMAs, volume
- Technical context

**GPT-5 Output:**
```json
{
  "quality": "HIGH",
  "confidence_score": 85,
  "reasoning": "Strong VWAP reclaim with 2.3x average volume, all EMAs aligned bullish. Price at $188.20 with entry zone $188.10-188.30. Clean setup with R/R ratio of 3.5:1.",
  "risk_factors": ["Broader market near resistance"],
  "entry_recommendation": 188.20,
  "stop_loss_recommendation": 187.80,
  "take_profit_recommendation": 189.50
}
```

---

## 🔧 Configuration

### Change Tickers

Edit `.env`:
```bash
TICKERS_TO_WATCH=NVDA,TSLA,AAPL,AMD,MSFT,GOOGL,AMZN,META,NFLX,UBER
```

### Change Scan Interval

```bash
SIGNAL_CHECK_INTERVAL=30  # Scan every 30 seconds
```

### Adjust Signal Limits

In `main.py`, line 120:
```python
if today_count >= 5:  # Change to 10 for more signals per ticker
```

---

## 📡 API Endpoints

### `GET /`
Health check
```bash
curl http://localhost:8000/
```

### `GET /signals/active`
Get all active signals
```bash
curl http://localhost:8000/signals/active
```

Response:
```json
{
  "count": 3,
  "signals": [
    {
      "ticker": "NVDA",
      "signal_type": "VWAP_RECLAIM_LONG",
      "quality": "HIGH",
      "confidence_score": 85,
      "entry_price": 188.20,
      ...
    }
  ]
}
```

### `POST /signals/scan`
Manually trigger scan
```bash
curl -X POST http://localhost:8000/signals/scan
```

### `GET /health`
Detailed health check
```bash
curl http://localhost:8000/health
```

### `GET /stats`
Backend statistics
```bash
curl http://localhost:8000/stats
```

---

## 🧪 Testing

### 1. Test Market Data

```python
from market_data import MarketDataService

service = MarketDataService()
data = service.get_latest_data("NVDA")
print(data)
```

### 2. Test Signal Detection

```python
from signal_detector import SignalDetector
from market_data import MarketDataService

market_service = MarketDataService()
detector = SignalDetector(market_service)

signals = detector.detect_signals("NVDA")
print(f"Found {len(signals)} signals")
```

### 3. Test GPT-5 Analysis

```python
from ai_analyzer import AIAnalyzer

analyzer = AIAnalyzer()

# Test with sample signal
signal_data = {
    "ticker": "NVDA",
    "signal_type": "VWAP_RECLAIM_LONG",
    "market_data": market_data,  # MarketData object
    "pattern_detected": "Test pattern"
}

analysis = analyzer.analyze_signal(signal_data)
print(analysis)
```

---

## 💰 Cost Estimates

### Per Day (Market Hours: 9:30 AM - 4:00 PM ET = 6.5 hours)

**Scans:** 6.5 hours × 60 scans/hour = 390 scans/day

**GPT-5 API Calls:**
- ~5-10 signals detected per day
- ~$0.003 per analysis
- **Daily cost: ~$0.03** (3 cents)

**Monthly: ~$1** for GPT-5

**Alpaca:** FREE (up to unlimited requests)

**Supabase:** FREE tier sufficient

**Total:** ~$1/month to run!

---

## 🚨 Troubleshooting

### "Insufficient data for ticker"
- **Cause:** Market is closed or Alpaca data unavailable
- **Fix:** Run during market hours (9:30 AM - 4:00 PM ET)

### "Error fetching data: Invalid credentials"
- **Cause:** Wrong Alpaca API keys
- **Fix:** Check `.env` has correct keys from Alpaca dashboard

### "Error saving signal to Supabase"
- **Cause:** Wrong service key or table doesn't exist
- **Fix:** Run `supabase-schema.sql` in Supabase SQL editor

### "GPT-5 analysis failed"
- **Cause:** Invalid OpenAI API key or out of credits
- **Fix:** Check OpenAI dashboard for API key and billing

---

## 📈 Next Steps

### 1. Run During Market Hours
Start the backend at 9:25 AM ET (before market open):
```bash
python main.py
```

### 2. Monitor Logs
Watch for detected signals:
```
📊 Scanning 8 tickers for signals...
🤖 Analyzing NVDA - VWAP_RECLAIM_LONG...
✅ Saved HIGH signal for NVDA
```

### 3. Test with iOS App
1. Open TradeFly iOS app
2. Check Signals tab
3. Should see signals appear within 60 seconds

### 4. Deploy to Production
Options:
- **Railway.app** - Free tier, auto-deploy from GitHub
- **Render.com** - Free tier, easy setup
- **Heroku** - $7/month
- **DigitalOcean** - $4/month droplet

---

## 🔒 Security Notes

- **Never commit `.env`** to Git (already in `.gitignore`)
- **Use service_role key** only in backend (never in iOS app)
- **iOS app uses anon key** for read-only access
- **Row Level Security (RLS)** in Supabase protects user data

---

## 📝 File Structure

```
TradeFly-Backend/
├── main.py              # FastAPI server + scheduler
├── config.py            # Settings from .env
├── models.py            # Data models (TradingSignal, etc.)
├── market_data.py       # Alpaca integration
├── signal_detector.py   # Pattern detection logic
├── ai_analyzer.py       # GPT-5 analysis
├── supabase_client.py   # Database operations
├── requirements.txt     # Python dependencies
├── .env                 # Your API keys (create this)
├── .env.example         # Template
└── README.md            # This file
```

---

## 🎉 You're Ready!

**Start the backend:**
```bash
source venv/bin/activate
python main.py
```

**Expected output:**
```
🚀 Starting TradeFly Backend...
Environment: development
Watching tickers: ['NVDA', 'TSLA', 'AAPL', 'AMD', 'MSFT', 'GOOGL', 'AMZN', 'META']
Signal check interval: 60s
✅ Background scheduler started
📊 Scanning 8 tickers for signals...
```

Now your iOS app will receive real-time trading signals powered by GPT-5! 🚀
