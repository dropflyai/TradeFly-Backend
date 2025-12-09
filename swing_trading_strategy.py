"""
Swing Trading Strategy - 14-30 DTE Options
More forgiving, less theta decay, time to be right

TARGET: 20-50% gains over 1-5 days
TIME HORIZON: 14-30 days to expiration
HOLDING PERIOD: 1-5 days average
"""
import logging
from typing import Optional
import numpy as np
from datetime import datetime, timedelta

from options_models import OptionContract, SignalAction
from technical_analysis import TechnicalAnalysis
from improved_filters import ImprovedFilters

logger = logging.getLogger(__name__)


class SwingSignal:
    """Swing trading signal for 14-30 DTE options"""
    def __init__(
        self,
        action: SignalAction,
        contract: OptionContract,
        entry: float,
        target: float,
        stop: float,
        confidence: float,
        reason: str,
        holding_period_days: int = 3
    ):
        self.action = action
        self.contract = contract
        self.entry = entry
        self.target = target
        self.stop = stop
        self.confidence = confidence
        self.reason = reason
        self.holding_period_days = holding_period_days


class SwingTradingStrategy:
    """
    Swing Trading Strategy - Give trades TIME to work

    Key Differences from Scalping:
    - 14-30 DTE (not 0-7)
    - Hold 1-5 days (not minutes)
    - Less theta decay per day
    - More forgiving entries
    """

    @staticmethod
    def detect_signal(
        contract: OptionContract,
        price_history_1h: np.ndarray,  # Hourly bars, not 1-minute
        price_history_daily: np.ndarray
    ) -> Optional[SwingSignal]:
        """
        Detect swing trading opportunities

        Criteria:
        1. 14-30 DTE (sweet spot - enough time, not too expensive)
        2. Delta: 0.40-0.60 (slightly OTM to ATM)
        3. Daily trend: 3+ days of momentum
        4. Price pullback to support
        5. RSI: Oversold/overbought on daily

        Args:
            contract: Option contract
            price_history_1h: Hourly price bars
            price_history_daily: Daily price bars

        Returns:
            SwingSignal if opportunity detected
        """
        ta = TechnicalAnalysis()

        # === FILTER 1: Time to Expiration (14-30 days) ===
        try:
            exp_date = datetime.strptime(contract.expiration, "%Y-%m-%d")
            days_to_exp = (exp_date - datetime.now()).days

            if days_to_exp < 14:
                logger.debug(f"{contract.symbol}: Too close to expiration ({days_to_exp} days)")
                return None

            if days_to_exp > 30:
                logger.debug(f"{contract.symbol}: Too far out ({days_to_exp} days)")
                return None

        except Exception as e:
            logger.debug(f"{contract.symbol}: Could not parse expiration date")
            return None

        # === FILTER 2: Delta (0.40-0.60 for swings) ===
        delta = abs(contract.greeks.delta)
        if not (0.40 <= delta <= 0.60):
            logger.debug(f"{contract.symbol}: Delta {delta:.2f} outside swing range (want 0.40-0.60)")
            return None

        # === FILTER 3: Price Affordability (under $5/share = $500/contract) ===
        if contract.pricing.ask > 5.0:
            logger.debug(f"{contract.symbol}: Too expensive ${contract.pricing.ask:.2f}/share for swing")
            return None

        # === FILTER 4: Liquidity & Quality ===
        if contract.volume_metrics.volume < 50:
            logger.debug(f"{contract.symbol}: Volume too low for swing: {contract.volume_metrics.volume}")
            return None

        if contract.volume_metrics.open_interest < 100:
            logger.debug(f"{contract.symbol}: OI too low: {contract.volume_metrics.open_interest}")
            return None

        # === FILTER 5: Daily Trend Analysis ===
        if len(price_history_daily) < 10:
            logger.debug(f"{contract.symbol}: Insufficient daily history")
            return None

        # Calculate daily momentum
        daily_momentum = ta.momentum(price_history_daily, period=3)  # 3-day trend

        # Calculate daily RSI
        daily_rsi = ta.rsi(price_history_daily, period=14)

        # === BULLISH SWING SETUP ===
        # Looking for: uptrend + pullback + oversold RSI
        if daily_momentum > 0.01:  # 1%+ uptrend over 3 days
            if contract.greeks.delta > 0:  # CALL contract
                # Want RSI oversold (pullback in uptrend)
                if 30 <= daily_rsi <= 45:
                    # Check hourly for entry confirmation
                    if len(price_history_1h) >= 5:
                        hourly_momentum = ta.momentum(price_history_1h, period=1)

                        # Want recent bounce (hourly turning up)
                        if hourly_momentum > 0.001:
                            confidence = 0.75 + (daily_momentum * 5)  # Higher confidence for stronger trends
                            confidence = min(confidence, 0.95)

                            return SwingSignal(
                                action=SignalAction.BUY_CALL,
                                contract=contract,
                                entry=contract.pricing.ask,
                                target=contract.pricing.ask * 1.30,  # 30% target
                                stop=contract.pricing.ask * 0.85,     # 15% stop
                                confidence=confidence,
                                reason=f"Swing: {daily_momentum:.1%} daily uptrend, RSI {daily_rsi:.0f} pullback, {days_to_exp}d to exp",
                                holding_period_days=3
                            )

        # === BEARISH SWING SETUP ===
        # Looking for: downtrend + bounce + overbought RSI
        if daily_momentum < -0.01:  # 1%+ downtrend over 3 days
            if contract.greeks.delta < 0:  # PUT contract
                # Want RSI overbought (bounce in downtrend)
                if 55 <= daily_rsi <= 70:
                    # Check hourly for entry confirmation
                    if len(price_history_1h) >= 5:
                        hourly_momentum = ta.momentum(price_history_1h, period=1)

                        # Want recent rejection (hourly turning down)
                        if hourly_momentum < -0.001:
                            confidence = 0.75 + (abs(daily_momentum) * 5)
                            confidence = min(confidence, 0.95)

                            return SwingSignal(
                                action=SignalAction.BUY_PUT,
                                contract=contract,
                                entry=contract.pricing.ask,
                                target=contract.pricing.ask * 1.30,
                                stop=contract.pricing.ask * 0.85,
                                confidence=confidence,
                                reason=f"Swing: {daily_momentum:.1%} daily downtrend, RSI {daily_rsi:.0f} bounce, {days_to_exp}d to exp",
                                holding_period_days=3
                            )

        return None

    @staticmethod
    def get_exit_plan(signal: SwingSignal) -> dict:
        """
        Get detailed exit plan for swing trade

        Returns:
            Dictionary with exit instructions
        """
        return {
            "entry_price": signal.entry,
            "target_price": signal.target,
            "stop_loss": signal.stop,
            "holding_period": f"{signal.holding_period_days} days (average)",
            "max_hold": "5 days or 50% of time to expiration",
            "profit_target": f"{((signal.target / signal.entry - 1) * 100):.0f}%",
            "risk": f"{((1 - signal.stop / signal.entry) * 100):.0f}%",
            "risk_reward": f"{((signal.target - signal.entry) / (signal.entry - signal.stop)):.1f}:1",
            "instructions": [
                "1. Enter at market open or on next dip",
                "2. Set stop loss immediately",
                "3. Take 50% profit at 15% gain",
                "4. Let remaining 50% run to 30% target",
                "5. Exit at EOD if down 10%+",
                f"6. Exit after {signal.holding_period_days} days regardless"
            ]
        }
