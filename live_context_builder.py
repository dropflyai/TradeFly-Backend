"""
Live Context Builder
Constructs real-time market context for GPT-5 analysis
Injects LIVE data: current prices, SPY trend, time of day, key levels, NEWS
"""
import logging
from datetime import datetime, time
from typing import Dict, List, Optional, Tuple
import pandas as pd
from models import MarketData
from market_data import MarketDataService

logger = logging.getLogger(__name__)


class LiveContextBuilder:
    """Builds real-time context for signal analysis"""

    def __init__(self, market_service: MarketDataService, news_service=None):
        self.market_service = market_service
        self.news_service = news_service

    async def build_analysis_context(self, signal_data: dict, data_5m: Optional[MarketData] = None,
                               data_daily: Optional[MarketData] = None) -> str:
        """
        Build comprehensive real-time context for GPT-5 analysis

        Args:
            signal_data: Dict with ticker, signal_type, market_data, pattern_detected
            data_5m: Optional 5-minute timeframe data
            data_daily: Optional daily timeframe data

        Returns:
            Formatted context string with all live market data
        """
        data = signal_data['market_data']

        # Get current time
        now = datetime.now()

        # Get SPY data for market context
        spy_data = self.market_service.get_latest_data("SPY")

        # Get key levels
        levels = self._get_key_levels(data.ticker, data)

        # Get news if news service available
        news_summary = ""
        market_news_summary = ""
        if self.news_service:
            try:
                # Get stock-specific news
                stock_news = await self.news_service.get_stock_news(data.ticker, hours_back=2)
                if stock_news:
                    news_summary = self.news_service.create_news_summary(data.ticker, stock_news)

                # Get market-wide news
                market_news = await self.news_service.get_market_news(hours_back=4)
                if market_news:
                    market_news_summary = self.news_service.create_market_news_summary(market_news)
            except Exception as e:
                logger.error(f"Error fetching news: {e}")

        # Build the context
        context = f"""
═══════════════════════════════════════════════════════════
LIVE SIGNAL ANALYSIS REQUEST
═══════════════════════════════════════════════════════════

TIMESTAMP: {now.strftime('%I:%M:%S %p ET')} on {now.strftime('%A, %B %d, %Y')}

TICKER: {data.ticker}
SIGNAL TYPE: {signal_data['signal_type']}
PATTERN DETECTED: {signal_data['pattern_detected']}

═══════════════════════════════════════════════════════════
CURRENT MARKET DATA (1-MINUTE TIMEFRAME)
═══════════════════════════════════════════════════════════

Price Action:
• Current Price: ${data.price:.2f}
• Open:  ${data.open:.2f}
• High:  ${data.high:.2f}
• Low:   ${data.low:.2f}
• Range: ${data.high - data.low:.2f} ({self._calculate_percent(data.high - data.low, data.low):.2f}%)

Technical Indicators:
• VWAP:  ${data.vwap:.2f} (Price is {self._calculate_percent(data.price - data.vwap, data.vwap):+.2f}% from VWAP)
  └─ Price {self._get_position_text(data.price, data.vwap)} VWAP
• EMA9:  ${data.ema9:.2f} (Price is {self._calculate_percent(data.price - data.ema9, data.ema9):+.2f}% from EMA9)
• EMA20: ${data.ema20:.2f} (Price is {self._calculate_percent(data.price - data.ema20, data.ema20):+.2f}% from EMA20)
• EMA50: ${data.ema50:.2f} (Price is {self._calculate_percent(data.price - data.ema50, data.ema50):+.2f}% from EMA50)

EMA Alignment (1-minute):
{self._analyze_ema_alignment(data.ema9, data.ema20, data.ema50)}

Volume Analysis:
• Current Volume: {data.volume:,}
• Average Volume (20-period): {self.market_service.get_average_volume(data.ticker):,}
• Volume Ratio: {self._calculate_volume_ratio(data.volume, data.ticker):.2f}x average
• Assessment: {self._assess_volume(data.volume, data.ticker)}

Candle Analysis:
{self._analyze_current_candle(data)}

═══════════════════════════════════════════════════════════
MULTI-TIMEFRAME ANALYSIS
═══════════════════════════════════════════════════════════

{self._build_5min_analysis(data_5m) if data_5m else "5-minute data not available"}

{self._build_daily_analysis(data_daily) if data_daily else "Daily data not available"}

═══════════════════════════════════════════════════════════
MARKET CONTEXT (LIVE)
═══════════════════════════════════════════════════════════

{self._build_spy_context(spy_data) if spy_data else "SPY data not available"}

Time of Day Analysis:
{self._analyze_time_of_day(now)}

═══════════════════════════════════════════════════════════
KEY PRICE LEVELS (CALCULATED FROM TODAY'S DATA)
═══════════════════════════════════════════════════════════

{self._format_key_levels(levels, data.price)}

{news_summary if news_summary else ""}

{market_news_summary if market_news_summary else ""}

═══════════════════════════════════════════════════════════
ANALYSIS REQUIRED
═══════════════════════════════════════════════════════════

Using the TradeFly Expert Trading System rules (provided in system prompt):

1. Systematically check ALL 10 core rules
2. List each confirmation that is MET
3. List each confirmation that is MISSING or FAILED
4. Rate the signal as HIGH, MEDIUM, or LOW based on criteria
5. Calculate precise entry, stop loss, and take profit prices
6. Provide realistic win probability estimate
7. Explain your reasoning in detail

Remember:
• Be BRUTALLY selective - only 5-10% should be HIGH quality
• Protect user capital - when in doubt, rate lower
• List ALL failed confirmations honestly
• Calculate exact risk/reward ratio
• Consider real-time market conditions

Analyze this signal now.
"""
        return context

    def _calculate_percent(self, value: float, base: float) -> float:
        """Calculate percentage difference"""
        if base == 0:
            return 0
        return (value / base) * 100

    def _get_position_text(self, price: float, level: float) -> str:
        """Get text describing price position relative to level"""
        return "ABOVE" if price > level else "BELOW" if price < level else "AT"

    def _calculate_volume_ratio(self, current_volume: int, ticker: str) -> float:
        """Calculate current volume vs average"""
        avg = self.market_service.get_average_volume(ticker)
        if avg == 0:
            return 1.0
        return current_volume / avg

    def _assess_volume(self, current_volume: int, ticker: str) -> str:
        """Assess volume quality"""
        ratio = self._calculate_volume_ratio(current_volume, ticker)
        if ratio >= 2.0:
            return "STRONG (≥2x average) ✓"
        elif ratio >= 1.5:
            return "ADEQUATE (≥1.5x average) ✓"
        elif ratio >= 1.0:
            return "WEAK (<1.5x average) ✗"
        else:
            return "VERY WEAK (<1x average) ✗"

    def _analyze_ema_alignment(self, ema9: float, ema20: float, ema50: float) -> str:
        """Analyze EMA alignment and trend"""
        if ema9 > ema20 > ema50:
            spread = ((ema9 - ema50) / ema50) * 100
            return f"✓ BULLISH ALIGNMENT (EMA9 > EMA20 > EMA50)\n  └─ Spread: {spread:.2f}% (wider = stronger trend)"
        elif ema9 < ema20 < ema50:
            spread = ((ema50 - ema9) / ema50) * 100
            return f"✗ BEARISH ALIGNMENT (EMA9 < EMA20 < EMA50)\n  └─ Spread: {spread:.2f}%"
        else:
            return f"⚠ MIXED ALIGNMENT (no clear trend)\n  └─ EMA9: ${ema9:.2f}, EMA20: ${ema20:.2f}, EMA50: ${ema50:.2f}"

    def _analyze_current_candle(self, data: MarketData) -> str:
        """Analyze current candle pattern"""
        body = abs(data.price - data.open)
        total_range = data.high - data.low

        if total_range == 0:
            return "• Candle Type: Doji (indecision)"

        body_percent = (body / total_range) * 100
        upper_wick = data.high - max(data.open, data.price)
        lower_wick = min(data.open, data.price) - data.low

        candle_type = "GREEN (Bullish)" if data.price > data.open else "RED (Bearish)"
        close_position = ((data.price - data.low) / total_range) * 100 if total_range > 0 else 50

        analysis = f"""• Candle Type: {candle_type}
• Body Size: {body_percent:.1f}% of total range
• Close Position: {close_position:.1f}% of range (100% = high, 0% = low)
• Upper Wick: ${upper_wick:.2f}
• Lower Wick: ${lower_wick:.2f}"""

        # Identify patterns
        if lower_wick > body * 2:
            analysis += "\n• Pattern: HAMMER (long lower wick = rejection of lows) ✓"
        if upper_wick > body * 2:
            analysis += "\n• Pattern: SHOOTING STAR (long upper wick = rejection of highs)"
        if close_position > 75 and data.price > data.open:
            analysis += "\n• Pattern: STRONG BULLISH CLOSE (closed near high) ✓"

        return analysis

    def _build_5min_analysis(self, data_5m: Optional[MarketData]) -> str:
        """Build 5-minute timeframe analysis"""
        if not data_5m:
            return "5-MINUTE TIMEFRAME: Data not available"

        ema_alignment = self._analyze_ema_alignment(data_5m.ema9, data_5m.ema20, data_5m.ema50)

        return f"""5-MINUTE TIMEFRAME:
• Current Price: ${data_5m.price:.2f}
• VWAP: ${data_5m.vwap:.2f}
• EMA Alignment:
{ema_alignment}
• Trend Assessment: {self._assess_trend(data_5m)}"""

    def _build_daily_analysis(self, data_daily: Optional[MarketData]) -> str:
        """Build daily timeframe analysis"""
        if not data_daily:
            return "DAILY TIMEFRAME: Data not available"

        # For daily, we'd typically check 200 EMA
        ema200_text = f"${data_daily.ema50:.2f}" if data_daily.ema50 else "N/A"
        above_ema = data_daily.price > data_daily.ema50 if data_daily.ema50 else False

        return f"""DAILY TIMEFRAME:
• Current Price: ${data_daily.price:.2f}
• Major EMA (50-day): {ema200_text}
• Position: Price is {"ABOVE" if above_ema else "BELOW"} daily EMA
• Trend: {"UPTREND ✓" if above_ema else "DOWNTREND ✗"}
• Assessment: {"Supports LONG signals" if above_ema else "Supports PUT signals"}"""

    def _assess_trend(self, data: MarketData) -> str:
        """Assess trend direction"""
        if data.ema9 > data.ema20 > data.ema50:
            return "UPTREND (all EMAs aligned bullish)"
        elif data.ema9 < data.ema20 < data.ema50:
            return "DOWNTREND (all EMAs aligned bearish)"
        else:
            return "SIDEWAYS/CHOPPY (mixed EMA signals)"

    def _build_spy_context(self, spy_data: Optional[MarketData]) -> str:
        """Build SPY market context"""
        if not spy_data:
            return "SPY (S&P 500): Data not available"

        day_change = spy_data.price - spy_data.open
        day_change_pct = (day_change / spy_data.open) * 100 if spy_data.open > 0 else 0

        above_vwap = spy_data.price > spy_data.vwap
        trend = "BULLISH ✓" if day_change_pct > 0 else "BEARISH ✗"

        # Assess impact on signals
        if day_change_pct > 0.5:
            impact = "VERY SUPPORTIVE of LONG signals"
        elif day_change_pct > 0:
            impact = "SUPPORTIVE of LONG signals"
        elif day_change_pct > -0.5:
            impact = "NEUTRAL (slight headwind for LONGS)"
        else:
            impact = "HEADWIND for LONG signals (consider only PUTS)"

        return f"""SPY (S&P 500) - Market Context:
• Current Price: ${spy_data.price:.2f}
• Day Change: ${day_change:+.2f} ({day_change_pct:+.2f}%)
• vs VWAP: {"ABOVE ✓" if above_vwap else "BELOW ✗"} (${spy_data.vwap:.2f})
• Trend: {trend}
• Impact on Signals: {impact}

RULE CHECK:
• For LONG signals: {"Can rate HIGH ✓" if day_change_pct > 0 else "Max MEDIUM ⚠" if day_change_pct > -0.5 else "Max LOW ✗"}
• For PUT signals: {"Can rate HIGH ✓" if day_change_pct < 0 else "Max MEDIUM ⚠"}"""

    def _analyze_time_of_day(self, now: datetime) -> str:
        """Analyze current time and trading session quality"""
        hour = now.hour
        minute = now.minute
        current_time = time(hour, minute)

        # Define sessions
        morning_start = time(9, 30)
        morning_end = time(11, 30)
        lunch_start = time(11, 30)
        lunch_end = time(14, 0)
        power_start = time(14, 0)
        power_end = time(16, 0)
        close = time(16, 0)

        if current_time < morning_start:
            session = "PRE-MARKET"
            quality = "LOW - Pre-market is too risky, max LOW rating"
        elif morning_start <= current_time < morning_end:
            session = "MORNING SESSION (Premium Hours)"
            quality = "EXCELLENT - Best time for trading, can rate HIGH ✓"
        elif lunch_start <= current_time < lunch_end:
            session = "LUNCH HOUR"
            quality = "POOR - Choppy, low conviction, max MEDIUM rating ⚠"
        elif power_start <= current_time < time(15, 30):
            session = "POWER HOUR"
            quality = "GOOD - Institutional activity, can rate HIGH ✓"
        elif time(15, 30) <= current_time < close:
            session = "LATE AFTERNOON"
            quality = "POOR - Low liquidity, erratic, max MEDIUM rating ⚠"
        else:
            session = "AFTER HOURS"
            quality = "LOW - After hours too risky, max LOW rating ✗"

        return f"""• Current Time: {now.strftime('%I:%M %p ET')}
• Trading Session: {session}
• Quality Assessment: {quality}

RULE CHECK:
• Can this signal be rated HIGH? {("YES ✓" if "EXCELLENT" in quality or "GOOD" in quality else "NO ✗")}"""

    def _get_key_levels(self, ticker: str, data: MarketData) -> Dict[str, List[float]]:
        """
        Calculate key support and resistance levels
        Uses previous day high/low, VWAP, and round numbers
        """
        levels = {
            "resistance": [],
            "support": []
        }

        # Add previous day levels (would need historical data - simplified here)
        # In production, fetch actual previous day high/low
        prev_day_high = data.high * 1.01  # Placeholder
        prev_day_low = data.low * 0.99    # Placeholder

        levels["resistance"].append(prev_day_high)
        levels["support"].append(prev_day_low)

        # Add VWAP as a level
        if data.price > data.vwap:
            levels["support"].append(data.vwap)
        else:
            levels["resistance"].append(data.vwap)

        # Add major EMAs as levels
        levels["support"].append(data.ema20)
        levels["support"].append(data.ema50)

        # Add round number levels
        current_round = round(data.price)
        levels["resistance"].append(current_round + 1)
        levels["support"].append(current_round - 1)

        # Sort levels
        levels["resistance"] = sorted(set(levels["resistance"]), reverse=True)
        levels["support"] = sorted(set(levels["support"]), reverse=True)

        return levels

    def _format_key_levels(self, levels: Dict[str, List[float]], current_price: float) -> str:
        """Format key levels for display"""
        output = "Resistance Levels (above current price):\n"
        for level in levels["resistance"][:3]:  # Top 3
            if level > current_price:
                distance = ((level - current_price) / current_price) * 100
                output += f"• ${level:.2f} (+{distance:.2f}% away)\n"

        output += "\nSupport Levels (below current price):\n"
        for level in levels["support"][:3]:  # Top 3
            if level < current_price:
                distance = ((current_price - level) / current_price) * 100
                output += f"• ${level:.2f} (-{distance:.2f}% away)\n"

        # Check if near key level
        nearest_level, distance = self._find_nearest_level(current_price, levels)
        if distance < 0.3:  # Within 0.3%
            output += f"\n✓ NEAR KEY LEVEL: Current price ${current_price:.2f} is {distance:.2f}% from ${nearest_level:.2f}"
        else:
            output += f"\n✗ NOT NEAR KEY LEVEL: Nearest level ${nearest_level:.2f} is {distance:.2f}% away (need <0.3%)"

        return output

    def _find_nearest_level(self, price: float, levels: Dict[str, List[float]]) -> Tuple[float, float]:
        """Find nearest key level and distance to it"""
        all_levels = levels["resistance"] + levels["support"]
        if not all_levels:
            return price, 100.0

        nearest = min(all_levels, key=lambda x: abs(x - price))
        distance = abs((price - nearest) / price) * 100

        return nearest, distance
