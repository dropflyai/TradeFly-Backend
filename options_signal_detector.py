"""
Options Signal Detector - Main Engine
Orchestrates all strategies and generates trading signals

This is the CORE ENGINE that:
1. Fetches real-time options data
2. Runs scalping, momentum, and volume spike detection
3. Calculates technical indicators
4. Applies risk management
5. Generates actionable trading signals
6. Detects candlestick patterns for entry/exit signals

RELIABILITY FEATURES:
- Data staleness detection (refuse to trade on old data)
"""
import logging
from typing import List, Optional
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import requests
import os
import redis
import time

from options_models import (
    OptionContract,
    ScalpSignal,
    MomentumSignal,
    VolumeSpikeSignal,
    OptionsSignal,
    StrategyType,
    TechnicalIndicators
)
from options_strategies import (
    ScalpingStrategy,
    MomentumStrategy,
    VolumeSpikeStrategy,
    RiskManager
)
from swing_trading_strategy import SwingTradingStrategy, SwingSignal
from massive_options_api import MassiveOptionsAPI
from technical_analysis import TechnicalAnalysis
from candlestick_patterns import CandlestickPatternDetector, PatternType, Signal

logger = logging.getLogger(__name__)


class DataStaleError(Exception):
    """Raised when market data is too old to trade on"""
    pass


# Initialize Redis client for staleness check
try:
    redis_host = os.getenv('REDIS_HOST', 'localhost')
    redis_port = int(os.getenv('REDIS_PORT', 6379))
    redis_client = redis.Redis(
        host=redis_host,
        port=redis_port,
        decode_responses=True,
        socket_connect_timeout=3,
        socket_timeout=3
    )
    redis_client.ping()
    logger.info(f"✅ Redis connected for staleness detection: {redis_host}:{redis_port}")
except Exception as e:
    logger.warning(f"⚠️  Redis unavailable: {e}. Staleness detection disabled.")
    redis_client = None


class OptionsSignalDetector:
    """
    Main options trading signal detection engine

    Combines:
    - Real-time options data
    - Multiple trading strategies
    - Technical analysis
    - Risk management
    """

    def __init__(
        self,
        options_api: MassiveOptionsAPI,
        account_balance: float = 10000.0
    ):
        self.options_api = options_api
        self.account_balance = account_balance
        self.risk_manager = RiskManager()
        self.ta = TechnicalAnalysis()
        self.pattern_detector = CandlestickPatternDetector()

        logger.info("Options Signal Detector initialized with candlestick pattern recognition")

    def _check_data_freshness(self) -> None:
        """
        Check if market data is fresh enough to trade on

        Raises:
            DataStaleError: If data is older than 45 seconds
        """
        if not redis_client:
            # If Redis unavailable, skip staleness check
            return

        try:
            last_update = redis_client.get("last_data_update")

            if not last_update:
                logger.warning("⚠️  No data update timestamp found - first run?")
                return

            age = time.time() - float(last_update)

            if age > 45:  # 45 second threshold
                raise DataStaleError(
                    f"Market data is {age:.1f}s old (threshold: 45s). "
                    f"Refusing to generate signals on stale data."
                )

            logger.debug(f"✅ Data freshness OK: {age:.1f}s old")

        except DataStaleError:
            raise
        except Exception as e:
            logger.warning(f"Could not check data freshness: {e}")

    def scan_for_signals(
        self,
        watchlist: List[str],
        strategies: List[StrategyType] = None
    ) -> List[OptionsSignal]:
        """
        Scan watchlist for trading opportunities

        RELIABILITY: Checks data freshness before scanning

        Args:
            watchlist: List of symbols to scan (e.g., ["NVDA", "TSLA", "AAPL"])
            strategies: Strategies to run (defaults to all)

        Returns:
            List of OptionsSignal objects

        Raises:
            DataStaleError: If market data is too old
        """
        # Check data freshness FIRST
        try:
            self._check_data_freshness()
        except DataStaleError as e:
            logger.error(f"❌ {e}")
            # Return empty signals rather than crash - frontend will show error
            return []

        if strategies is None:
            strategies = [
                StrategyType.SCALPING,
                StrategyType.SWING,
                StrategyType.MOMENTUM,
                StrategyType.VOLUME_SPIKE
            ]

        all_signals = []

        for symbol in watchlist:
            logger.info(f"Scanning {symbol} for options signals...")

            # Get liquid options for this symbol
            # Very low threshold for early session testing (tune up during peak hours 11AM-2PM)
            contracts = self.options_api.get_liquid_options(
                symbol,
                min_volume=10,  # Very low for early session - will tune up at peak hours
                max_spread_percent=50.0  # Increased to 50% for affordable options (cheap contracts have wide % spreads)
            )

            if not contracts:
                logger.warning(f"No liquid contracts found for {symbol}")
                continue

            # Get underlying price history
            price_history = self._get_price_history(symbol)
            if price_history is None:
                logger.warning(f"Could not get price history for {symbol}")
                continue

            # Run strategies on each contract
            for contract in contracts:
                signals = self._analyze_contract(
                    contract,
                    price_history,
                    strategies
                )
                all_signals.extend(signals)

        # Rank signals by confidence
        all_signals.sort(key=lambda s: s.confidence, reverse=True)

        logger.info(f"Generated {len(all_signals)} trading signals")
        return all_signals

    def _analyze_contract(
        self,
        contract: OptionContract,
        price_history: dict,
        strategies: List[StrategyType]
    ) -> List[OptionsSignal]:
        """
        Analyze a single contract with all strategies

        Args:
            contract: Option contract to analyze
            price_history: Price history for underlying
            strategies: Strategies to apply

        Returns:
            List of signals generated
        """
        signals = []

        # Detect candlestick patterns for entry confirmation
        candlestick_patterns = self._detect_candlestick_patterns(price_history)

        # Store patterns for later use in signal enhancement
        price_history['candlestick_patterns'] = candlestick_patterns

        # Run scalping strategy
        if StrategyType.SCALPING in strategies:
            scalp_signal = self._detect_scalp(contract, price_history)
            if scalp_signal:
                # Enhance with candlestick patterns
                enhanced_signal = self._enhance_signal_with_patterns(
                    self._convert_to_unified_signal(scalp_signal, contract),
                    candlestick_patterns
                )
                signals.append(enhanced_signal)

        # Run swing trading strategy
        if StrategyType.SWING in strategies:
            swing_signal = self._detect_swing(contract, price_history)
            if swing_signal:
                enhanced_signal = self._enhance_signal_with_patterns(
                    self._convert_to_unified_signal(swing_signal, contract),
                    candlestick_patterns
                )
                signals.append(enhanced_signal)

        # Run momentum strategy
        if StrategyType.MOMENTUM in strategies:
            momentum_signal = self._detect_momentum(contract, price_history)
            if momentum_signal:
                enhanced_signal = self._enhance_signal_with_patterns(
                    self._convert_to_unified_signal(momentum_signal, contract),
                    candlestick_patterns
                )
                signals.append(enhanced_signal)

        # Run volume spike strategy
        if StrategyType.VOLUME_SPIKE in strategies:
            volume_signal = self._detect_volume_spike(contract, price_history)
            if volume_signal:
                enhanced_signal = self._enhance_signal_with_patterns(
                    self._convert_to_unified_signal(volume_signal, contract),
                    candlestick_patterns
                )
                signals.append(enhanced_signal)

        return signals

    def _detect_scalp(
        self,
        contract: OptionContract,
        price_history: dict
    ) -> Optional[ScalpSignal]:
        """
        Run scalping strategy

        Args:
            contract: Option contract
            price_history: Price history data

        Returns:
            ScalpSignal if detected
        """
        try:
            prices_1m = price_history.get("1m", np.array([]))

            if len(prices_1m) < 5:
                return None

            signal = ScalpingStrategy.detect_signal(
                contract=contract,
                price_history_1m=prices_1m,
                timeframe='1m'
            )

            return signal

        except Exception as e:
            logger.error(f"Error in scalp detection: {e}")
            return None

    def _detect_swing(
        self,
        contract: OptionContract,
        price_history: dict
    ) -> Optional[SwingSignal]:
        """
        Run swing trading strategy

        Args:
            contract: Option contract
            price_history: Price history data

        Returns:
            SwingSignal if detected
        """
        try:
            prices_1h = price_history.get("1h", np.array([]))
            prices_daily = price_history.get("daily", np.array([]))

            if len(prices_1h) < 5 or len(prices_daily) < 10:
                return None

            signal = SwingTradingStrategy.detect_signal(
                contract=contract,
                price_history_1h=prices_1h,
                price_history_daily=prices_daily
            )

            return signal

        except Exception as e:
            logger.error(f"Error in swing detection: {e}")
            return None

    def _detect_momentum(
        self,
        contract: OptionContract,
        price_history: dict
    ) -> Optional[MomentumSignal]:
        """
        Run momentum strategy

        Args:
            contract: Option contract
            price_history: Price history data

        Returns:
            MomentumSignal if detected
        """
        try:
            prices_15m = price_history.get("15m", np.array([]))
            volumes_15m = price_history.get("15m_volume", np.array([]))

            if len(prices_15m) < 35:  # Need enough for MACD
                return None

            signal = MomentumStrategy.detect_signal(
                contract=contract,
                price_history_15m=prices_15m,
                volume_history_15m=volumes_15m
            )

            return signal

        except Exception as e:
            logger.error(f"Error in momentum detection: {e}")
            return None

    def _detect_volume_spike(
        self,
        contract: OptionContract,
        price_history: dict
    ) -> Optional[VolumeSpikeSignal]:
        """
        Run volume spike strategy

        Args:
            contract: Option contract
            price_history: Price history data

        Returns:
            VolumeSpikeSignal if detected
        """
        try:
            # Simulate block trades detection
            # In production, this would come from real-time trade feed
            block_trades = self._simulate_block_trades(contract)

            signal = VolumeSpikeStrategy.detect_signal(
                contract=contract,
                block_trades=block_trades
            )

            return signal

        except Exception as e:
            logger.error(f"Error in volume spike detection: {e}")
            return None

    def _convert_to_unified_signal(
        self,
        strategy_signal,
        contract: OptionContract
    ) -> OptionsSignal:
        """
        Convert strategy-specific signal to unified OptionsSignal

        Args:
            strategy_signal: ScalpSignal, MomentumSignal, or VolumeSpikeSignal
            contract: Option contract

        Returns:
            Unified OptionsSignal
        """
        # Calculate technical indicators
        technical = self._calculate_technical_indicators(contract)

        # Determine strategy type
        if isinstance(strategy_signal, ScalpSignal):
            strategy_type = StrategyType.SCALPING
            entry = strategy_signal.entry
            target = strategy_signal.target
            stop = strategy_signal.stop
        elif isinstance(strategy_signal, SwingSignal):
            strategy_type = StrategyType.SWING
            entry = strategy_signal.entry
            target = strategy_signal.target
            stop = strategy_signal.stop
        elif isinstance(strategy_signal, MomentumSignal):
            strategy_type = StrategyType.MOMENTUM
            entry = strategy_signal.entry
            target = strategy_signal.target
            stop = strategy_signal.stop
        else:  # VolumeSpikeSignal
            strategy_type = StrategyType.VOLUME_SPIKE
            # For volume spikes, use current price with standard targets
            entry = contract.pricing.ask
            target = entry * 1.30  # 30% target
            stop = entry * 0.85     # 15% stop

        # Calculate risk/reward
        risk = entry - stop
        reward = target - entry
        risk_reward = reward / risk if risk > 0 else 0

        # Calculate position size recommendation
        position_size = self.risk_manager.calculate_position_size(
            self.account_balance,
            risk_per_trade=0.02
        )

        # Generate signal ID
        signal_id = f"{strategy_type.value}_{contract.symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        return OptionsSignal(
            signal_id=signal_id,
            strategy=strategy_type,
            contract=contract,
            action=strategy_signal.action,
            entry_price=entry,
            target_price=target,
            stop_loss=stop,
            confidence=strategy_signal.confidence,
            reasoning=strategy_signal.reason,
            technical_indicators=technical,
            position_size_recommendation=position_size,
            risk_reward_ratio=risk_reward,
            timestamp=datetime.now(),
            is_active=True
        )

    def _calculate_technical_indicators(
        self,
        contract: OptionContract
    ) -> TechnicalIndicators:
        """
        Calculate all technical indicators for a contract

        Args:
            contract: Option contract

        Returns:
            TechnicalIndicators object
        """
        # Placeholder - in production, fetch real price history
        # For now, use dummy values
        return TechnicalIndicators(
            rsi_14=50.0,
            macd_line=0.0,
            macd_signal=0.0,
            macd_histogram=0.0,
            bb_upper=contract.underlying_price * 1.02,
            bb_middle=contract.underlying_price,
            bb_lower=contract.underlying_price * 0.98,
            vwap=contract.underlying_price,
            resistance_levels=[contract.underlying_price * 1.05],
            support_levels=[contract.underlying_price * 0.95]
        )

    def _get_price_history(self, symbol: str) -> Optional[dict]:
        """
        Get REAL price history for underlying stock using Massive API (Stock Advanced)

        Args:
            symbol: Stock symbol

        Returns:
            Dictionary with price arrays and DataFrames for different timeframes
        """
        try:
            api_key = os.getenv('MASSIVE_API_KEY')
            if not api_key:
                logger.error("MASSIVE_API_KEY not found")
                return None

            base_url = "https://api.massive.com"

            # Get different timeframes using Massive API aggregates
            # Stock Advanced plan includes real-time intraday bars

            # 1-minute bars (last 100 bars for scalping)
            df_1m = self._fetch_massive_bars(base_url, api_key, symbol, '1', 'minute', 100)

            # 15-minute bars (last 50 bars for momentum)
            df_15m = self._fetch_massive_bars(base_url, api_key, symbol, '15', 'minute', 50)

            # 1-hour bars (last 50 bars for swing)
            df_1h = self._fetch_massive_bars(base_url, api_key, symbol, '1', 'hour', 50)

            # Daily bars (last 90 days for swing + candlestick patterns)
            df_daily = self._fetch_massive_bars(base_url, api_key, symbol, '1', 'day', 90)

            # Check if we have at least SOME data
            if df_1m is None or df_1m.empty:
                logger.warning(f"No price history available for {symbol} from Massive API")
                return None

            # Extract close prices as numpy arrays
            prices_1m = df_1m['close'].values[-100:] if len(df_1m) > 0 else np.array([])
            prices_15m = df_15m['close'].values[-50:] if len(df_15m) > 0 and df_15m is not None else np.array([])
            volumes_15m = df_15m['volume'].values[-50:] if len(df_15m) > 0 and df_15m is not None else np.array([])
            prices_1h = df_1h['close'].values[-50:] if len(df_1h) > 0 and df_1h is not None else np.array([])
            prices_daily = df_daily['close'].values[-30:] if len(df_daily) > 0 and df_daily is not None else np.array([])

            logger.info(f"✅ Fetched Massive API data for {symbol}: {len(prices_1m)} 1m bars, {len(prices_15m)} 15m bars, {len(prices_1h)} 1h bars, {len(prices_daily)} daily bars")

            # Rename columns to match yfinance format for candlestick patterns
            for df in [df_1m, df_15m, df_1h, df_daily]:
                if df is not None and not df.empty:
                    df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']

            return {
                "1m": prices_1m,
                "15m": prices_15m,
                "15m_volume": volumes_15m,
                "1h": prices_1h,
                "daily": prices_daily,
                # Include DataFrames for candlestick pattern detection
                "df_1m": df_1m if df_1m is not None else pd.DataFrame(),
                "df_15m": df_15m if df_15m is not None else pd.DataFrame(),
                "df_1h": df_1h if df_1h is not None else pd.DataFrame(),
                "df_daily": df_daily if df_daily is not None else pd.DataFrame()
            }

        except Exception as e:
            logger.error(f"Error getting price history from Massive API for {symbol}: {e}")
            return None

    def _fetch_massive_bars(self, base_url: str, api_key: str, symbol: str,
                           multiplier: str, timespan: str, limit: int) -> Optional[pd.DataFrame]:
        """
        Fetch aggregate bars from Massive API

        Args:
            base_url: Massive API base URL
            api_key: API key
            symbol: Stock symbol
            multiplier: Time multiplier (e.g., '1', '15')
            timespan: Timespan unit ('minute', 'hour', 'day')
            limit: Number of bars to fetch

        Returns:
            DataFrame with OHLCV data or None
        """
        try:
            # Calculate date range
            today = datetime.now()
            if timespan == 'minute':
                from_date = (today - timedelta(days=2)).strftime('%Y-%m-%d')
            elif timespan == 'hour':
                from_date = (today - timedelta(days=30)).strftime('%Y-%m-%d')
            else:  # day
                from_date = (today - timedelta(days=180)).strftime('%Y-%m-%d')

            to_date = today.strftime('%Y-%m-%d')

            url = f"{base_url}/v2/aggs/ticker/{symbol}/range/{multiplier}/{timespan}/{from_date}/{to_date}"

            params = {
                'adjusted': 'true',
                'sort': 'desc',
                'limit': limit,
                'apiKey': api_key
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            if data.get('resultsCount', 0) == 0:
                logger.debug(f"No {multiplier}{timespan} data for {symbol}")
                return None

            results = data.get('results', [])
            if not results:
                return None

            # Convert to DataFrame (Massive API format: o, h, l, c, v, t)
            df = pd.DataFrame(results)
            df = df[['o', 'h', 'l', 'c', 'v']]  # open, high, low, close, volume
            df.columns = ['open', 'high', 'low', 'close', 'volume']

            # Reverse to chronological order
            df = df.iloc[::-1].reset_index(drop=True)

            return df

        except Exception as e:
            logger.debug(f"Error fetching {multiplier}{timespan} bars for {symbol}: {e}")
            return None

    def _detect_candlestick_patterns(self, price_history: dict) -> List:
        """
        Detect candlestick patterns across all timeframes

        Args:
            price_history: Dictionary with DataFrames for different timeframes

        Returns:
            List of detected candlestick patterns
        """
        all_patterns = []

        try:
            # Check daily timeframe for swing patterns
            df_daily = price_history.get('df_daily')
            if df_daily is not None and len(df_daily) >= 10:
                patterns_daily = self.pattern_detector.detect_patterns(df_daily)
                for pattern in patterns_daily:
                    pattern.timeframe = 'daily'  # Add timeframe info
                all_patterns.extend(patterns_daily)
                if patterns_daily:
                    logger.info(f"Found {len(patterns_daily)} candlestick patterns on daily chart")

            # Check 1-hour timeframe for swing/momentum patterns
            df_1h = price_history.get('df_1h')
            if df_1h is not None and len(df_1h) >= 10:
                patterns_1h = self.pattern_detector.detect_patterns(df_1h)
                for pattern in patterns_1h:
                    pattern.timeframe = '1h'
                all_patterns.extend(patterns_1h)
                if patterns_1h:
                    logger.info(f"Found {len(patterns_1h)} candlestick patterns on 1h chart")

            # Check 15-minute timeframe for scalp/momentum patterns
            df_15m = price_history.get('df_15m')
            if df_15m is not None and len(df_15m) >= 10:
                patterns_15m = self.pattern_detector.detect_patterns(df_15m)
                for pattern in patterns_15m:
                    pattern.timeframe = '15m'
                all_patterns.extend(patterns_15m)
                if patterns_15m:
                    logger.info(f"Found {len(patterns_15m)} candlestick patterns on 15m chart")

        except Exception as e:
            logger.error(f"Error detecting candlestick patterns: {e}")

        return all_patterns

    def _enhance_signal_with_patterns(
        self,
        signal: OptionsSignal,
        patterns: List
    ) -> OptionsSignal:
        """
        Enhance trading signal with candlestick pattern information

        Args:
            signal: Original trading signal
            patterns: List of detected candlestick patterns

        Returns:
            Enhanced signal with pattern confirmation
        """
        if not patterns:
            return signal

        # Filter patterns by timeframe relevance
        relevant_patterns = []

        if signal.strategy == StrategyType.SCALPING:
            # Scalping: Focus on 15m patterns
            relevant_patterns = [p for p in patterns if hasattr(p, 'timeframe') and p.timeframe == '15m']
        elif signal.strategy == StrategyType.SWING:
            # Swing: Focus on daily and 1h patterns
            relevant_patterns = [p for p in patterns if hasattr(p, 'timeframe') and p.timeframe in ['daily', '1h']]
        elif signal.strategy == StrategyType.MOMENTUM:
            # Momentum: Use 1h and 15m patterns
            relevant_patterns = [p for p in patterns if hasattr(p, 'timeframe') and p.timeframe in ['1h', '15m']]
        else:
            # Volume spike: Use all patterns
            relevant_patterns = patterns

        if not relevant_patterns:
            return signal

        # Find the strongest pattern (highest confidence)
        strongest_pattern = max(relevant_patterns, key=lambda p: p.confidence)

        # Check if pattern confirms signal direction
        pattern_confirms = (
            (strongest_pattern.signal == Signal.BULLISH and signal.action.lower() == 'buy') or
            (strongest_pattern.signal == Signal.BEARISH and signal.action.lower() == 'sell')
        )

        if pattern_confirms:
            # Boost confidence by pattern confirmation
            confidence_boost = strongest_pattern.confidence * 0.1  # Up to 10% boost
            signal.confidence = min(1.0, signal.confidence + confidence_boost)

            # Update reasoning with pattern info
            pattern_desc = f"{strongest_pattern.pattern_type.value.replace('_', ' ').title()} ({strongest_pattern.timeframe})"
            signal.reasoning += f" | Confirmed by {pattern_desc} pattern (confidence: {strongest_pattern.confidence:.2f})"

            # Update target/stop if pattern provides better levels
            if strongest_pattern.target_price and strongest_pattern.target_price > signal.entry_price:
                signal.target_price = strongest_pattern.target_price
            if strongest_pattern.stop_loss:
                signal.stop_loss = strongest_pattern.stop_loss

            logger.info(f"Signal enhanced with {pattern_desc} pattern, confidence now {signal.confidence:.2f}")
        else:
            # Pattern contradicts signal - reduce confidence
            signal.confidence = max(0.5, signal.confidence - 0.1)
            logger.warning(f"Pattern {strongest_pattern.pattern_type.value} contradicts signal direction")

        return signal

    def _simulate_block_trades(self, contract: OptionContract) -> List[dict]:
        """
        Simulate block trades detection
        In production, this would come from real-time trade feed

        Args:
            contract: Option contract

        Returns:
            List of simulated block trades
        """
        # If volume is very high, simulate some block trades
        if contract.volume_metrics.is_very_high_volume:
            num_blocks = min(5, contract.volume_metrics.volume // 500)

            blocks = []
            for i in range(num_blocks):
                blocks.append({
                    "size": np.random.randint(100, 500),
                    "price": contract.pricing.mark * (1 + np.random.uniform(-0.05, 0.05)),
                    "side": "buy" if np.random.random() > 0.5 else "sell",
                    "timestamp": datetime.now()
                })

            return blocks

        return []

    def get_top_signals(
        self,
        watchlist: List[str],
        max_signals: int = 10,
        min_confidence: float = 0.80
    ) -> List[OptionsSignal]:
        """
        Get top trading signals above confidence threshold

        Args:
            watchlist: Symbols to scan
            max_signals: Maximum number of signals to return
            min_confidence: Minimum confidence threshold

        Returns:
            List of top signals
        """
        all_signals = self.scan_for_signals(watchlist)

        # Filter by confidence
        high_confidence_signals = [
            s for s in all_signals
            if s.confidence >= min_confidence
        ]

        # Return top N
        return high_confidence_signals[:max_signals]
