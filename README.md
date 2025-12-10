# TradeFly AI - Options Trading Signals Platform

Real-time options trading signals with dynamic market scanning and customizable filters.

## Features

### 🎯 Unified Signals Dashboard
- **Strategy Filters**: Scalping (0-7 DTE), Swing (14-30 DTE), Momentum, Volume Spike, LEAPs (90+ DTE)
- **Moneyness Levels**: Deep ITM, ITM, ATM, OTM, Far OTM
- **Custom Price Range**: Min/Max price inputs with quick preset buttons ($1, $5, $10, $50)
- **Delta Range**: Customizable min/max delta filters
- **Days to Expiration**: 0-3, 4-7, 7-14, 14-30, 30-60, 60-90, 90+ DTE
- **Confidence Threshold**: 50%-95% signal confidence filtering

### 🔥 Dynamic Market Scanning
- **Top Movers Scanner**: Automatically identifies gainers, losers, and most active stocks
- **Real-time Ticker**: Live scrolling feed of top market movers with prices and % changes
- **Smart Watchlist**: Scans 100+ stocks based on market movement (updates every 5 minutes)
- **Auto-Discovery**: Replaces fixed watchlists with dynamic market-wide scanning

## Quick Start

```bash
# Set environment variables
export POLYGON_API_KEY="your_massive_api_key"
export ACCOUNT_BALANCE="10000"
export PORT="8002"

# Run server
python3 main_options.py
```

Access at: **http://localhost:8002**

## API Endpoints

### Signals
- `GET /api/options/signals` - Get trading signals with filters
- `GET /api/options/top-signals` - Top-rated signals

### Market Data
- `GET /api/market/status` - Market open/closed status
- `GET /api/market/top-movers` - Top gainers, losers, actives
- `GET /api/market/dynamic-watchlist` - Dynamic stock watchlist

### Paper Trading
- `GET /api/paper/trades` - All paper trades
- `GET /api/paper/positions` - Open positions
- `GET /api/paper/stats` - Performance stats

## Architecture

```
Backend (FastAPI):
├── main_options.py          - Main API server
├── top_movers.py            - Dynamic market scanner
├── massive_options_api.py   - Options data (Massive + yfinance)
├── options_strategies.py    - Signal algorithms
└── market_hours.py          - Market hours detection

Frontend (SPA):
├── static/pages/signals.html - Unified signals dashboard
├── static/js/app.js          - Router & init
└── static/components/        - Reusable components
```

## Signal Strategies

### Scalping (0-7 DTE)
- Target: 10-20% gains in 1-5 minutes
- Delta: 0.20-0.99
- Volume: 10+ contracts
- Max price: <$50
- Confidence: 70-85%

### Swing Trading (14-30 DTE)
- Target: 2-10x returns over 1-3 weeks
- Focus: Cheaper options with explosive potential
- Risk: 15% stop loss

## Data Sources

1. **Massive API** (formerly Polygon.io) - Primary options data
2. **yfinance** - Free fallback for options chains and historical data
3. **Yahoo Finance** - Market movers scanner (gainers/losers/actives)

## Technical Indicators

- RSI (14-period) - Overbought/oversold
- MACD - Trend strength
- Bollinger Bands - Volatility
- VWAP - Volume-weighted price
- Support/Resistance levels

---

**⚠️ Disclaimer**: Educational purposes only. Options trading involves substantial risk of loss.
