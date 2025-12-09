"""
Premium Selling Strategies - Verified 70%+ Win Rates
Theta Gang strategies that consistently outperform buying options

Based on verified performance:
- Wheel Strategy: 72.7% win rate over 13 years (SteadyOptions)
- Credit Spreads: 75%+ win rate (0DTE data)
- Iron Butterflies: 60-70% win rate (verified)
- Short Straddles/Strangles: 60-70% win rate
"""
import logging
from typing import Optional, List, Tuple
from datetime import datetime, date
from enum import Enum
import numpy as np

from options_models import (
    OptionContract,
    OptionType,
    SignalAction,
    StrategyType
)
from greeks_calculator import GreeksCalculator

logger = logging.getLogger(__name__)


class PremiumStrategy(str, Enum):
    """Premium selling strategy types"""
    WHEEL = "WHEEL"
    CREDIT_SPREAD = "CREDIT_SPREAD"
    IRON_CONDOR = "IRON_CONDOR"
    IRON_BUTTERFLY = "IRON_BUTTERFLY"
    SHORT_STRANGLE = "SHORT_STRANGLE"
    SHORT_STRADDLE = "SHORT_STRADDLE"
    COVERED_CALL = "COVERED_CALL"


class WheelStrategySignal:
    """
    The Wheel Strategy - 72.7% Win Rate (Verified)

    Phase 1: Sell cash-secured puts (collect premium)
    Phase 2: If assigned, sell covered calls (collect more premium)
    Phase 3: Repeat

    Optimal Parameters (from research):
    - DTE: 30-45 days (theta decay sweet spot)
    - Delta: 0.30-0.40 (30-40% OTM)
    - IV Rank: >50 preferred
    - Win Rate: 72.7% (13-year verified data)
    """

    @staticmethod
    def find_wheel_opportunities(
        symbol: str,
        stock_price: float,
        options_chain: List[OptionContract],
        min_dte: int = 30,
        max_dte: int = 45,
        target_delta: float = 0.35
    ) -> List[dict]:
        """
        Find optimal wheel strategy entry points

        Args:
            symbol: Stock symbol
            stock_price: Current stock price
            options_chain: Available options
            min_dte: Minimum days to expiration
            max_dte: Maximum days to expiration
            target_delta: Target delta (0.30-0.40)

        Returns:
            List of wheel opportunity signals
        """
        opportunities = []

        for contract in options_chain:
            # Only look at puts for wheel entry
            if contract.option_type != OptionType.PUT:
                continue

            # Filter by DTE (30-45 days sweet spot)
            if not (min_dte <= contract.days_to_expiration <= max_dte):
                continue

            # Filter by delta (30-40 delta puts)
            delta = abs(contract.greeks.delta)
            if not (0.25 <= delta <= 0.45):
                continue

            # Calculate premium yield
            premium = contract.pricing.mark
            strike = contract.strike
            premium_yield = (premium / strike) * 100

            # Calculate annual return potential
            days = contract.days_to_expiration
            annualized_return = (premium_yield / days) * 365

            # Filter: Want minimum annualized return
            if annualized_return < 12:  # 12%+ annual return
                continue

            # Check if we actually want to own this stock at strike
            discount_to_current = ((stock_price - strike) / stock_price) * 100

            opportunities.append({
                "symbol": symbol,
                "strategy": "WHEEL_ENTRY",
                "action": "SELL_PUT",
                "contract": contract,
                "strike": strike,
                "premium": premium,
                "delta": delta,
                "dte": days,
                "premium_yield": premium_yield,
                "annualized_return": annualized_return,
                "discount_if_assigned": discount_to_current,
                "confidence": 0.73,  # 72.7% verified win rate
                "reasoning": f"Wheel: Sell {delta:.2f}Δ put, {premium_yield:.1f}% yield, {annualized_return:.1f}% annual",
                "assignment_risk": delta,
                "max_profit": premium * 100,  # Per contract
                "max_loss": (strike - premium) * 100,  # If stock goes to $0
                "breakeven": strike - premium
            })

        # Sort by annualized return
        opportunities.sort(key=lambda x: x["annualized_return"], reverse=True)

        return opportunities

    @staticmethod
    def find_covered_call_opportunities(
        symbol: str,
        stock_price: float,
        shares_owned: int,
        options_chain: List[OptionContract],
        min_dte: int = 30,
        max_dte: int = 45
    ) -> List[dict]:
        """
        Find covered call opportunities (Phase 2 of wheel)

        Args:
            symbol: Stock symbol
            stock_price: Current price
            shares_owned: Shares owned (must be 100+)
            options_chain: Available calls
            min_dte: Minimum DTE
            max_dte: Maximum DTE

        Returns:
            List of covered call opportunities
        """
        if shares_owned < 100:
            return []

        num_contracts = shares_owned // 100
        opportunities = []

        for contract in options_chain:
            # Only calls for covered call
            if contract.option_type != OptionType.CALL:
                continue

            # Filter by DTE
            if not (min_dte <= contract.days_to_expiration <= max_dte):
                continue

            # Filter by delta (30-40 delta calls)
            delta = abs(contract.greeks.delta)
            if not (0.25 <= delta <= 0.45):
                continue

            # Premium and yield
            premium = contract.pricing.mark
            strike = contract.strike

            # Calculate total premium
            total_premium = premium * 100 * num_contracts

            # Calculate yield on shares
            shares_value = stock_price * shares_owned
            premium_yield = (total_premium / shares_value) * 100

            # Annualized return
            days = contract.days_to_expiration
            annualized_return = (premium_yield / days) * 365

            # Additional upside if called away
            capital_gain = ((strike - stock_price) / stock_price) * 100 if strike > stock_price else 0

            opportunities.append({
                "symbol": symbol,
                "strategy": "COVERED_CALL",
                "action": "SELL_CALL",
                "contract": contract,
                "strike": strike,
                "premium": premium,
                "delta": delta,
                "dte": days,
                "num_contracts": num_contracts,
                "total_premium": total_premium,
                "premium_yield": premium_yield,
                "annualized_return": annualized_return,
                "capital_gain_if_called": capital_gain,
                "total_return": premium_yield + capital_gain,
                "confidence": 0.73,
                "reasoning": f"Covered Call: {delta:.2f}Δ, {premium_yield:.1f}% yield, {annualized_return:.1f}% annual",
                "assignment_probability": delta,
                "max_profit": total_premium + (max(0, strike - stock_price) * shares_owned),
                "max_loss": float('inf'),  # Unlimited downside on stock
                "breakeven": stock_price - premium
            })

        opportunities.sort(key=lambda x: x["total_return"], reverse=True)

        return opportunities


class CreditSpreadStrategy:
    """
    Credit Spreads - 75%+ Win Rate (Verified)

    Sell one option, buy another further OTM as protection
    Collect premium, risk is limited

    Types:
    - Bull Put Spread: Bullish (sell put, buy put lower)
    - Bear Call Spread: Bearish (sell call, buy call higher)
    """

    @staticmethod
    def find_credit_spread_opportunities(
        symbol: str,
        stock_price: float,
        options_chain: List[OptionContract],
        trend: str = "bullish",
        target_delta: float = 0.30,
        spread_width: float = 5.0,
        min_dte: int = 30,
        max_dte: int = 45
    ) -> List[dict]:
        """
        Find credit spread opportunities

        Args:
            symbol: Stock symbol
            stock_price: Current price
            options_chain: Options chain
            trend: "bullish" or "bearish"
            target_delta: Target short strike delta
            spread_width: Width between strikes ($)
            min_dte: Min days to expiration
            max_dte: Max days to expiration

        Returns:
            List of credit spread opportunities
        """
        opportunities = []

        # Filter by DTE and type
        if trend == "bullish":
            option_type = OptionType.PUT
            strategy_name = "BULL_PUT_SPREAD"
        else:
            option_type = OptionType.CALL
            strategy_name = "BEAR_CALL_SPREAD"

        # Find short strike (sell)
        short_candidates = [
            c for c in options_chain
            if c.option_type == option_type
            and min_dte <= c.days_to_expiration <= max_dte
            and 0.25 <= abs(c.greeks.delta) <= 0.40
        ]

        for short_contract in short_candidates:
            short_strike = short_contract.strike
            short_premium = short_contract.pricing.mark

            # Find long strike (buy for protection)
            long_strike = short_strike - spread_width if trend == "bullish" else short_strike + spread_width

            long_contract = next(
                (c for c in options_chain
                 if c.option_type == option_type
                 and c.strike == long_strike
                 and c.expiration == short_contract.expiration),
                None
            )

            if not long_contract:
                continue

            long_premium = long_contract.pricing.ask  # Paying ask for protection

            # Calculate spread metrics
            net_credit = short_premium - long_premium
            max_profit = net_credit * 100
            max_loss = (spread_width - net_credit) * 100
            risk_reward = abs(max_loss / max_profit) if max_profit > 0 else 999

            # Calculate return on risk
            return_on_risk = (max_profit / max_loss) * 100 if max_loss > 0 else 0

            # Annualized return
            days = short_contract.days_to_expiration
            annualized_return = (return_on_risk / days) * 365

            # Probability of profit (based on delta)
            prob_profit = 1 - abs(short_contract.greeks.delta)

            # Filter: Want good return on risk
            if return_on_risk < 15:  # 15%+ ROI
                continue

            opportunities.append({
                "symbol": symbol,
                "strategy": strategy_name,
                "action": "OPEN_SPREAD",
                "short_contract": short_contract,
                "long_contract": long_contract,
                "short_strike": short_strike,
                "long_strike": long_strike,
                "spread_width": spread_width,
                "net_credit": net_credit,
                "max_profit": max_profit,
                "max_loss": max_loss,
                "risk_reward_ratio": risk_reward,
                "return_on_risk": return_on_risk,
                "annualized_return": annualized_return,
                "probability_of_profit": prob_profit,
                "dte": days,
                "confidence": 0.75,  # 75% verified win rate
                "reasoning": f"{strategy_name}: {prob_profit:.0%} PoP, {return_on_risk:.1f}% ROI, {annualized_return:.0f}% annual",
                "breakeven": short_strike - net_credit if trend == "bullish" else short_strike + net_credit
            })

        opportunities.sort(key=lambda x: x["return_on_risk"], reverse=True)

        return opportunities


class IronCondorStrategy:
    """
    Iron Condor - Neutral Market Strategy
    60-70% Win Rate (Verified)

    Combines bull put spread + bear call spread
    Profit from range-bound stock (theta decay)
    """

    @staticmethod
    def find_iron_condor_opportunities(
        symbol: str,
        stock_price: float,
        options_chain: List[OptionContract],
        wing_width: float = 5.0,
        min_dte: int = 30,
        max_dte: int = 45
    ) -> List[dict]:
        """
        Find iron condor opportunities

        Args:
            symbol: Stock symbol
            stock_price: Current price
            options_chain: Options chain
            wing_width: Width of each spread
            min_dte: Min DTE
            max_dte: Max DTE

        Returns:
            List of iron condor opportunities
        """
        opportunities = []

        # Iron Condor = Bull Put Spread + Bear Call Spread
        # Need 4 strikes: short put, long put, short call, long call

        # Find put side (bull put spread)
        put_spreads = CreditSpreadStrategy.find_credit_spread_opportunities(
            symbol,
            stock_price,
            options_chain,
            trend="bullish",
            spread_width=wing_width,
            min_dte=min_dte,
            max_dte=max_dte
        )

        # Find call side (bear call spread)
        call_spreads = CreditSpreadStrategy.find_credit_spread_opportunities(
            symbol,
            stock_price,
            options_chain,
            trend="bearish",
            spread_width=wing_width,
            min_dte=min_dte,
            max_dte=max_dte
        )

        # Combine spreads with same expiration
        for put_spread in put_spreads[:5]:  # Top 5 put spreads
            for call_spread in call_spreads[:5]:  # Top 5 call spreads
                # Must have same expiration
                if put_spread["short_contract"].expiration != call_spread["short_contract"].expiration:
                    continue

                # Calculate iron condor metrics
                total_credit = put_spread["net_credit"] + call_spread["net_credit"]
                max_profit = total_credit * 100
                max_loss = (wing_width - total_credit) * 100
                return_on_risk = (max_profit / max_loss) * 100 if max_loss > 0 else 0

                # Calculate range (profit zone)
                lower_breakeven = put_spread["breakeven"]
                upper_breakeven = call_spread["breakeven"]
                profit_range = upper_breakeven - lower_breakeven
                profit_range_percent = (profit_range / stock_price) * 100

                # Probability of profit (both sides stay OTM)
                put_pop = put_spread["probability_of_profit"]
                call_pop = call_spread["probability_of_profit"]
                combined_pop = put_pop * call_pop  # Independent probabilities

                days = put_spread["dte"]
                annualized_return = (return_on_risk / days) * 365

                opportunities.append({
                    "symbol": symbol,
                    "strategy": "IRON_CONDOR",
                    "action": "OPEN_CONDOR",
                    "put_spread": put_spread,
                    "call_spread": call_spread,
                    "total_credit": total_credit,
                    "max_profit": max_profit,
                    "max_loss": max_loss,
                    "return_on_risk": return_on_risk,
                    "annualized_return": annualized_return,
                    "lower_breakeven": lower_breakeven,
                    "upper_breakeven": upper_breakeven,
                    "profit_range": profit_range,
                    "profit_range_percent": profit_range_percent,
                    "probability_of_profit": combined_pop,
                    "dte": days,
                    "confidence": 0.65,  # 60-70% win rate
                    "reasoning": f"Iron Condor: {combined_pop:.0%} PoP, {profit_range_percent:.1f}% range, {return_on_risk:.1f}% ROI"
                })

        opportunities.sort(key=lambda x: x["probability_of_profit"], reverse=True)

        return opportunities


class ShortStrangleStrategy:
    """
    Short Strangle - High Theta Decay
    60-70% Win Rate (Verified)

    Sell OTM put + OTM call
    Profit if stock stays in range
    Higher risk than iron condor (undefined)
    """

    @staticmethod
    def find_short_strangle_opportunities(
        symbol: str,
        stock_price: float,
        options_chain: List[OptionContract],
        target_delta: float = 0.30,
        min_dte: int = 30,
        max_dte: int = 45,
        min_iv_rank: float = 50.0
    ) -> List[dict]:
        """
        Find short strangle opportunities

        Args:
            symbol: Stock symbol
            stock_price: Current price
            options_chain: Options chain
            target_delta: Target delta for both strikes
            min_dte: Min DTE
            max_dte: Max DTE
            min_iv_rank: Minimum IV rank (prefer high IV)

        Returns:
            List of short strangle opportunities
        """
        opportunities = []

        # Find put side
        put_candidates = [
            c for c in options_chain
            if c.option_type == OptionType.PUT
            and min_dte <= c.days_to_expiration <= max_dte
            and 0.25 <= abs(c.greeks.delta) <= 0.35
            and c.iv_metrics.iv_rank >= min_iv_rank
        ]

        # Find call side
        call_candidates = [
            c for c in options_chain
            if c.option_type == OptionType.CALL
            and min_dte <= c.days_to_expiration <= max_dte
            and 0.25 <= abs(c.greeks.delta) <= 0.35
            and c.iv_metrics.iv_rank >= min_iv_rank
        ]

        # Match by expiration
        for put in put_candidates:
            matching_calls = [
                c for c in call_candidates
                if c.expiration == put.expiration
            ]

            for call in matching_calls:
                total_credit = put.pricing.mark + call.pricing.mark
                max_profit = total_credit * 100

                # Calculate breakevens
                lower_breakeven = put.strike - total_credit
                upper_breakeven = call.strike + total_credit
                profit_range = upper_breakeven - lower_breakeven
                profit_range_percent = (profit_range / stock_price) * 100

                # Probability of profit
                put_pop = 1 - abs(put.greeks.delta)
                call_pop = 1 - abs(call.greeks.delta)
                combined_pop = put_pop * call_pop

                # Theta decay (daily profit potential)
                total_theta = abs(put.greeks.theta) + abs(call.greeks.theta)
                daily_theta_profit = total_theta * 100

                days = put.days_to_expiration

                opportunities.append({
                    "symbol": symbol,
                    "strategy": "SHORT_STRANGLE",
                    "action": "SELL_STRANGLE",
                    "put_contract": put,
                    "call_contract": call,
                    "put_strike": put.strike,
                    "call_strike": call.strike,
                    "total_credit": total_credit,
                    "max_profit": max_profit,
                    "max_loss": float('inf'),  # Undefined risk
                    "lower_breakeven": lower_breakeven,
                    "upper_breakeven": upper_breakeven,
                    "profit_range": profit_range,
                    "profit_range_percent": profit_range_percent,
                    "probability_of_profit": combined_pop,
                    "daily_theta": daily_theta_profit,
                    "dte": days,
                    "iv_rank": (put.iv_metrics.iv_rank + call.iv_metrics.iv_rank) / 2,
                    "confidence": 0.65,  # 60-70% win rate
                    "reasoning": f"Short Strangle: {combined_pop:.0%} PoP, ${daily_theta_profit:.2f}/day theta, {profit_range_percent:.1f}% range",
                    "risk_level": "HIGH"  # Undefined risk
                })

        opportunities.sort(key=lambda x: x["daily_theta"], reverse=True)

        return opportunities
