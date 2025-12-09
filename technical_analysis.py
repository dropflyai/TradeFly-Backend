"""
Technical Analysis Engine - Institutional Grade
Multi-timeframe indicator suite for options trading
"""
import numpy as np
import pandas as pd
from typing import Optional, List, Tuple
from dataclasses import dataclass


@dataclass
class PriceBar:
    """Single price bar (candle)"""
    timestamp: float
    open: float
    high: float
    low: float
    close: float
    volume: float


class TechnicalAnalysis:
    """
    Institutional-grade technical indicators
    Verified algorithms from quantitative trading
    """

    @staticmethod
    def rsi(prices: np.ndarray, period: int = 14) -> float:
        """
        Relative Strength Index - momentum oscillator

        Args:
            prices: Array of closing prices
            period: Lookback period (default 14)

        Returns:
            RSI value (0-100)
        """
        if len(prices) < period + 1:
            return 50.0  # Neutral if insufficient data

        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)

        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])

        if avg_loss == 0:
            return 100.0

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return float(rsi)

    @staticmethod
    def macd(
        prices: np.ndarray,
        fast: int = 12,
        slow: int = 26,
        signal: int = 9
    ) -> Tuple[float, float, float]:
        """
        MACD - Moving Average Convergence Divergence
        Trend and momentum indicator

        Args:
            prices: Array of closing prices
            fast: Fast EMA period
            slow: Slow EMA period
            signal: Signal line EMA period

        Returns:
            Tuple of (macd_line, signal_line, histogram)
        """
        if len(prices) < slow + signal:
            return 0.0, 0.0, 0.0

        prices_series = pd.Series(prices)

        ema_fast = prices_series.ewm(span=fast, adjust=False).mean()
        ema_slow = prices_series.ewm(span=slow, adjust=False).mean()

        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line

        return (
            float(macd_line.iloc[-1]),
            float(signal_line.iloc[-1]),
            float(histogram.iloc[-1])
        )

    @staticmethod
    def bollinger_bands(
        prices: np.ndarray,
        period: int = 20,
        std_dev: float = 2.0
    ) -> Tuple[float, float, float]:
        """
        Bollinger Bands - volatility and mean reversion

        Args:
            prices: Array of closing prices
            period: Lookback period
            std_dev: Standard deviation multiplier

        Returns:
            Tuple of (upper_band, middle_band, lower_band)
        """
        if len(prices) < period:
            current = float(prices[-1])
            return current, current, current

        sma = np.mean(prices[-period:])
        std = np.std(prices[-period:])

        upper = sma + (std_dev * std)
        lower = sma - (std_dev * std)

        return float(upper), float(sma), float(lower)

    @staticmethod
    def vwap(prices: np.ndarray, volumes: np.ndarray) -> float:
        """
        Volume Weighted Average Price

        Args:
            prices: Array of prices (typically close or typical price)
            volumes: Array of volumes

        Returns:
            VWAP value
        """
        if len(prices) == 0 or len(volumes) == 0:
            return 0.0

        total_volume = np.sum(volumes)
        if total_volume == 0:
            return float(prices[-1])

        return float(np.sum(prices * volumes) / total_volume)

    @staticmethod
    def ema(prices: np.ndarray, period: int) -> float:
        """
        Exponential Moving Average

        Args:
            prices: Array of prices
            period: EMA period

        Returns:
            Current EMA value
        """
        if len(prices) < period:
            return float(np.mean(prices))

        prices_series = pd.Series(prices)
        ema_values = prices_series.ewm(span=period, adjust=False).mean()
        return float(ema_values.iloc[-1])

    @staticmethod
    def sma(prices: np.ndarray, period: int) -> float:
        """
        Simple Moving Average

        Args:
            prices: Array of prices
            period: SMA period

        Returns:
            Current SMA value
        """
        if len(prices) < period:
            return float(np.mean(prices))

        return float(np.mean(prices[-period:]))

    @staticmethod
    def atr(bars: List[PriceBar], period: int = 14) -> float:
        """
        Average True Range - volatility measure

        Args:
            bars: List of price bars
            period: ATR period

        Returns:
            Current ATR value
        """
        if len(bars) < period + 1:
            return 0.0

        true_ranges = []
        for i in range(1, len(bars)):
            high = bars[i].high
            low = bars[i].low
            prev_close = bars[i-1].close

            tr = max(
                high - low,
                abs(high - prev_close),
                abs(low - prev_close)
            )
            true_ranges.append(tr)

        return float(np.mean(true_ranges[-period:]))

    @staticmethod
    def support_resistance_levels(
        prices: np.ndarray,
        window: int = 20,
        num_levels: int = 3
    ) -> Tuple[List[float], List[float]]:
        """
        Support and resistance levels using local extrema

        Args:
            prices: Array of prices
            window: Window for local extrema detection
            num_levels: Number of levels to return

        Returns:
            Tuple of (resistance_levels, support_levels)
        """
        if len(prices) < window * 3:
            current = float(prices[-1])
            return [current], [current]

        highs = []
        lows = []

        # Find local extrema
        for i in range(window, len(prices) - window):
            if prices[i] == max(prices[i-window:i+window]):
                highs.append(float(prices[i]))
            if prices[i] == min(prices[i-window:i+window]):
                lows.append(float(prices[i]))

        # Get top resistance and support levels
        resistance = sorted(set(highs), reverse=True)[:num_levels]
        support = sorted(set(lows))[:num_levels]

        # Ensure we have at least one level
        if not resistance:
            resistance = [float(prices[-1])]
        if not support:
            support = [float(prices[-1])]

        return resistance, support

    @staticmethod
    def momentum(prices: np.ndarray, period: int = 1) -> float:
        """
        Price momentum - percentage change

        Args:
            prices: Array of prices
            period: Lookback period (1 = last bar)

        Returns:
            Momentum as decimal (0.03 = 3%)
        """
        if len(prices) < period + 1:
            return 0.0

        current = prices[-1]
        previous = prices[-(period + 1)]

        if previous == 0:
            return 0.0

        return float((current - previous) / previous)

    @staticmethod
    def volume_ratio(current_volume: int, avg_volume: int) -> float:
        """
        Volume ratio compared to average

        Args:
            current_volume: Current period volume
            avg_volume: Average volume

        Returns:
            Volume ratio (3.0 = 3x average)
        """
        if avg_volume == 0:
            return 1.0

        return float(current_volume / avg_volume)

    @staticmethod
    def detect_pattern_breakout(
        prices: np.ndarray,
        current_price: float,
        pattern_type: str = "resistance"
    ) -> Optional[float]:
        """
        Detect if price has broken through resistance or support

        Args:
            prices: Historical prices
            current_price: Current price
            pattern_type: 'resistance' or 'support'

        Returns:
            Breakout level if detected, None otherwise
        """
        resistance, support = TechnicalAnalysis.support_resistance_levels(prices)

        if pattern_type == "resistance":
            for level in resistance:
                # Price broke above resistance with 0.5% buffer
                if current_price > level * 1.005 and prices[-2] <= level:
                    return level
        else:  # support
            for level in support:
                # Price broke below support with 0.5% buffer
                if current_price < level * 0.995 and prices[-2] >= level:
                    return level

        return None

    @staticmethod
    def calculate_typical_price(high: float, low: float, close: float) -> float:
        """
        Typical price for VWAP calculation

        Args:
            high: High price
            low: Low price
            close: Close price

        Returns:
            Typical price (H+L+C)/3
        """
        return (high + low + close) / 3.0

    @staticmethod
    def stochastic_oscillator(
        highs: np.ndarray,
        lows: np.ndarray,
        closes: np.ndarray,
        period: int = 14
    ) -> Tuple[float, float]:
        """
        Stochastic Oscillator - momentum indicator

        Args:
            highs: Array of high prices
            lows: Array of low prices
            closes: Array of close prices
            period: Lookback period

        Returns:
            Tuple of (%K, %D)
        """
        if len(closes) < period:
            return 50.0, 50.0

        highest_high = np.max(highs[-period:])
        lowest_low = np.min(lows[-period:])
        current_close = closes[-1]

        if highest_high == lowest_low:
            return 50.0, 50.0

        k = ((current_close - lowest_low) / (highest_high - lowest_low)) * 100

        # %D is 3-period SMA of %K (simplified here)
        d = k  # In production, calculate proper %D

        return float(k), float(d)

    @staticmethod
    def williams_r(
        highs: np.ndarray,
        lows: np.ndarray,
        closes: np.ndarray,
        period: int = 14
    ) -> float:
        """
        Williams %R - momentum indicator

        Args:
            highs: Array of high prices
            lows: Array of low prices
            closes: Array of close prices
            period: Lookback period

        Returns:
            Williams %R value (-100 to 0)
        """
        if len(closes) < period:
            return -50.0

        highest_high = np.max(highs[-period:])
        lowest_low = np.min(lows[-period:])
        current_close = closes[-1]

        if highest_high == lowest_low:
            return -50.0

        wr = ((highest_high - current_close) / (highest_high - lowest_low)) * -100

        return float(wr)


class MultiTimeframeAnalysis:
    """
    Analyze multiple timeframes simultaneously
    1-min, 5-min, 15-min for comprehensive view
    """

    @staticmethod
    def analyze_trend_alignment(
        prices_1m: np.ndarray,
        prices_5m: np.ndarray,
        prices_15m: np.ndarray
    ) -> dict:
        """
        Check if multiple timeframes align (strong signal)

        Returns:
            Dictionary with trend alignment analysis
        """
        ta = TechnicalAnalysis()

        # Calculate EMAs for each timeframe
        ema9_1m = ta.ema(prices_1m, 9)
        ema20_1m = ta.ema(prices_1m, 20)

        ema9_5m = ta.ema(prices_5m, 9)
        ema20_5m = ta.ema(prices_5m, 20)

        ema9_15m = ta.ema(prices_15m, 9)
        ema20_15m = ta.ema(prices_15m, 20)

        # Check bullish alignment (EMA9 > EMA20 on all timeframes)
        bullish_1m = ema9_1m > ema20_1m
        bullish_5m = ema9_5m > ema20_5m
        bullish_15m = ema9_15m > ema20_15m

        all_bullish = bullish_1m and bullish_5m and bullish_15m
        all_bearish = not bullish_1m and not bullish_5m and not bullish_15m

        return {
            "aligned": all_bullish or all_bearish,
            "direction": "bullish" if all_bullish else "bearish" if all_bearish else "mixed",
            "strength": sum([bullish_1m, bullish_5m, bullish_15m]),
            "timeframes": {
                "1m": "bullish" if bullish_1m else "bearish",
                "5m": "bullish" if bullish_5m else "bearish",
                "15m": "bullish" if bullish_15m else "bearish"
            }
        }
