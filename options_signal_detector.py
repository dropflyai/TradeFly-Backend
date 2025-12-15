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
"""
import logging
from typing import List, Optional
from datetime import datetime
import numpy as np
import pandas as pd
import yfinance as yf

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
from market_data_polygon import PolygonMarketDataService
from candlestick_patterns import CandlestickPatternDetector, PatternType, Signal

logger = logging.getLogger(__name__)


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
        market_data_api: PolygonMarketDataService,
        account_balance: float = 10000.0
    ):
        self.options_api = options_api
        self.market_data_api = market_data_api
        self.account_balance = account_balance
        self.risk_manager = RiskManager()
        self.ta = TechnicalAnalysis()
        self.pattern_detector = CandlestickPatternDetector()

        logger.info("Options Signal Detector initialized with candlestick pattern recognition")

    def scan_for_signals(
        self,
        watchlist: List[str],
        strategies: List[StrategyType] = None
    ) -> List[OptionsSignal]:
        """
        Scan watchlist for trading opportunities

        Args:
            watchlist: List of symbols to scan (e.g., ["NVDA", "TSLA", "AAPL"])
            strategies: Strategies to run (defaults to all)

        Returns:
            List of OptionsSignal objects
        """
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
        Get REAL price history for underlying stock using yfinance

        Args:
            symbol: Stock symbol

        Returns:
            Dictionary with price arrays and DataFrames for different timeframes
        """
        try:
            # Fetch real intraday data from yfinance (FREE)
            ticker = yf.Ticker(symbol)

            # Get 1-minute bars for last 60 minutes (for scalping)
            df_1m = ticker.history(period='1d', interval='1m')

            # Get 15-minute bars for momentum
            df_15m = ticker.history(period='5d', interval='15m')

            # Get 1-hour bars for swing trading
            df_1h = ticker.history(period='1mo', interval='1h')

            # Get daily bars for swing trading and candlestick patterns
            df_daily = ticker.history(period='3mo', interval='1d')

            if df_1m.empty:
                logger.warning(f"No price history available for {symbol}")
                return None

            # Extract close prices as numpy arrays
            prices_1m = df_1m['Close'].values[-100:] if len(df_1m) > 0 else np.array([])
            prices_15m = df_15m['Close'].values[-50:] if len(df_15m) > 0 else np.array([])
            volumes_15m = df_15m['Volume'].values[-50:] if len(df_15m) > 0 else np.array([])
            prices_1h = df_1h['Close'].values[-50:] if len(df_1h) > 0 else np.array([])
            prices_daily = df_daily['Close'].values[-30:] if len(df_daily) > 0 else np.array([])

            logger.info(f"Fetched REAL price data for {symbol}: {len(prices_1m)} 1m bars, {len(prices_15m)} 15m bars, {len(prices_1h)} 1h bars, {len(prices_daily)} daily bars")

            return {
                "1m": prices_1m,
                "15m": prices_15m,
                "15m_volume": volumes_15m,
                "1h": prices_1h,
                "daily": prices_daily,
                # Include DataFrames for candlestick pattern detection
                "df_1m": df_1m,
                "df_15m": df_15m,
                "df_1h": df_1h,
                "df_daily": df_daily
            }

        except Exception as e:
            logger.error(f"Error getting price history for {symbol}: {e}")
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
