"""
Candlestick Pattern Recognition Module
Professional-grade pattern detection for entry/exit signals

Implements 15+ proven candlestick patterns with confidence scoring
"""
import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class PatternType(Enum):
    """Candlestick pattern types"""
    # Reversal Patterns
    HAMMER = "hammer"
    INVERTED_HAMMER = "inverted_hammer"
    HANGING_MAN = "hanging_man"
    SHOOTING_STAR = "shooting_star"
    BULLISH_ENGULFING = "bullish_engulfing"
    BEARISH_ENGULFING = "bearish_engulfing"
    MORNING_STAR = "morning_star"
    EVENING_STAR = "evening_star"
    PIERCING_LINE = "piercing_line"
    DARK_CLOUD_COVER = "dark_cloud_cover"

    # Continuation Patterns
    THREE_WHITE_SOLDIERS = "three_white_soldiers"
    THREE_BLACK_CROWS = "three_black_crows"
    RISING_THREE_METHODS = "rising_three_methods"
    FALLING_THREE_METHODS = "falling_three_methods"

    # Indecision Patterns
    DOJI = "doji"
    DRAGONFLY_DOJI = "dragonfly_doji"
    GRAVESTONE_DOJI = "gravestone_doji"

    # Strong Momentum
    MARUBOZU_BULLISH = "marubozu_bullish"
    MARUBOZU_BEARISH = "marubozu_bearish"

    # Two-Candle Patterns
    TWEEZER_TOP = "tweezer_top"
    TWEEZER_BOTTOM = "tweezer_bottom"
    HARAMI_BULLISH = "harami_bullish"
    HARAMI_BEARISH = "harami_bearish"


class Signal(Enum):
    """Trading signal direction"""
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"


@dataclass
class CandlestickPattern:
    """Detected candlestick pattern"""
    pattern_type: PatternType
    signal: Signal
    confidence: float  # 0.0 to 1.0
    description: str
    candle_index: int  # Index in the dataframe where pattern was detected
    support_level: Optional[float] = None
    resistance_level: Optional[float] = None
    target_price: Optional[float] = None
    stop_loss: Optional[float] = None


class CandlestickPatternDetector:
    """
    Detects candlestick patterns in price data

    Professional-grade pattern recognition with:
    - 15+ proven patterns
    - Confidence scoring
    - Support/resistance levels
    - Entry/exit recommendations
    """

    def __init__(self, min_confidence: float = 0.6):
        """
        Initialize pattern detector

        Args:
            min_confidence: Minimum confidence threshold (0.0-1.0)
        """
        self.min_confidence = min_confidence

    def detect_patterns(self, df: pd.DataFrame) -> List[CandlestickPattern]:
        """
        Detect all patterns in price data

        Args:
            df: DataFrame with OHLCV columns (open, high, low, close, volume)

        Returns:
            List of detected patterns sorted by confidence
        """
        if len(df) < 3:
            return []

        patterns = []

        # Add calculated fields
        df = self._prepare_dataframe(df)

        # Detect all pattern types
        patterns.extend(self._detect_doji_patterns(df))
        patterns.extend(self._detect_hammer_patterns(df))
        patterns.extend(self._detect_engulfing_patterns(df))
        patterns.extend(self._detect_star_patterns(df))
        patterns.extend(self._detect_soldiers_crows_patterns(df))
        patterns.extend(self._detect_marubozu_patterns(df))
        patterns.extend(self._detect_harami_patterns(df))
        patterns.extend(self._detect_tweezer_patterns(df))
        patterns.extend(self._detect_piercing_patterns(df))

        # Filter by confidence and sort
        patterns = [p for p in patterns if p.confidence >= self.min_confidence]
        patterns.sort(key=lambda x: x.confidence, reverse=True)

        logger.info(f"Detected {len(patterns)} candlestick patterns (min confidence: {self.min_confidence})")

        return patterns

    def _prepare_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add calculated fields for pattern detection"""
        df = df.copy()

        # Body size (abs difference between open and close)
        df['body'] = abs(df['close'] - df['open'])

        # Upper shadow (high - max(open, close))
        df['upper_shadow'] = df['high'] - df[['open', 'close']].max(axis=1)

        # Lower shadow (min(open, close) - low)
        df['lower_shadow'] = df[['open', 'close']].min(axis=1) - df['low']

        # Total range
        df['range'] = df['high'] - df['low']

        # Bullish/bearish
        df['bullish'] = df['close'] > df['open']

        # Average body size (for comparison)
        df['avg_body'] = df['body'].rolling(window=10, min_periods=1).mean()

        # Average range (for comparison)
        df['avg_range'] = df['range'].rolling(window=10, min_periods=1).mean()

        return df

    def _detect_doji_patterns(self, df: pd.DataFrame) -> List[CandlestickPattern]:
        """Detect Doji patterns (indecision)"""
        patterns = []

        for i in range(1, len(df)):
            candle = df.iloc[i]
            prev_candle = df.iloc[i-1]

            # Doji: body is very small relative to range
            body_ratio = candle['body'] / candle['range'] if candle['range'] > 0 else 0

            if body_ratio < 0.1:  # Body is less than 10% of total range
                # Regular Doji
                if 0.3 < (candle['upper_shadow'] / candle['range']) < 0.7:
                    confidence = 1.0 - body_ratio  # Smaller body = higher confidence

                    # Determine signal based on trend
                    signal = Signal.NEUTRAL
                    if i >= 3:
                        trend = self._determine_trend(df, i, lookback=3)
                        if trend == "downtrend":
                            signal = Signal.BULLISH  # Doji in downtrend = potential reversal
                        elif trend == "uptrend":
                            signal = Signal.BEARISH  # Doji in uptrend = potential reversal

                    patterns.append(CandlestickPattern(
                        pattern_type=PatternType.DOJI,
                        signal=signal,
                        confidence=min(confidence, 0.85),
                        description="Doji - Market indecision, potential reversal",
                        candle_index=i,
                        support_level=candle['low'],
                        resistance_level=candle['high']
                    ))

                # Dragonfly Doji (long lower shadow, little/no upper shadow)
                elif candle['lower_shadow'] > candle['range'] * 0.7:
                    confidence = min(candle['lower_shadow'] / candle['range'], 0.95)

                    patterns.append(CandlestickPattern(
                        pattern_type=PatternType.DRAGONFLY_DOJI,
                        signal=Signal.BULLISH,
                        confidence=confidence,
                        description="Dragonfly Doji - Bullish reversal after rejection of lows",
                        candle_index=i,
                        support_level=candle['low'],
                        stop_loss=candle['low'] * 0.98
                    ))

                # Gravestone Doji (long upper shadow, little/no lower shadow)
                elif candle['upper_shadow'] > candle['range'] * 0.7:
                    confidence = min(candle['upper_shadow'] / candle['range'], 0.95)

                    patterns.append(CandlestickPattern(
                        pattern_type=PatternType.GRAVESTONE_DOJI,
                        signal=Signal.BEARISH,
                        confidence=confidence,
                        description="Gravestone Doji - Bearish reversal after rejection of highs",
                        candle_index=i,
                        resistance_level=candle['high'],
                        stop_loss=candle['high'] * 1.02
                    ))

        return patterns

    def _detect_hammer_patterns(self, df: pd.DataFrame) -> List[CandlestickPattern]:
        """Detect Hammer and related patterns"""
        patterns = []

        for i in range(1, len(df)):
            candle = df.iloc[i]

            # Hammer characteristics:
            # - Small body at top of range
            # - Long lower shadow (2x+ body)
            # - Little/no upper shadow

            if candle['range'] == 0:
                continue

            body_position = (candle['high'] - max(candle['open'], candle['close'])) / candle['range']
            lower_shadow_ratio = candle['lower_shadow'] / candle['body'] if candle['body'] > 0 else float('inf')
            upper_shadow_ratio = candle['upper_shadow'] / candle['lower_shadow'] if candle['lower_shadow'] > 0 else 0

            # Hammer (bullish reversal)
            if (body_position < 0.3 and  # Body near top
                lower_shadow_ratio >= 2.0 and  # Long lower shadow
                upper_shadow_ratio < 0.3):  # Small upper shadow

                trend = self._determine_trend(df, i, lookback=5)
                confidence = 0.7 if trend == "downtrend" else 0.5
                confidence += min((lower_shadow_ratio - 2.0) * 0.1, 0.2)

                patterns.append(CandlestickPattern(
                    pattern_type=PatternType.HAMMER,
                    signal=Signal.BULLISH,
                    confidence=min(confidence, 0.95),
                    description="Hammer - Bullish reversal, buyers rejected lows",
                    candle_index=i,
                    support_level=candle['low'],
                    target_price=candle['close'] + (candle['close'] - candle['low']) * 2,
                    stop_loss=candle['low'] * 0.98
                ))

            # Inverted Hammer (bullish reversal)
            elif (body_position > 0.7 and  # Body near bottom
                  candle['upper_shadow'] >= candle['body'] * 2.0 and  # Long upper shadow
                  candle['lower_shadow'] < candle['upper_shadow'] * 0.3):  # Small lower shadow

                trend = self._determine_trend(df, i, lookback=5)
                confidence = 0.65 if trend == "downtrend" else 0.45

                patterns.append(CandlestickPattern(
                    pattern_type=PatternType.INVERTED_HAMMER,
                    signal=Signal.BULLISH,
                    confidence=min(confidence, 0.90),
                    description="Inverted Hammer - Potential bullish reversal, needs confirmation",
                    candle_index=i,
                    resistance_level=candle['high'],
                    stop_loss=candle['low'] * 0.98
                ))

            # Hanging Man (bearish reversal - same shape as hammer but in uptrend)
            elif (body_position < 0.3 and
                  lower_shadow_ratio >= 2.0 and
                  upper_shadow_ratio < 0.3):

                trend = self._determine_trend(df, i, lookback=5)
                if trend == "uptrend":
                    confidence = 0.7 + min((lower_shadow_ratio - 2.0) * 0.1, 0.2)

                    patterns.append(CandlestickPattern(
                        pattern_type=PatternType.HANGING_MAN,
                        signal=Signal.BEARISH,
                        confidence=min(confidence, 0.90),
                        description="Hanging Man - Bearish reversal in uptrend",
                        candle_index=i,
                        resistance_level=candle['high'],
                        stop_loss=candle['high'] * 1.02
                    ))

            # Shooting Star (bearish reversal)
            elif (body_position > 0.7 and
                  candle['upper_shadow'] >= candle['body'] * 2.0 and
                  candle['lower_shadow'] < candle['upper_shadow'] * 0.3):

                trend = self._determine_trend(df, i, lookback=5)
                if trend == "uptrend":
                    confidence = 0.75

                    patterns.append(CandlestickPattern(
                        pattern_type=PatternType.SHOOTING_STAR,
                        signal=Signal.BEARISH,
                        confidence=min(confidence, 0.95),
                        description="Shooting Star - Strong bearish reversal, sellers rejected highs",
                        candle_index=i,
                        resistance_level=candle['high'],
                        target_price=candle['close'] - (candle['high'] - candle['close']) * 2,
                        stop_loss=candle['high'] * 1.02
                    ))

        return patterns

    def _detect_engulfing_patterns(self, df: pd.DataFrame) -> List[CandlestickPattern]:
        """Detect Bullish/Bearish Engulfing patterns"""
        patterns = []

        for i in range(1, len(df)):
            current = df.iloc[i]
            prev = df.iloc[i-1]

            # Bullish Engulfing: bearish candle followed by larger bullish candle
            if (not prev['bullish'] and current['bullish'] and
                current['open'] <= prev['close'] and
                current['close'] > prev['open']):

                # Confidence based on size difference
                size_ratio = current['body'] / prev['body'] if prev['body'] > 0 else 2.0
                confidence = min(0.6 + (size_ratio - 1.0) * 0.2, 0.95)

                # Higher confidence if in downtrend
                trend = self._determine_trend(df, i, lookback=5)
                if trend == "downtrend":
                    confidence += 0.1

                patterns.append(CandlestickPattern(
                    pattern_type=PatternType.BULLISH_ENGULFING,
                    signal=Signal.BULLISH,
                    confidence=min(confidence, 0.95),
                    description="Bullish Engulfing - Strong bullish reversal",
                    candle_index=i,
                    support_level=current['low'],
                    target_price=current['close'] + (current['close'] - prev['low']),
                    stop_loss=prev['low'] * 0.98
                ))

            # Bearish Engulfing: bullish candle followed by larger bearish candle
            elif (prev['bullish'] and not current['bullish'] and
                  current['open'] >= prev['close'] and
                  current['close'] < prev['open']):

                size_ratio = current['body'] / prev['body'] if prev['body'] > 0 else 2.0
                confidence = min(0.6 + (size_ratio - 1.0) * 0.2, 0.95)

                trend = self._determine_trend(df, i, lookback=5)
                if trend == "uptrend":
                    confidence += 0.1

                patterns.append(CandlestickPattern(
                    pattern_type=PatternType.BEARISH_ENGULFING,
                    signal=Signal.BEARISH,
                    confidence=min(confidence, 0.95),
                    description="Bearish Engulfing - Strong bearish reversal",
                    candle_index=i,
                    resistance_level=current['high'],
                    target_price=current['close'] - (prev['high'] - current['close']),
                    stop_loss=prev['high'] * 1.02
                ))

        return patterns

    def _detect_star_patterns(self, df: pd.DataFrame) -> List[CandlestickPattern]:
        """Detect Morning Star and Evening Star patterns"""
        patterns = []

        for i in range(2, len(df)):
            first = df.iloc[i-2]
            second = df.iloc[i-1]
            third = df.iloc[i]

            # Morning Star (bullish reversal): bearish, small body, bullish
            if (not first['bullish'] and
                second['body'] < first['body'] * 0.5 and
                third['bullish'] and
                third['close'] > first['open'] + first['body'] * 0.5):

                trend = self._determine_trend(df, i-2, lookback=5)
                confidence = 0.75 if trend == "downtrend" else 0.60

                patterns.append(CandlestickPattern(
                    pattern_type=PatternType.MORNING_STAR,
                    signal=Signal.BULLISH,
                    confidence=min(confidence, 0.90),
                    description="Morning Star - Three-candle bullish reversal",
                    candle_index=i,
                    support_level=second['low'],
                    target_price=third['close'] + (third['close'] - second['low']) * 1.5,
                    stop_loss=second['low'] * 0.98
                ))

            # Evening Star (bearish reversal): bullish, small body, bearish
            elif (first['bullish'] and
                  second['body'] < first['body'] * 0.5 and
                  not third['bullish'] and
                  third['close'] < first['close'] - first['body'] * 0.5):

                trend = self._determine_trend(df, i-2, lookback=5)
                confidence = 0.75 if trend == "uptrend" else 0.60

                patterns.append(CandlestickPattern(
                    pattern_type=PatternType.EVENING_STAR,
                    signal=Signal.BEARISH,
                    confidence=min(confidence, 0.90),
                    description="Evening Star - Three-candle bearish reversal",
                    candle_index=i,
                    resistance_level=second['high'],
                    target_price=third['close'] - (second['high'] - third['close']) * 1.5,
                    stop_loss=second['high'] * 1.02
                ))

        return patterns

    def _detect_soldiers_crows_patterns(self, df: pd.DataFrame) -> List[CandlestickPattern]:
        """Detect Three White Soldiers and Three Black Crows"""
        patterns = []

        for i in range(2, len(df)):
            first = df.iloc[i-2]
            second = df.iloc[i-1]
            third = df.iloc[i]

            # Three White Soldiers (strong bullish continuation)
            if (first['bullish'] and second['bullish'] and third['bullish'] and
                second['close'] > first['close'] and third['close'] > second['close'] and
                second['open'] > first['open'] and second['open'] < first['close'] and
                third['open'] > second['open'] and third['open'] < second['close']):

                confidence = 0.85
                patterns.append(CandlestickPattern(
                    pattern_type=PatternType.THREE_WHITE_SOLDIERS,
                    signal=Signal.BULLISH,
                    confidence=confidence,
                    description="Three White Soldiers - Strong bullish continuation",
                    candle_index=i,
                    support_level=first['low'],
                    target_price=third['close'] * 1.05
                ))

            # Three Black Crows (strong bearish continuation)
            elif (not first['bullish'] and not second['bullish'] and not third['bullish'] and
                  second['close'] < first['close'] and third['close'] < second['close'] and
                  second['open'] < first['open'] and second['open'] > first['close'] and
                  third['open'] < second['open'] and third['open'] > second['close']):

                confidence = 0.85
                patterns.append(CandlestickPattern(
                    pattern_type=PatternType.THREE_BLACK_CROWS,
                    signal=Signal.BEARISH,
                    confidence=confidence,
                    description="Three Black Crows - Strong bearish continuation",
                    candle_index=i,
                    resistance_level=first['high'],
                    target_price=third['close'] * 0.95
                ))

        return patterns

    def _detect_marubozu_patterns(self, df: pd.DataFrame) -> List[CandlestickPattern]:
        """Detect Marubozu patterns (strong momentum, no shadows)"""
        patterns = []

        for i in range(len(df)):
            candle = df.iloc[i]

            if candle['range'] == 0:
                continue

            # Marubozu: body takes up 90%+ of range
            body_ratio = candle['body'] / candle['range']

            if body_ratio >= 0.90:
                if candle['bullish']:
                    confidence = min(body_ratio, 0.90)

                    patterns.append(CandlestickPattern(
                        pattern_type=PatternType.MARUBOZU_BULLISH,
                        signal=Signal.BULLISH,
                        confidence=confidence,
                        description="Bullish Marubozu - Extremely strong buying pressure",
                        candle_index=i,
                        support_level=candle['low']
                    ))
                else:
                    confidence = min(body_ratio, 0.90)

                    patterns.append(CandlestickPattern(
                        pattern_type=PatternType.MARUBOZU_BEARISH,
                        signal=Signal.BEARISH,
                        confidence=confidence,
                        description="Bearish Marubozu - Extremely strong selling pressure",
                        candle_index=i,
                        resistance_level=candle['high']
                    ))

        return patterns

    def _detect_harami_patterns(self, df: pd.DataFrame) -> List[CandlestickPattern]:
        """Detect Harami patterns (reversal)"""
        patterns = []

        for i in range(1, len(df)):
            first = df.iloc[i-1]
            second = df.iloc[i]

            # Bullish Harami: large bearish followed by small bullish inside
            if (not first['bullish'] and second['bullish'] and
                second['open'] > first['close'] and
                second['close'] < first['open'] and
                second['body'] < first['body'] * 0.5):

                confidence = 0.70

                patterns.append(CandlestickPattern(
                    pattern_type=PatternType.HARAMI_BULLISH,
                    signal=Signal.BULLISH,
                    confidence=confidence,
                    description="Bullish Harami - Potential bullish reversal",
                    candle_index=i,
                    support_level=first['low']
                ))

            # Bearish Harami: large bullish followed by small bearish inside
            elif (first['bullish'] and not second['bullish'] and
                  second['open'] < first['close'] and
                  second['close'] > first['open'] and
                  second['body'] < first['body'] * 0.5):

                confidence = 0.70

                patterns.append(CandlestickPattern(
                    pattern_type=PatternType.HARAMI_BEARISH,
                    signal=Signal.BEARISH,
                    confidence=confidence,
                    description="Bearish Harami - Potential bearish reversal",
                    candle_index=i,
                    resistance_level=first['high']
                ))

        return patterns

    def _detect_tweezer_patterns(self, df: pd.DataFrame) -> List[CandlestickPattern]:
        """Detect Tweezer Top and Bottom patterns"""
        patterns = []

        for i in range(1, len(df)):
            first = df.iloc[i-1]
            second = df.iloc[i]

            # Tweezer Bottom (bullish reversal): similar lows
            low_diff = abs(first['low'] - second['low']) / first['low'] if first['low'] > 0 else 0
            if low_diff < 0.002:  # Lows within 0.2%
                if not first['bullish'] and second['bullish']:
                    confidence = 0.75

                    patterns.append(CandlestickPattern(
                        pattern_type=PatternType.TWEEZER_BOTTOM,
                        signal=Signal.BULLISH,
                        confidence=confidence,
                        description="Tweezer Bottom - Support confirmed, bullish reversal",
                        candle_index=i,
                        support_level=min(first['low'], second['low'])
                    ))

            # Tweezer Top (bearish reversal): similar highs
            high_diff = abs(first['high'] - second['high']) / first['high'] if first['high'] > 0 else 0
            if high_diff < 0.002:  # Highs within 0.2%
                if first['bullish'] and not second['bullish']:
                    confidence = 0.75

                    patterns.append(CandlestickPattern(
                        pattern_type=PatternType.TWEEZER_TOP,
                        signal=Signal.BEARISH,
                        confidence=confidence,
                        description="Tweezer Top - Resistance confirmed, bearish reversal",
                        candle_index=i,
                        resistance_level=max(first['high'], second['high'])
                    ))

        return patterns

    def _detect_piercing_patterns(self, df: pd.DataFrame) -> List[CandlestickPattern]:
        """Detect Piercing Line and Dark Cloud Cover"""
        patterns = []

        for i in range(1, len(df)):
            first = df.iloc[i-1]
            second = df.iloc[i]

            # Piercing Line (bullish reversal)
            if (not first['bullish'] and second['bullish'] and
                second['open'] < first['low'] and
                second['close'] > (first['open'] + first['close']) / 2 and
                second['close'] < first['open']):

                penetration = (second['close'] - first['close']) / first['body'] if first['body'] > 0 else 0
                confidence = min(0.6 + penetration * 0.3, 0.85)

                patterns.append(CandlestickPattern(
                    pattern_type=PatternType.PIERCING_LINE,
                    signal=Signal.BULLISH,
                    confidence=confidence,
                    description="Piercing Line - Bullish reversal with strong buying",
                    candle_index=i,
                    support_level=second['low']
                ))

            # Dark Cloud Cover (bearish reversal)
            elif (first['bullish'] and not second['bullish'] and
                  second['open'] > first['high'] and
                  second['close'] < (first['open'] + first['close']) / 2 and
                  second['close'] > first['open']):

                penetration = (first['close'] - second['close']) / first['body'] if first['body'] > 0 else 0
                confidence = min(0.6 + penetration * 0.3, 0.85)

                patterns.append(CandlestickPattern(
                    pattern_type=PatternType.DARK_CLOUD_COVER,
                    signal=Signal.BEARISH,
                    confidence=confidence,
                    description="Dark Cloud Cover - Bearish reversal with strong selling",
                    candle_index=i,
                    resistance_level=second['high']
                ))

        return patterns

    def _determine_trend(self, df: pd.DataFrame, index: int, lookback: int = 5) -> str:
        """Determine if price is in uptrend, downtrend, or sideways"""
        if index < lookback:
            return "unknown"

        recent_closes = df.iloc[index-lookback:index]['close'].values

        # Calculate linear regression slope
        x = np.arange(len(recent_closes))
        slope = np.polyfit(x, recent_closes, 1)[0]

        # Threshold based on price (1% move over lookback period)
        threshold = recent_closes[-1] * 0.01 / lookback

        if slope > threshold:
            return "uptrend"
        elif slope < -threshold:
            return "downtrend"
        else:
            return "sideways"

    def get_pattern_summary(self, patterns: List[CandlestickPattern]) -> Dict:
        """Get summary statistics of detected patterns"""
        if not patterns:
            return {
                "total_patterns": 0,
                "bullish_count": 0,
                "bearish_count": 0,
                "neutral_count": 0,
                "avg_confidence": 0.0,
                "strongest_signal": None
            }

        bullish = [p for p in patterns if p.signal == Signal.BULLISH]
        bearish = [p for p in patterns if p.signal == Signal.BEARISH]
        neutral = [p for p in patterns if p.signal == Signal.NEUTRAL]

        return {
            "total_patterns": len(patterns),
            "bullish_count": len(bullish),
            "bearish_count": len(bearish),
            "neutral_count": len(neutral),
            "avg_confidence": np.mean([p.confidence for p in patterns]),
            "strongest_signal": patterns[0] if patterns else None,
            "pattern_types": [p.pattern_type.value for p in patterns]
        }
