"""
Improved Entry Filters - Only High-Probability Setups
Filters out garbage signals and only shows trades with real edge
"""
import logging
from typing import Optional
import numpy as np

from options_models import OptionContract

logger = logging.getLogger(__name__)


class ImprovedFilters:
    """
    Strict filters to avoid bad trades
    Only pass signals with real probability of profit
    """

    @staticmethod
    def check_volume_quality(contract: OptionContract) -> tuple[bool, str]:
        """
        Check if volume is REAL and not fake

        Returns:
            (passes, reason)
        """
        # Must have significant volume
        if contract.volume_metrics.volume < 100:
            return False, f"Volume too low: {contract.volume_metrics.volume}"

        # Open interest should exist (people actually trading this)
        if contract.volume_metrics.open_interest < 50:
            return False, f"No real interest: OI={contract.volume_metrics.open_interest}"

        # Volume should be reasonable relative to OI
        volume_to_oi = contract.volume_metrics.volume / max(contract.volume_metrics.open_interest, 1)
        if volume_to_oi > 10:
            # Suspicious - way more volume than OI (manipulation?)
            return False, f"Suspicious volume/OI ratio: {volume_to_oi:.1f}x"

        return True, "Volume quality good"

    @staticmethod
    def check_price_action(contract: OptionContract, price_momentum_1m: float) -> tuple[bool, str]:
        """
        Check if price action supports the trade

        Returns:
            (passes, reason)
        """
        # For CALLS: stock should be moving UP
        if contract.greeks.delta > 0:  # CALL
            if price_momentum_1m <= 0:
                return False, f"CALL but stock moving DOWN {price_momentum_1m:.2%}"
            if price_momentum_1m < 0.002:  # Less than 0.2% momentum
                return False, f"CALL but weak momentum {price_momentum_1m:.2%}"

        # For PUTS: stock should be moving DOWN
        else:  # PUT
            if price_momentum_1m >= 0:
                return False, f"PUT but stock moving UP {price_momentum_1m:.2%}"
            if price_momentum_1m > -0.002:  # Less than 0.2% momentum
                return False, f"PUT but weak momentum {price_momentum_1m:.2%}"

        return True, "Price action supports trade"

    @staticmethod
    def check_time_to_expiration(contract: OptionContract) -> tuple[bool, str]:
        """
        Check if there's enough time for the trade to work

        Returns:
            (passes, reason)
        """
        from datetime import datetime

        try:
            exp_date = datetime.strptime(contract.expiration, "%Y-%m-%d")
            days_to_exp = (exp_date - datetime.now()).days

            # For scalping: Need at least 1 day
            if days_to_exp < 1:
                return False, f"Expires too soon: {days_to_exp} days"

            # Warning for very close expiration
            if days_to_exp < 3:
                logger.warning(f"{contract.symbol}: Only {days_to_exp} days to expiration - high theta decay")

            # Don't trade options expiring in more than 30 days for scalping
            if days_to_exp > 30:
                return False, f"Too far out for scalping: {days_to_exp} days"

        except:
            pass  # Can't parse expiration date

        return True, "Time to expiration acceptable"

    @staticmethod
    def check_implied_volatility(contract: OptionContract) -> tuple[bool, str]:
        """
        Check IV for signs of inflated premiums

        Returns:
            (passes, reason)
        """
        iv = contract.iv_metrics.iv

        # IV should be reasonable
        if iv < 0.15:  # Less than 15%
            return False, f"IV too low {iv:.1%} - dead option"

        if iv > 2.0:  # More than 200%
            return False, f"IV too high {iv:.1%} - overpriced"

        # Check IV rank (how high is IV relative to its range)
        if contract.iv_metrics.iv_rank > 0.80:
            logger.warning(f"{contract.symbol}: High IV rank {contract.iv_metrics.iv_rank:.1%} - expensive premiums")

        return True, "IV acceptable"

    @staticmethod
    def check_spread_quality(contract: OptionContract) -> tuple[bool, str]:
        """
        Check if spread is tradeable

        Returns:
            (passes, reason)
        """
        # Spread should not be too wide
        spread = contract.pricing.spread
        mark = contract.pricing.mark

        if mark == 0:
            return False, "No market price"

        spread_percent = (spread / mark) * 100

        # For scalping, need tight spreads
        if spread_percent > 30:
            return False, f"Spread too wide: {spread_percent:.1f}%"

        # Absolute spread should be reasonable
        if spread > 1.0 and mark < 5.0:
            return False, f"Spread ${spread:.2f} too wide for ${mark:.2f} option"

        return True, "Spread quality good"

    @staticmethod
    def check_greeks_quality(contract: OptionContract) -> tuple[bool, str]:
        """
        Check if Greeks make sense for scalping

        Returns:
            (passes, reason)
        """
        delta = abs(contract.greeks.delta)
        gamma = contract.greeks.gamma
        theta = contract.greeks.theta

        # Delta: For scalping, want 0.30-0.70 (slightly OTM to slightly ITM)
        if delta < 0.25:
            return False, f"Delta too low {delta:.2f} - too far OTM"

        if delta > 0.85:
            return False, f"Delta too high {delta:.2f} - too expensive, limited leverage"

        # Theta: Should not be bleeding too fast
        # For a $1 option, losing more than $0.10/day is bad
        mark = contract.pricing.mark
        if mark > 0:
            daily_theta_percent = abs(theta / mark)
            if daily_theta_percent > 0.15:  # Losing 15%+ per day
                return False, f"Theta decay too high: {daily_theta_percent:.1%}/day"

        return True, "Greeks quality good"

    @staticmethod
    def check_moneyness(contract: OptionContract) -> tuple[bool, str]:
        """
        Check if option is appropriately priced

        Returns:
            (passes, reason)
        """
        strike = contract.strike
        underlying = contract.underlying_price

        if underlying == 0:
            return False, "No underlying price"

        # Calculate how far from ATM
        distance = abs(strike - underlying) / underlying

        # For scalping, don't want too far OTM
        if distance > 0.10:  # More than 10% from underlying
            return False, f"Too far from money: {distance:.1%}"

        return True, "Moneyness acceptable"

    @classmethod
    def apply_all_filters(
        cls,
        contract: OptionContract,
        price_momentum_1m: float
    ) -> tuple[bool, list[str]]:
        """
        Apply all improved filters

        Returns:
            (passes_all, list_of_reasons)
        """
        checks = [
            cls.check_volume_quality(contract),
            cls.check_price_action(contract, price_momentum_1m),
            cls.check_time_to_expiration(contract),
            cls.check_implied_volatility(contract),
            cls.check_spread_quality(contract),
            cls.check_greeks_quality(contract),
            cls.check_moneyness(contract)
        ]

        failures = [reason for passed, reason in checks if not passed]
        warnings = [reason for passed, reason in checks if passed and "warning" in reason.lower()]

        passes_all = len(failures) == 0

        if passes_all and warnings:
            logger.debug(f"{contract.symbol}: PASSED with warnings: {', '.join(warnings)}")

        return passes_all, failures
