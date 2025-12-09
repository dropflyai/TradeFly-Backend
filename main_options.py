"""
TradeFly Options - Main FastAPI Application
World-Class Algorithmic Options Trading System

This is the PRODUCTION backend for institutional-grade options trading signals
"""
import logging
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from typing import List, Optional
from datetime import datetime
import os
from dotenv import load_dotenv

from options_models import OptionsSignal, StrategyType
from options_signal_detector import OptionsSignalDetector
from massive_options_api import MassiveOptionsAPI
from market_data_polygon import PolygonMarketDataService
from paper_trading import PaperTradingEngine, TradeOutcome
from backtest_engine import BacktestEngine
from position_tracker import PositionTracker, ExitSignal, ExitReason
from market_hours import MarketHours

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global instances
options_api: Optional[MassiveOptionsAPI] = None
market_data_api: Optional[PolygonMarketDataService] = None
signal_detector: Optional[OptionsSignalDetector] = None
paper_trading: Optional[PaperTradingEngine] = None
position_tracker: Optional[PositionTracker] = None

# Default watchlist - COMPREHENSIVE mix of affordable and premium stocks
DEFAULT_WATCHLIST = [
    # === AFFORDABLE STOCKS (options under $500/contract) ===
    "SOFI",   # $8-15 stock = cheap options
    "PLTR",   # $30-40 stock = affordable options
    "NIO",    # $5-10 stock = very cheap options
    "F",      # $10-15 stock = cheap options
    "BAC",    # $30-40 stock = affordable options

    # === BIG TECH (high-priced but liquid) ===
    "NVDA",   # $140+ stock - AI leader
    "TSLA",   # $250+ stock - EV leader
    "AAPL",   # $190+ stock - Mega cap
    "MSFT",   # $415+ stock - Mega cap
    "GOOGL",  # $170+ stock - Mega cap
    "META",   # $560+ stock - Mega cap
    "AMZN",   # $210+ stock - Mega cap
    "AMD",    # $140+ stock - Chips

    # === ETFS (usually cheaper and liquid) ===
    "SPY",    # S&P 500 ETF
    "QQQ",    # NASDAQ ETF
    "IWM",    # Russell 2000 ETF

    # === OTHER POPULAR TRADING STOCKS ===
    "NFLX",   # Streaming
    "DIS",    # Disney
    "COIN",   # Crypto
    "UBER",   # Ride sharing
    "RIVN",   # EV
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan - startup and shutdown
    """
    # Startup
    logger.info("🚀 TradeFly Options - Starting up...")

    global options_api, market_data_api, signal_detector, paper_trading, position_tracker

    # Initialize paper trading engine
    paper_trading = PaperTradingEngine()
    logger.info("✅ Paper trading engine initialized")

    # Initialize position tracker
    position_tracker = PositionTracker()
    logger.info("✅ Position tracker initialized")

    # Initialize Massive Options API
    massive_api_key = os.getenv("POLYGON_API_KEY")  # Same key works for options
    if massive_api_key:
        options_api = MassiveOptionsAPI(massive_api_key)
        market_data_api = PolygonMarketDataService(massive_api_key)

        # Initialize signal detector
        signal_detector = OptionsSignalDetector(
            options_api=options_api,
            market_data_api=market_data_api,
            account_balance=float(os.getenv("ACCOUNT_BALANCE", "10000"))
        )

        logger.info("✅ Options trading engine initialized")
    else:
        logger.error("❌ POLYGON_API_KEY not found - options trading disabled")

    yield

    # Shutdown
    logger.info("👋 TradeFly Options - Shutting down...")


# Create FastAPI app
app = FastAPI(
    title="TradeFly Options API",
    description="World-Class Algorithmic Options Trading System",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your webapp domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    """Serve the trading dashboard UI"""
    return FileResponse("static/index.html")


@app.get("/api/health")
async def health_check():
    """API health check endpoint"""
    return {
        "name": "TradeFly Options API",
        "status": "operational",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "engines": {
            "options_api": options_api is not None,
            "market_data": market_data_api is not None,
            "signal_detector": signal_detector is not None
        }
    }


@app.get("/api/market/status")
async def get_market_status():
    """
    Get live market status and trading hours

    Returns:
        Market status with current time, session info, and trading hours
    """
    return MarketHours.get_market_status()


@app.get("/api/market/price-history")
async def get_price_history(
    symbol: str,
    timeframe: str = "1Day",
    days: int = 30
):
    """
    Get historical price data for charting

    Args:
        symbol: Stock symbol (e.g., "NVDA")
        timeframe: Timeframe for bars (1Min, 5Min, 15Min, 1Hour, 1Day)
        days: Number of days of history to fetch

    Returns:
        List of price bars with OHLCV data
    """
    if not data_provider:
        raise HTTPException(status_code=503, detail="Data provider not initialized")

    try:
        from datetime import datetime, timedelta

        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # Map timeframe to API format
        timeframe_map = {
            "1Min": "minute",
            "5Min": "minute",
            "15Min": "minute",
            "1Hour": "hour",
            "1Day": "day"
        }

        multiplier_map = {
            "1Min": 1,
            "5Min": 5,
            "15Min": 15,
            "1Hour": 1,
            "1Day": 1
        }

        tf_type = timeframe_map.get(timeframe, "day")
        multiplier = multiplier_map.get(timeframe, 1)

        # Fetch aggregates from Polygon
        bars = data_provider.get_aggregates(
            symbol=symbol,
            multiplier=multiplier,
            timespan=tf_type,
            from_date=start_date.strftime("%Y-%m-%d"),
            to_date=end_date.strftime("%Y-%m-%d")
        )

        if not bars:
            return []

        # Transform to chart format
        chart_data = []
        for bar in bars:
            chart_data.append({
                "time": int(bar.timestamp / 1000),  # Convert to seconds for TradingView
                "open": bar.open,
                "high": bar.high,
                "low": bar.low,
                "close": bar.close,
                "volume": bar.volume
            })

        return chart_data

    except Exception as e:
        logger.error(f"Error fetching price history for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching price history: {str(e)}")


@app.get("/api/options/signals", response_model=List[OptionsSignal])
async def get_signals(
    symbols: Optional[str] = None,
    strategy: Optional[StrategyType] = None,
    min_confidence: float = 0.80,
    max_results: int = 20
):
    """
    Get current options trading signals

    Args:
        symbols: Comma-separated symbols (e.g., "NVDA,TSLA,AAPL")
        strategy: Specific strategy to filter (SCALPING, MOMENTUM, VOLUME_SPIKE)
        min_confidence: Minimum confidence threshold (0-1)
        max_results: Maximum number of signals to return

    Returns:
        List of OptionsSignal objects
    """
    if not signal_detector:
        raise HTTPException(status_code=503, detail="Signal detector not initialized")

    # Parse watchlist
    watchlist = symbols.split(",") if symbols else DEFAULT_WATCHLIST

    # Get strategies to run
    strategies = [strategy] if strategy else None

    try:
        # Scan for signals
        signals = signal_detector.scan_for_signals(
            watchlist=watchlist,
            strategies=strategies
        )

        # Filter by confidence
        filtered_signals = [
            s for s in signals
            if s.confidence >= min_confidence
        ]

        # Auto-log filtered signals to paper trading
        if paper_trading:
            for signal in filtered_signals[:max_results]:
                try:
                    paper_trading.add_signal(signal)
                    logger.debug(f"Auto-logged signal {signal.signal_id} to paper trading")
                except Exception as e:
                    logger.warning(f"Failed to auto-log signal {signal.signal_id}: {e}")

        # Limit results
        return filtered_signals[:max_results]

    except Exception as e:
        logger.error(f"Error generating signals: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/options/top-signals", response_model=List[OptionsSignal])
async def get_top_signals(
    watchlist: Optional[str] = None,
    max_signals: int = 10,
    min_confidence: float = 0.85
):
    """
    Get top-rated trading signals

    Args:
        watchlist: Comma-separated symbols
        max_signals: Maximum number of signals
        min_confidence: Minimum confidence (0-1)

    Returns:
        List of top signals
    """
    if not signal_detector:
        raise HTTPException(status_code=503, detail="Signal detector not initialized")

    symbols = watchlist.split(",") if watchlist else DEFAULT_WATCHLIST

    try:
        signals = signal_detector.get_top_signals(
            watchlist=symbols,
            max_signals=max_signals,
            min_confidence=min_confidence
        )

        # Auto-log signals to paper trading
        if paper_trading:
            for signal in signals:
                try:
                    paper_trading.add_signal(signal)
                    logger.debug(f"Auto-logged signal {signal.signal_id} to paper trading")
                except Exception as e:
                    logger.warning(f"Failed to auto-log signal {signal.signal_id}: {e}")

        return signals

    except Exception as e:
        logger.error(f"Error getting top signals: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/options/chain/{symbol}")
async def get_options_chain(symbol: str):
    """
    Get full options chain for a symbol

    Args:
        symbol: Stock symbol (e.g., NVDA)

    Returns:
        List of option contracts
    """
    if not options_api:
        raise HTTPException(status_code=503, detail="Options API not initialized")

    try:
        contracts = options_api.get_options_chain(symbol.upper())

        return {
            "symbol": symbol.upper(),
            "timestamp": datetime.now().isoformat(),
            "contracts_count": len(contracts),
            "contracts": [c.dict() for c in contracts]
        }

    except Exception as e:
        logger.error(f"Error fetching options chain for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/options/liquid/{symbol}")
async def get_liquid_options(
    symbol: str,
    min_volume: int = 1000,
    max_spread: float = 5.0
):
    """
    Get liquid options suitable for trading

    Args:
        symbol: Stock symbol
        min_volume: Minimum daily volume
        max_spread: Maximum bid-ask spread %

    Returns:
        List of liquid option contracts
    """
    if not options_api:
        raise HTTPException(status_code=503, detail="Options API not initialized")

    try:
        contracts = options_api.get_liquid_options(
            symbol=symbol.upper(),
            min_volume=min_volume,
            max_spread_percent=max_spread
        )

        return {
            "symbol": symbol.upper(),
            "timestamp": datetime.now().isoformat(),
            "liquid_contracts": len(contracts),
            "filters": {
                "min_volume": min_volume,
                "max_spread_percent": max_spread
            },
            "contracts": [c.dict() for c in contracts]
        }

    except Exception as e:
        logger.error(f"Error fetching liquid options for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/options/unusual-activity")
async def get_unusual_activity(
    min_volume_ratio: float = 5.0,
    min_premium: float = 1000000
):
    """
    Get unusual options activity (smart money)

    Args:
        min_volume_ratio: Minimum volume/avg ratio (5x)
        min_premium: Minimum premium flow ($)

    Returns:
        List of contracts with unusual activity
    """
    if not options_api:
        raise HTTPException(status_code=503, detail="Options API not initialized")

    try:
        contracts = options_api.get_unusual_activity(
            min_volume_ratio=min_volume_ratio,
            min_premium=min_premium
        )

        return {
            "timestamp": datetime.now().isoformat(),
            "unusual_contracts": len(contracts),
            "filters": {
                "min_volume_ratio": min_volume_ratio,
                "min_premium_usd": min_premium
            },
            "contracts": [c.dict() for c in contracts]
        }

    except Exception as e:
        logger.error(f"Error fetching unusual activity: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/watchlist")
async def get_watchlist():
    """
    Get default watchlist

    Returns:
        List of symbols being monitored
    """
    return {
        "watchlist": DEFAULT_WATCHLIST,
        "count": len(DEFAULT_WATCHLIST)
    }


@app.post("/api/scan/background")
async def start_background_scan(
    background_tasks: BackgroundTasks,
    symbols: Optional[str] = None
):
    """
    Start background signal scan

    Args:
        background_tasks: FastAPI background tasks
        symbols: Comma-separated symbols (optional)

    Returns:
        Scan started confirmation
    """
    if not signal_detector:
        raise HTTPException(status_code=503, detail="Signal detector not initialized")

    watchlist = symbols.split(",") if symbols else DEFAULT_WATCHLIST

    background_tasks.add_task(
        run_background_scan,
        watchlist
    )

    return {
        "status": "scan_started",
        "watchlist": watchlist,
        "timestamp": datetime.now().isoformat()
    }


async def run_background_scan(watchlist: List[str]):
    """
    Run signal scan in background

    Args:
        watchlist: Symbols to scan
    """
    logger.info(f"Starting background scan for {len(watchlist)} symbols...")

    try:
        signals = signal_detector.scan_for_signals(watchlist)
        logger.info(f"Background scan complete: {len(signals)} signals generated")

        # In production, save signals to database or send alerts

    except Exception as e:
        logger.error(f"Error in background scan: {e}")


# ============================================================================
# PAPER TRADING ENDPOINTS - Track Performance & Learn
# ============================================================================

@app.get("/api/paper/stats")
async def get_paper_trading_stats(strategy: Optional[str] = None):
    """
    Get paper trading performance statistics

    Args:
        strategy: Filter by strategy (optional)

    Returns:
        Performance metrics including win rate, avg profit/loss, etc.
    """
    if not paper_trading:
        raise HTTPException(status_code=503, detail="Paper trading not initialized")

    stats = paper_trading.get_performance_stats(strategy)

    return {
        "timestamp": datetime.now().isoformat(),
        "strategy_filter": strategy,
        "stats": stats
    }


@app.post("/api/paper/add-trade")
async def add_manual_trade(
    symbol: str,
    strategy: str,
    action: str,
    entry_price: float,
    target_price: float,
    stop_loss: float,
    strike: float,
    option_type: str,
    expiration: str,
    entry_time: Optional[str] = None
):
    """
    Manually add a trade to paper trading (e.g., a trade you already took)

    Args:
        symbol: Stock symbol (e.g., NIO)
        strategy: Strategy name (e.g., SCALPING)
        action: Trade action (e.g., BUY_CALL)
        entry_price: Entry price per share
        target_price: Target price
        stop_loss: Stop loss price
        strike: Option strike price
        option_type: "call" or "put"
        expiration: Expiration date (YYYY-MM-DD)
        entry_time: Entry timestamp (ISO format, defaults to now)

    Returns:
        Created trade details
    """
    if not paper_trading:
        raise HTTPException(status_code=503, detail="Paper trading not initialized")

    from paper_trading import PaperTrade, TradeOutcome

    # Parse entry time
    if entry_time:
        entry_dt = datetime.fromisoformat(entry_time)
    else:
        entry_dt = datetime.now()

    # Create trade
    signal_id = f"manual_{symbol}_{entry_dt.strftime('%Y%m%d_%H%M%S')}"

    trade = PaperTrade(
        signal_id=signal_id,
        symbol=symbol,
        strategy=strategy,
        action=action,
        entry_price=entry_price,
        entry_time=entry_dt,
        target_price=target_price,
        stop_loss=stop_loss,
        strike=strike,
        option_type=option_type,
        expiration=expiration,
        outcome=TradeOutcome.PENDING,
        original_confidence=0.0,
        notes="Manually added trade"
    )

    paper_trading.trades.append(trade)
    paper_trading.save_trades()

    logger.info(f"Manually added trade: {symbol} ${strike} {option_type} @ ${entry_price}")

    return {
        "status": "trade_added",
        "trade": {
            "signal_id": trade.signal_id,
            "symbol": trade.symbol,
            "strategy": trade.strategy,
            "action": trade.action,
            "entry_price": trade.entry_price,
            "target_price": trade.target_price,
            "stop_loss": trade.stop_loss,
            "strike": trade.strike,
            "option_type": trade.option_type,
            "expiration": trade.expiration,
            "entry_time": trade.entry_time.isoformat()
        }
    }


@app.post("/api/paper/close-trade")
async def close_paper_trade(
    signal_id: str,
    exit_price: float,
    reason: str = "Manual close"
):
    """
    Manually close a paper trade

    Args:
        signal_id: ID of the trade to close
        exit_price: Exit price
        reason: Reason for closing

    Returns:
        Updated trade details
    """
    if not paper_trading:
        raise HTTPException(status_code=503, detail="Paper trading not initialized")

    trade = paper_trading.close_trade(signal_id, exit_price, reason)

    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")

    return {
        "status": "trade_closed",
        "trade": {
            "signal_id": trade.signal_id,
            "symbol": trade.symbol,
            "entry_price": trade.entry_price,
            "exit_price": trade.exit_price,
            "profit_loss": trade.profit_loss,
            "profit_loss_percent": trade.profit_loss_percent,
            "outcome": trade.outcome.value,
            "notes": trade.notes
        }
    }


@app.get("/api/paper/open-trades")
async def get_open_trades():
    """
    Get all open paper trades

    Returns:
        List of open trades
    """
    if not paper_trading:
        raise HTTPException(status_code=503, detail="Paper trading not initialized")

    trades = paper_trading.get_open_trades()

    return {
        "timestamp": datetime.now().isoformat(),
        "count": len(trades),
        "trades": [
            {
                "signal_id": t.signal_id,
                "symbol": t.symbol,
                "strategy": t.strategy,
                "action": t.action,
                "entry_price": t.entry_price,
                "target_price": t.target_price,
                "stop_loss": t.stop_loss,
                "strike": t.strike,
                "option_type": t.option_type,
                "expiration": t.expiration,
                "entry_time": t.entry_time.isoformat(),
                "days_open": (datetime.now() - t.entry_time).days
            }
            for t in trades
        ]
    }


@app.get("/api/paper/closed-trades")
async def get_closed_trades(limit: int = 50):
    """
    Get closed paper trades

    Args:
        limit: Maximum number of trades to return

    Returns:
        List of closed trades
    """
    if not paper_trading:
        raise HTTPException(status_code=503, detail="Paper trading not initialized")

    trades = paper_trading.get_closed_trades(limit)

    return {
        "timestamp": datetime.now().isoformat(),
        "count": len(trades),
        "trades": [
            {
                "signal_id": t.signal_id,
                "symbol": t.symbol,
                "strategy": t.strategy,
                "action": t.action,
                "entry_price": t.entry_price,
                "exit_price": t.exit_price,
                "profit_loss": t.profit_loss,
                "profit_loss_percent": t.profit_loss_percent,
                "outcome": t.outcome.value,
                "entry_time": t.entry_time.isoformat(),
                "exit_time": t.exit_time.isoformat() if t.exit_time else None,
                "notes": t.notes
            }
            for t in trades
        ]
    }


@app.get("/api/training/stats")
async def get_training_data_stats():
    """
    Get AI training data statistics and insights

    Returns:
        Overall stats, strategy performance, AI insights
    """
    try:
        from training_data import training_data_manager

        stats = training_data_manager.get_stats_summary()

        # Add more detailed stats
        all_outcomes = training_data_manager.get_all_outcomes()
        completed = [o for o in all_outcomes if o.outcome]

        if completed:
            wins = [o for o in completed if o.outcome == 'win']
            losses = [o for o in completed if o.outcome == 'loss']

            stats['avg_profit_percent'] = sum(o.profit_loss_percent for o in wins) / len(wins) if wins else 0
            stats['avg_loss_percent'] = sum(o.profit_loss_percent for o in losses) / len(losses) if losses else 0
            stats['profit_factor'] = abs(sum(o.profit_loss_percent for o in wins) / sum(o.profit_loss_percent for o in losses)) if losses and sum(o.profit_loss_percent for o in losses) != 0 else 0

        return stats

    except Exception as e:
        logger.error(f"Error getting training stats: {e}")
        # Return empty stats if training data not available
        return {
            'total_outcomes': 0,
            'completed': 0,
            'pending': 0,
            'win_rate': 0.0,
            'total_wins': 0,
            'total_losses': 0,
            'strategies': {},
            'avg_profit_percent': 0,
            'avg_loss_percent': 0,
            'profit_factor': 0
        }


@app.get("/api/training/recent-outcomes")
async def get_recent_training_outcomes(limit: int = 10):
    """
    Get recent training data outcomes

    Args:
        limit: Number of outcomes to return

    Returns:
        List of recent SignalOutcome objects
    """
    try:
        from training_data import training_data_manager

        outcomes = training_data_manager.get_all_outcomes(limit=limit)

        # Convert to dict format for JSON serialization
        return [
            {
                'signal_id': o.signal_id,
                'timestamp': o.timestamp.isoformat(),
                'symbol': o.symbol,
                'strategy': o.strategy.value,
                'confidence': o.confidence,
                'action': o.action.value,
                'entry_price': o.entry_price,
                'exit_price': o.exit_price,
                'profit_loss_percent': o.profit_loss_percent,
                'hold_duration_minutes': o.hold_duration_minutes,
                'exit_reason': o.exit_reason,
                'outcome': o.outcome,
                'rsi_14': o.rsi_14,
                'delta': o.delta,
                'iv_rank': o.iv_rank
            }
            for o in outcomes
        ]

    except Exception as e:
        logger.error(f"Error getting recent outcomes: {e}")
        return []


@app.post("/api/paper/quick-add-signal")
async def quick_add_signal_to_paper_trading(signal: OptionsSignal):
    """
    Quick-add a signal to paper trading (one-click from signal card)

    Args:
        signal: Complete OptionsSignal object from frontend

    Returns:
        Created trade details
    """
    if not paper_trading:
        raise HTTPException(status_code=503, detail="Paper trading not initialized")

    try:
        # Check if already in paper trading
        existing = next(
            (t for t in paper_trading.trades if t.signal_id == signal.signal_id),
            None
        )

        if existing:
            # Return existing trade
            return {
                "status": "already_exists",
                "message": "Signal already in paper trading",
                "trade": {
                    "signal_id": existing.signal_id,
                    "symbol": existing.symbol,
                    "strategy": existing.strategy,
                    "entry_price": existing.entry_price,
                    "outcome": existing.outcome.value
                }
            }

        # Add to paper trading
        trade = paper_trading.add_signal(signal)

        logger.info(f"Quick-added signal {signal.signal_id} to paper trading: {signal.symbol} @ ${signal.suggested_entry}")

        return {
            "status": "added",
            "message": f"Added {signal.symbol} to paper trading",
            "trade": {
                "signal_id": trade.signal_id,
                "symbol": trade.symbol,
                "strategy": trade.strategy,
                "action": trade.action,
                "entry_price": trade.entry_price,
                "target_price": trade.target_price,
                "stop_loss": trade.stop_loss,
                "strike": trade.strike,
                "option_type": trade.option_type,
                "expiration": trade.expiration,
                "confidence": trade.original_confidence
            }
        }

    except Exception as e:
        logger.error(f"Error quick-adding signal to paper trading: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# BACKTESTING ENDPOINTS - Test Strategies Before Using Them
# ============================================================================

@app.get("/api/backtest/run/{symbol}")
async def run_backtest(
    symbol: str,
    strategy: str = "SCALPING",
    lookback_days: int = 30,
    option_dte: int = 7
):
    """
    Run backtest on a symbol to see if strategy would have worked

    Args:
        symbol: Stock symbol (e.g., NIO)
        strategy: Strategy to test
        lookback_days: Days of history to test
        option_dte: Days to expiration for simulated options

    Returns:
        Backtest results with win rate, profit factor, etc.
    """
    backtest = BacktestEngine()

    result = backtest.backtest_strategy_on_stock(
        symbol=symbol.upper(),
        strategy_name=strategy,
        lookback_days=lookback_days,
        option_dte=option_dte
    )

    # Generate report
    report = backtest.get_summary_report(result)

    return {
        "symbol": symbol.upper(),
        "strategy": strategy,
        "lookback_days": lookback_days,
        "results": {
            "total_trades": result.total_trades,
            "winners": result.winners,
            "losers": result.losers,
            "win_rate": result.win_rate,
            "profit_factor": result.profit_factor,
            "avg_win_percent": result.avg_win,
            "avg_loss_percent": result.avg_loss,
            "best_trade_percent": result.best_trade,
            "worst_trade_percent": result.worst_trade,
            "total_pnl": result.total_pnl,
            "avg_holding_days": result.avg_holding_period
        },
        "report": report
    }


@app.post("/api/backtest/batch")
async def run_batch_backtest(
    symbols: List[str],
    strategy: str = "SCALPING",
    lookback_days: int = 30
):
    """
    Run backtest on multiple symbols at once

    Args:
        symbols: List of symbols to test
        strategy: Strategy to test
        lookback_days: Days of history

    Returns:
        Results for all symbols
    """
    backtest = BacktestEngine()
    results = {}

    for symbol in symbols[:10]:  # Limit to 10 symbols
        result = backtest.backtest_strategy_on_stock(
            symbol=symbol.upper(),
            strategy_name=strategy,
            lookback_days=lookback_days
        )

        results[symbol.upper()] = {
            "total_trades": result.total_trades,
            "win_rate": result.win_rate,
            "profit_factor": result.profit_factor,
            "total_pnl": result.total_pnl
        }

    # Sort by win rate
    sorted_results = dict(sorted(results.items(), key=lambda x: x[1]["win_rate"], reverse=True))

    return {
        "timestamp": datetime.now().isoformat(),
        "strategy": strategy,
        "symbols_tested": len(sorted_results),
        "results": sorted_results
    }


# ==================== POSITION TRACKING ENDPOINTS ====================
@app.post("/api/positions/mark-bought")
async def mark_signal_as_bought(
    signal_id: str,
    symbol: str,
    strategy: str,
    action: str,
    entry_price: float,
    target_price: float,
    stop_loss: float,
    strike: float,
    option_type: str,
    expiration: str,
    contracts_bought: int = 1,
    notes: str = ""
):
    """
    Mark a signal as bought and start tracking it

    Args:
        signal_id: Original signal ID
        symbol: Stock symbol
        strategy: "SCALPING" or "SWING"
        action: "BUY_CALL" or "BUY_PUT"
        entry_price: Price you bought at (per share)
        target_price: Target to sell at
        stop_loss: Stop loss price
        strike: Option strike price
        option_type: "call" or "put"
        expiration: Expiration date "YYYY-MM-DD"
        contracts_bought: Number of contracts (default 1)
        notes: Optional notes

    Returns:
        Position object
    """
    if not position_tracker:
        raise HTTPException(status_code=503, detail="Position tracker not initialized")

    try:
        position = position_tracker.add_position(
            signal_id=signal_id,
            symbol=symbol,
            strategy=strategy,
            action=action,
            entry_price=entry_price,
            target_price=target_price,
            stop_loss=stop_loss,
            strike=strike,
            option_type=option_type,
            expiration=expiration,
            contracts_bought=contracts_bought,
            notes=notes
        )

        return {
            "success": True,
            "message": f"Position tracked: {symbol} {strike}{option_type.upper()}",
            "position": {
                "position_id": position.position_id,
                "symbol": position.symbol,
                "strategy": position.strategy,
                "entry_price": position.entry_price,
                "target_price": position.target_price,
                "stop_loss": position.stop_loss,
                "contracts": position.contracts_bought,
                "max_profit": (position.target_price - position.entry_price) * 100 * position.contracts_bought,
                "max_loss": (position.entry_price - position.stop_loss) * 100 * position.contracts_bought
            }
        }
    except Exception as e:
        logger.error(f"Error marking position as bought: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/positions/active")
async def get_active_positions():
    """
    Get all active positions (trades you're currently holding)

    Returns:
        List of active positions with current P/L
    """
    if not position_tracker:
        raise HTTPException(status_code=503, detail="Position tracker not initialized")

    try:
        active = position_tracker.get_active_positions()

        positions = []
        for pos in active:
            # Calculate current P/L
            pnl_percent = pos.profit_loss_percent or 0.0
            pnl_dollars = pos.profit_loss or 0.0

            # Check exit signals
            exit_signals = position_tracker.check_exit_signals(pos.position_id)

            positions.append({
                "position_id": pos.position_id,
                "signal_id": pos.signal_id,
                "symbol": pos.symbol,
                "strategy": pos.strategy,
                "action": pos.action,
                "entry_price": pos.entry_price,
                "current_price": pos.current_price,
                "target_price": pos.target_price,
                "stop_loss": pos.stop_loss,
                "contracts": pos.contracts_bought,
                "strike": pos.strike,
                "option_type": pos.option_type,
                "expiration": pos.expiration,
                "entry_time": pos.entry_time.isoformat(),
                "last_update": pos.last_update.isoformat() if pos.last_update else None,
                "profit_loss": pnl_dollars,
                "profit_loss_percent": pnl_percent,
                "exit_signals": [
                    {
                        "reason": sig.reason.value,
                        "urgency": sig.urgency,
                        "message": sig.message,
                        "suggested_exit_price": sig.suggested_exit_price
                    }
                    for sig in exit_signals
                ],
                "has_exit_signal": len(exit_signals) > 0,
                "notes": pos.notes
            })

        return {
            "timestamp": datetime.now().isoformat(),
            "active_positions": len(positions),
            "positions": positions
        }
    except Exception as e:
        logger.error(f"Error getting active positions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/positions/update/{position_id}")
async def update_position_price(position_id: str, current_price: float):
    """
    Update position with current price (check for exit signals)

    Args:
        position_id: Position to update
        current_price: Current option price

    Returns:
        Updated position with exit signals
    """
    if not position_tracker:
        raise HTTPException(status_code=503, detail="Position tracker not initialized")

    try:
        position = position_tracker.update_position(position_id, current_price)
        if not position:
            raise HTTPException(status_code=404, detail="Position not found")

        # Check for exit signals
        exit_signals = position_tracker.check_exit_signals(position_id)

        return {
            "success": True,
            "position": {
                "position_id": position.position_id,
                "symbol": position.symbol,
                "current_price": position.current_price,
                "profit_loss": position.profit_loss,
                "profit_loss_percent": position.profit_loss_percent,
                "highest_price": position.highest_price
            },
            "exit_signals": [
                {
                    "reason": sig.reason.value,
                    "urgency": sig.urgency,
                    "message": sig.message,
                    "suggested_exit_price": sig.suggested_exit_price
                }
                for sig in exit_signals
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating position: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/positions/close/{position_id}")
async def close_position(position_id: str, exit_price: float, exit_reason: str = "Manual close"):
    """
    Close a position (mark as sold)

    Args:
        position_id: Position to close
        exit_price: Price you sold at
        exit_reason: Why you closed it

    Returns:
        Closed position with final P/L
    """
    if not position_tracker:
        raise HTTPException(status_code=503, detail="Position tracker not initialized")

    try:
        position = position_tracker.close_position(position_id, exit_price, exit_reason)
        if not position:
            raise HTTPException(status_code=404, detail="Position not found")

        return {
            "success": True,
            "message": f"Position closed: {position.profit_loss_percent:+.1f}%",
            "position": {
                "position_id": position.position_id,
                "symbol": position.symbol,
                "entry_price": position.entry_price,
                "exit_price": position.exit_price,
                "entry_time": position.entry_time.isoformat(),
                "exit_time": position.exit_time.isoformat() if position.exit_time else None,
                "holding_period": str(position.exit_time - position.entry_time) if position.exit_time else None,
                "profit_loss": position.profit_loss,
                "profit_loss_percent": position.profit_loss_percent,
                "exit_reason": position.exit_reason,
                "contracts": position.contracts_bought
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error closing position: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/positions/closed")
async def get_closed_positions(limit: int = 50):
    """
    Get closed positions (trade history)

    Args:
        limit: Number of trades to return (default 50)

    Returns:
        List of closed positions
    """
    if not position_tracker:
        raise HTTPException(status_code=503, detail="Position tracker not initialized")

    try:
        closed = position_tracker.get_closed_positions(limit)

        positions = []
        for pos in closed:
            positions.append({
                "position_id": pos.position_id,
                "symbol": pos.symbol,
                "strategy": pos.strategy,
                "action": pos.action,
                "entry_price": pos.entry_price,
                "exit_price": pos.exit_price,
                "entry_time": pos.entry_time.isoformat(),
                "exit_time": pos.exit_time.isoformat() if pos.exit_time else None,
                "holding_period": str(pos.exit_time - pos.entry_time) if pos.exit_time else None,
                "profit_loss": pos.profit_loss,
                "profit_loss_percent": pos.profit_loss_percent,
                "exit_reason": pos.exit_reason,
                "contracts": pos.contracts_bought,
                "strike": pos.strike,
                "option_type": pos.option_type
            })

        return {
            "timestamp": datetime.now().isoformat(),
            "closed_positions": len(positions),
            "positions": positions
        }
    except Exception as e:
        logger.error(f"Error getting closed positions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/positions/stats")
async def get_position_stats(strategy: Optional[str] = None):
    """
    Get performance statistics for tracked positions

    Args:
        strategy: Filter by strategy ("SCALPING" or "SWING")

    Returns:
        Performance metrics
    """
    if not position_tracker:
        raise HTTPException(status_code=503, detail="Position tracker not initialized")

    try:
        stats = position_tracker.get_performance_summary(strategy)
        return {
            "timestamp": datetime.now().isoformat(),
            "strategy_filter": strategy,
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Error getting position stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# === SPA CATCH-ALL ROUTE ===
# This MUST be the last route defined (most specific routes first, catch-all last)
@app.get("/{full_path:path}")
async def spa_catchall(full_path: str):
    """
    Catch-all route for Single Page Application
    Serves index.html for client-side routing (/scalping, /swing, etc.)

    Allows the frontend router to handle navigation without 404 errors
    """
    # Don't interfere with API routes or static files - those should 404 if not found
    if full_path.startswith("api/") or full_path.startswith("static/"):
        raise HTTPException(status_code=404, detail="Not found")

    # Serve index.html for all other routes (SPA client-side routing)
    return FileResponse("static/index.html")


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8001"))  # Different port from stock backend

    uvicorn.run(
        "main_options:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
