"""
Trading signal detection logic
Detects patterns: ORB, VWAP reclaim/reject, EMA trends, HOD/LOD breaks
"""
import logging
from typing import Optional, List
from datetime import datetime, timedelta
from models import MarketData, SignalType, detect_asset_type, AssetType
from market_data import MarketDataService

logger = logging.getLogger(__name__)


class SignalDetector:
    """Detects trading patterns in real-time market data"""

    def __init__(self, market_service: MarketDataService):
        self.market_service = market_service
        self.orb_cache = {}  # Cache opening range for each ticker

    def detect_signals(self, ticker: str) -> List[dict]:
        """
        Detect all possible signals for a ticker

        Args:
            ticker: Stock symbol

        Returns:
            List of detected signals (raw, before AI analysis)
        """
        data = self.market_service.get_latest_data(ticker)
        if not data:
            return []

        signals = []

        # Check each pattern type
        if signal := self._check_vwap_reclaim(data):
            signals.append(signal)

        if signal := self._check_vwap_reject(data):
            signals.append(signal)

        if signal := self._check_ema_trend(data):
            signals.append(signal)

        if signal := self._check_orb_breakout(data):
            signals.append(signal)

        if signal := self._check_orb_breakdown(data):
            signals.append(signal)

        return signals

    def _check_vwap_reclaim(self, data: MarketData) -> Optional[dict]:
        """
        Detect VWAP reclaim pattern (price crosses above VWAP)

        Criteria:
        - Price was below VWAP recently
        - Price now above VWAP
        - Volume above average (relaxed for crypto)
        - EMAs aligned bullishly (relaxed for crypto)
        """
        # Check if price is above VWAP (with small buffer)
        if data.price <= data.vwap * 1.001:
            return None

        # Detect if crypto for relaxed rules
        is_crypto = detect_asset_type(data.ticker) == AssetType.CRYPTO

        # Check EMA alignment (bullish) - RELAXED for crypto (only need 2 of 3 aligned)
        if is_crypto:
            ema_bullish = (data.ema9 > data.ema20) or (data.ema20 > data.ema50)
        else:
            ema_bullish = (data.ema9 > data.ema20 and data.ema20 > data.ema50)

        if not ema_bullish:
            return None

        # Check volume - RELAXED for crypto (only need average volume, not 1.2x)
        avg_volume = self.market_service.get_average_volume(data.ticker)
        volume_threshold = avg_volume * 0.8 if is_crypto else avg_volume * 1.2
        if avg_volume == 0 or data.volume < volume_threshold:
            return None

        return {
            "ticker": data.ticker,
            "signal_type": SignalType.VWAP_RECLAIM_LONG,
            "market_data": data,
            "pattern_detected": f"VWAP Reclaim: Price ${data.price:.2f} crossed above VWAP ${data.vwap:.2f} with {data.volume/avg_volume:.1f}x volume"
        }

    def _check_vwap_reject(self, data: MarketData) -> Optional[dict]:
        """
        Detect VWAP rejection pattern (price rejected at VWAP, moving down)

        Criteria:
        - Price below VWAP
        - Price attempted to cross VWAP but failed
        - Volume elevated
        - EMAs aligned bearishly
        """
        # Check if price is below VWAP
        if data.price >= data.vwap * 0.999:
            return None

        # Check EMA alignment (bearish)
        if not (data.ema9 < data.ema20 and data.ema20 < data.ema50):
            return None

        # Check volume
        avg_volume = self.market_service.get_average_volume(data.ticker)
        if avg_volume == 0 or data.volume < avg_volume * 1.2:
            return None

        return {
            "ticker": data.ticker,
            "signal_type": SignalType.VWAP_REJECT_PUT,
            "market_data": data,
            "pattern_detected": f"VWAP Rejection: Price ${data.price:.2f} rejected at VWAP ${data.vwap:.2f} with elevated volume"
        }

    def _check_ema_trend(self, data: MarketData) -> Optional[dict]:
        """
        Detect EMA trend continuation (all EMAs aligned, price above all)

        Criteria:
        - EMA9 > EMA20 > EMA50 (bullish alignment) - RELAXED for crypto
        - Price above EMA9
        - Strong momentum
        """
        # Detect if crypto for relaxed rules
        is_crypto = detect_asset_type(data.ticker) == AssetType.CRYPTO

        # Check EMA alignment - RELAXED for crypto (only need 9 > 20 OR price above 9)
        if is_crypto:
            ema_aligned = (data.ema9 > data.ema20) or (data.price > data.ema9 * 1.002)
        else:
            ema_aligned = (data.ema9 > data.ema20 > data.ema50)

        if not ema_aligned:
            return None

        # Price must be above EMA9 (or very close for crypto)
        price_threshold = data.ema9 * 0.998 if is_crypto else data.ema9
        if data.price <= price_threshold:
            return None

        # Check spacing between EMAs (trending, not consolidating) - RELAXED for crypto
        ema_spread = (data.ema9 - data.ema50) / data.ema50
        min_spread = 0.002 if is_crypto else 0.005  # Crypto: 0.2% spread, Stocks: 0.5%
        if ema_spread < min_spread:
            return None

        return {
            "ticker": data.ticker,
            "signal_type": SignalType.EMA_TREND_LONG,
            "market_data": data,
            "pattern_detected": f"EMA Trend: Price ${data.price:.2f} > EMA9 ${data.ema9:.2f} > EMA20 ${data.ema20:.2f} > EMA50 ${data.ema50:.2f}"
        }

    def _check_orb_breakout(self, data: MarketData) -> Optional[dict]:
        """
        Detect Opening Range Breakout (first 5-min high broken)

        Criteria:
        - Past 9:35 AM (after opening range established)
        - Price breaks above opening range high
        - Volume surge
        """
        # Check if we're past opening range (9:30-9:35 AM ET)
        current_hour = data.timestamp.hour
        current_minute = data.timestamp.minute

        # Only detect after 9:35 AM ET
        if current_hour < 9 or (current_hour == 9 and current_minute < 35):
            return None

        # Cache opening range if not already cached
        if data.ticker not in self.orb_cache:
            # In production, you'd fetch the actual 9:30-9:35 range
            # For now, use a simple heuristic: assume we have it
            return None

        orb_high = self.orb_cache.get(data.ticker, {}).get('high', data.high)

        # Check if price broke above ORB high
        if data.price <= orb_high:
            return None

        # Check volume
        avg_volume = self.market_service.get_average_volume(data.ticker)
        if avg_volume == 0 or data.volume < avg_volume * 1.5:
            return None

        return {
            "ticker": data.ticker,
            "signal_type": SignalType.ORB_BREAKOUT_LONG,
            "market_data": data,
            "pattern_detected": f"ORB Breakout: Price ${data.price:.2f} broke above opening range high ${orb_high:.2f} with volume surge"
        }

    def _check_orb_breakdown(self, data: MarketData) -> Optional[dict]:
        """
        Detect Opening Range Breakdown (first 5-min low broken)

        Criteria:
        - Past 9:35 AM ET
        - Price breaks below opening range low
        - Volume surge
        """
        current_hour = data.timestamp.hour
        current_minute = data.timestamp.minute

        if current_hour < 9 or (current_hour == 9 and current_minute < 35):
            return None

        if data.ticker not in self.orb_cache:
            return None

        orb_low = self.orb_cache.get(data.ticker, {}).get('low', data.low)

        if data.price >= orb_low:
            return None

        avg_volume = self.market_service.get_average_volume(data.ticker)
        if avg_volume == 0 or data.volume < avg_volume * 1.5:
            return None

        return {
            "ticker": data.ticker,
            "signal_type": SignalType.ORB_BREAKDOWN_PUT,
            "market_data": data,
            "pattern_detected": f"ORB Breakdown: Price ${data.price:.2f} broke below opening range low ${orb_low:.2f} with volume surge"
        }

    def update_opening_range(self, ticker: str, high: float, low: float):
        """
        Manually update opening range for a ticker
        Called after 9:35 AM ET with the 9:30-9:35 range

        Args:
            ticker: Stock symbol
            high: Opening range high
            low: Opening range low
        """
        self.orb_cache[ticker] = {'high': high, 'low': low}
        logger.info(f"ORB set for {ticker}: High ${high:.2f}, Low ${low:.2f}")
