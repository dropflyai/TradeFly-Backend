"""
TradeFly Backend - FastAPI Server
Real-time trading signal detection with GPT-5 analysis
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import uvicorn

from config import settings

# Configure logging FIRST
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Auto-detect market data provider
if settings.polygon_api_key and not settings.use_yahoo_finance:
    from market_data_polygon import PolygonMarketDataService
    logger.info("📊 Using Massive (Real-time accurate data)")
    market_service = PolygonMarketDataService(settings.polygon_api_key)
elif settings.use_yahoo_finance:
    from market_data_yahoo import YahooMarketDataService
    logger.info("📊 Using Yahoo Finance (FREE, no API keys needed)")
    market_service = YahooMarketDataService()
else:
    from market_data import MarketDataService
    logger.info("📊 Using Alpaca Market Data")
    market_service = MarketDataService()

from signal_detector import SignalDetector
from ai_analyzer import AIAnalyzer
from supabase_client import SupabaseClient
from news_service import NewsService
from models import TradingSignal, SignalType, SignalQuality, AssetType, detect_asset_type, GPT5AnalysisResponse

# Global services (market_service already initialized above based on provider)
news_service = NewsService()  # News & catalyst monitoring
detector = SignalDetector(market_service)
ai_analyzer = AIAnalyzer(market_service, news_service)  # Now includes news analysis
supabase = SupabaseClient()
scheduler = BackgroundScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    logger.info("🚀 Starting TradeFly Backend...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Watching tickers: {settings.tickers_list}")
    logger.info(f"Signal check interval: {settings.signal_check_interval}s")

    # Start background scheduler (with async support)
    import asyncio

    def run_scan():
        """Wrapper to run async scan_for_signals in sync context"""
        asyncio.run(scan_for_signals())

    scheduler.add_job(
        func=run_scan,
        trigger=IntervalTrigger(seconds=settings.signal_check_interval),
        id='signal_scanner',
        name='Scan for trading signals',
        replace_existing=True
    )

    # Cleanup old signals every 30 minutes
    scheduler.add_job(
        func=cleanup_old_signals,
        trigger=IntervalTrigger(minutes=30),
        id='cleanup',
        name='Cleanup old signals',
        replace_existing=True
    )

    scheduler.start()
    logger.info("✅ Background scheduler started")

    # Run initial scan (use await since we're already in async context)
    await scan_for_signals()

    yield

    # Shutdown
    logger.info("🛑 Shutting down TradeFly Backend...")
    scheduler.shutdown()
    logger.info("✅ Scheduler stopped")


app = FastAPI(
    title="TradeFly Backend API",
    description="Real-time trading signal detection with GPT-5 AI analysis",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your iOS app domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def scan_for_signals():
    """
    Main signal scanning function - runs on schedule
    Detects patterns and uses GPT-5 to analyze them (now with news)
    """
    try:
        logger.info(f"📊 Scanning {len(settings.tickers_list)} tickers for signals...")

        signals_found = 0

        for ticker in settings.tickers_list:
            # Check if we already have signals for this ticker today
            today_count = supabase.get_signal_count_today(ticker)
            if today_count >= 5:  # Limit to 5 signals per ticker per day
                logger.debug(f"Skipping {ticker} - already has {today_count} signals today")
                continue

            # Detect patterns
            detected_signals = detector.detect_signals(ticker)

            for signal_data in detected_signals:
                asset_type = detect_asset_type(ticker)

                # TEMP: Bypass AI for crypto until GPT-5 access is enabled
                if asset_type == AssetType.CRYPTO:
                    logger.info(f"💰 CRYPTO SIGNAL DETECTED: {ticker} - {signal_data['signal_type']} (bypassing AI)")
                    should_save = True
                    # Create dummy analysis for crypto
                    analysis = GPT5AnalysisResponse(
                        quality=SignalQuality.MEDIUM,
                        confidence_score=75,
                        reasoning=f"Crypto signal detected: {signal_data['pattern_detected']}",
                        risk_factors=["Crypto volatility"],
                        entry_recommendation=signal_data['market_data'].price,
                        stop_loss_recommendation=signal_data['market_data'].price * 0.98,
                        take_profit_recommendation=signal_data['market_data'].price * 1.02
                    )
                else:
                    # For stocks: Use GPT-5 AI analysis
                    logger.info(f"🤖 Analyzing {ticker} - {signal_data['signal_type']}...")
                    analysis = await ai_analyzer.analyze_signal(signal_data)
                    should_save = analysis.quality in [SignalQuality.HIGH, SignalQuality.MEDIUM]

                if should_save:
                    # Create TradingSignal object
                    data = signal_data['market_data']
                    avg_volume = market_service.get_average_volume(ticker)

                    # Fetch news for this signal (to display in app)
                    stock_news = await news_service.get_stock_news(ticker, hours_back=2)
                    market_news = await news_service.get_market_news(hours_back=4)

                    trading_signal = TradingSignal(
                        ticker=ticker,
                        asset_type=detect_asset_type(ticker),
                        signal_type=SignalType(signal_data['signal_type']),
                        quality=analysis.quality,
                        timestamp=data.timestamp,
                        current_price=data.price,
                        entry_price=analysis.entry_recommendation,
                        stop_loss=analysis.stop_loss_recommendation,
                        take_profit_1=analysis.take_profit_recommendation,
                        vwap=data.vwap,
                        ema9=data.ema9,
                        ema20=data.ema20,
                        ema50=data.ema50,
                        volume=data.volume,
                        avg_volume=avg_volume if avg_volume > 0 else data.volume,
                        ai_reasoning=analysis.reasoning,
                        confidence_score=analysis.confidence_score,
                        risk_factors=analysis.risk_factors,
                        related_news=stock_news[:3],  # Top 3 most relevant news
                        market_news=market_news[:2],  # Top 2 market-wide news
                        timeframe="1min",
                        is_active=True
                    )

                    # Save to Supabase
                    if supabase.save_signal(trading_signal):
                        signals_found += 1
                        logger.info(f"✅ Saved {analysis.quality.value} signal for {ticker}")
                else:
                    logger.info(f"⚠️  Skipped LOW quality signal for {ticker}")

        # Clean up duplicates
        supabase.delete_duplicate_signals()

        logger.info(f"📈 Scan complete. Found {signals_found} new signals")

    except Exception as e:
        logger.error(f"❌ Error in signal scan: {e}", exc_info=True)


def cleanup_old_signals():
    """Cleanup old signals - runs every 30 minutes"""
    try:
        logger.info("🧹 Cleaning up old signals...")
        supabase.deactivate_old_signals(hours_old=2)
    except Exception as e:
        logger.error(f"Error in cleanup: {e}")


# API Routes

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "TradeFly Backend",
        "version": "1.0.0",
        "environment": settings.environment
    }


@app.get("/signals/active")
async def get_active_signals():
    """Get all active trading signals"""
    try:
        signals = supabase.get_active_signals()
        return {
            "count": len(signals),
            "signals": signals
        }
    except Exception as e:
        logger.error(f"Error fetching signals: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/signals/scan")
async def trigger_scan():
    """Manually trigger a signal scan"""
    try:
        await scan_for_signals()
        return {"status": "success", "message": "Signal scan triggered"}
    except Exception as e:
        logger.error(f"Error triggering scan: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/market-status")
async def get_market_status():
    """Get current market status and major indices"""
    try:
        from datetime import datetime, time
        import pytz

        # Get current time in Eastern Time (US markets)
        eastern = pytz.timezone('US/Eastern')
        now = datetime.now(eastern)
        current_time = now.time()

        # Market hours (NYSE/NASDAQ)
        pre_market_start = time(4, 0)   # 4:00 AM ET
        market_open = time(9, 30)        # 9:30 AM ET
        market_close = time(16, 0)       # 4:00 PM ET
        after_hours_end = time(20, 0)    # 8:00 PM ET

        # Determine market status
        is_weekend = now.weekday() >= 5  # Saturday=5, Sunday=6

        if is_weekend:
            status = "closed"
            status_text = "Markets Closed (Weekend)"
            next_change = None
        elif current_time < pre_market_start:
            status = "closed"
            status_text = "Pre-Market Opens"
            next_change = datetime.combine(now.date(), pre_market_start, eastern).isoformat()
        elif current_time < market_open:
            status = "pre_market"
            status_text = "Pre-Market • Opens"
            next_change = datetime.combine(now.date(), market_open, eastern).isoformat()
        elif current_time < market_close:
            status = "open"
            status_text = "Markets Open • Closes"
            next_change = datetime.combine(now.date(), market_close, eastern).isoformat()
        elif current_time < after_hours_end:
            status = "after_hours"
            status_text = "After Hours • Ends"
            next_change = datetime.combine(now.date(), after_hours_end, eastern).isoformat()
        else:
            status = "closed"
            status_text = "Markets Closed"
            # Next change is pre-market tomorrow
            from datetime import timedelta
            tomorrow = now + timedelta(days=1)
            next_change = datetime.combine(tomorrow.date(), pre_market_start, eastern).isoformat()

        # Get index prices (SPY, QQQ, BTC)
        indices = {}
        try:
            spy_data = market_service.get_latest_data("SPY")
            if spy_data:
                spy_prev_close = spy_data.get('prev_close', spy_data.get('close', 0))
                spy_current = spy_data.get('close', 0)
                spy_change = ((spy_current - spy_prev_close) / spy_prev_close * 100) if spy_prev_close else 0
                indices['SPY'] = {
                    "price": spy_current,
                    "change_percent": round(spy_change, 2)
                }
        except:
            indices['SPY'] = {"price": 0, "change_percent": 0}

        try:
            qqq_data = market_service.get_latest_data("QQQ")
            if qqq_data:
                qqq_prev_close = qqq_data.get('prev_close', qqq_data.get('close', 0))
                qqq_current = qqq_data.get('close', 0)
                qqq_change = ((qqq_current - qqq_prev_close) / qqq_prev_close * 100) if qqq_prev_close else 0
                indices['QQQ'] = {
                    "price": qqq_current,
                    "change_percent": round(qqq_change, 2)
                }
        except:
            indices['QQQ'] = {"price": 0, "change_percent": 0}

        try:
            btc_data = market_service.get_latest_data("BTC-USD")
            if btc_data:
                btc_prev_close = btc_data.get('prev_close', btc_data.get('close', 0))
                btc_current = btc_data.get('close', 0)
                btc_change = ((btc_current - btc_prev_close) / btc_prev_close * 100) if btc_prev_close else 0
                indices['BTC'] = {
                    "price": btc_current,
                    "change_percent": round(btc_change, 2)
                }
        except:
            indices['BTC'] = {"price": 0, "change_percent": 0}

        return {
            "status": status,
            "status_text": status_text,
            "is_open": status == "open",
            "next_change": next_change,
            "indices": indices,
            "timestamp": now.isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting market status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Detailed health check"""
    try:
        # Test Supabase connection
        active_signals = supabase.get_active_signals()

        # Test market data
        test_data = market_service.get_latest_data(settings.tickers_list[0])

        return {
            "status": "healthy",
            "supabase": "connected",
            "market_data": "connected" if test_data else "unavailable",
            "active_signals": len(active_signals),
            "scheduler": "running" if scheduler.running else "stopped"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_stats():
    """Get backend statistics"""
    try:
        active_signals = supabase.get_active_signals()

        # Count by quality
        quality_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for signal in active_signals:
            quality_counts[signal['quality']] += 1

        return {
            "total_active_signals": len(active_signals),
            "by_quality": quality_counts,
            "tickers_watched": len(settings.tickers_list),
            "scan_interval": settings.signal_check_interval
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/news/{ticker}")
async def get_ticker_news(ticker: str, hours_back: int = 4):
    """
    Get recent news for a specific ticker
    Used by iOS app to display news in signal detail view
    """
    try:
        news = await news_service.get_stock_news(ticker, hours_back=hours_back)
        sentiment_summary = news_service.create_news_summary(ticker, news)

        return {
            "ticker": ticker,
            "news_count": len(news),
            "news": news,
            "sentiment_summary": sentiment_summary
        }
    except Exception as e:
        logger.error(f"Error fetching news for {ticker}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/news/market/latest")
async def get_market_news_endpoint(hours_back: int = 6):
    """
    Get recent market-wide news (Fed, CPI, GDP, etc.)
    Used by iOS app to display market context
    """
    try:
        news = await news_service.get_market_news(hours_back=hours_back)
        summary = news_service.create_market_news_summary(news)

        return {
            "news_count": len(news),
            "news": news,
            "summary": summary
        }
    except Exception as e:
        logger.error(f"Error fetching market news: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/price/{ticker}")
async def get_current_price(ticker: str):
    """
    Get current real-time price and basic data for a ticker
    Used by iOS app for live price updates
    """
    try:
        data = market_service.get_latest_data(ticker)
        if not data:
            raise HTTPException(status_code=404, detail=f"No data available for {ticker}")

        return {
            "ticker": ticker,
            "price": data.price,
            "timestamp": data.timestamp.isoformat(),
            "open": data.open,
            "high": data.high,
            "low": data.low,
            "volume": data.volume,
            "vwap": data.vwap,
            "ema9": data.ema9,
            "ema20": data.ema20,
            "ema50": data.ema50
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching price for {ticker}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/candles/{ticker}")
async def get_candle_data(
    ticker: str,
    interval: str = "1m",
    limit: int = 100
):
    """
    Get candlestick data for charting
    Used by iOS app for AdvancedChartView

    Args:
        ticker: Stock symbol
        interval: Time interval (1m, 5m, 15m, 1h, 1d)
        limit: Number of candles to return (default 100)
    """
    try:
        import yfinance as yf
        from datetime import datetime, timedelta

        # Map intervals to yfinance periods
        period_map = {
            "1m": "1d",
            "5m": "5d",
            "15m": "5d",
            "1h": "1mo",
            "1d": "1y"
        }

        period = period_map.get(interval, "1d")

        ticker_obj = yf.Ticker(ticker)
        hist = ticker_obj.history(period=period, interval=interval)

        if hist.empty:
            raise HTTPException(status_code=404, detail=f"No candle data available for {ticker}")

        # Convert to list of candles
        candles = []
        for timestamp, row in hist.iterrows():
            candles.append({
                "timestamp": timestamp.isoformat(),
                "open": float(row['Open']),
                "high": float(row['High']),
                "low": float(row['Low']),
                "close": float(row['Close']),
                "volume": int(row['Volume'])
            })

        # Return last 'limit' candles
        candles = candles[-limit:]

        return {
            "ticker": ticker,
            "interval": interval,
            "candle_count": len(candles),
            "candles": candles
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching candles for {ticker}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.environment == "development",
        log_level=settings.log_level.lower()
    )
