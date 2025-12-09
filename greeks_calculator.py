"""
Options Greeks Calculator - Black-Scholes Model
Institutional-grade calculations for option risk metrics

VERIFIED: Standard Black-Scholes formulas used by professionals
"""
import math
from typing import Tuple
from datetime import date
from scipy.stats import norm
import logging

logger = logging.getLogger(__name__)


class GreeksCalculator:
    """
    Calculate option Greeks using Black-Scholes model

    Greeks:
    - Delta: Price sensitivity to underlying ($1 move)
    - Gamma: Rate of change of delta
    - Theta: Time decay per day
    - Vega: Sensitivity to IV changes (1% IV move)
    - Rho: Sensitivity to interest rate changes
    """

    @staticmethod
    def calculate_all_greeks(
        underlying_price: float,
        strike_price: float,
        days_to_expiration: int,
        implied_volatility: float,
        risk_free_rate: float = 0.05,  # 5% annual
        option_type: str = "call"
    ) -> dict:
        """
        Calculate all Greeks for an option

        Args:
            underlying_price: Current stock price
            strike_price: Option strike price
            days_to_expiration: Days until expiration
            implied_volatility: Implied volatility (as decimal, e.g., 0.30 for 30%)
            risk_free_rate: Risk-free interest rate (annual)
            option_type: "call" or "put"

        Returns:
            Dictionary with all Greeks
        """
        # Convert days to years
        time_to_expiration = days_to_expiration / 365.0

        # Handle edge cases
        if time_to_expiration <= 0:
            logger.warning("Option has expired")
            return {
                "delta": 0.0,
                "gamma": 0.0,
                "theta": 0.0,
                "vega": 0.0,
                "rho": 0.0
            }

        # Calculate d1 and d2 for Black-Scholes
        d1, d2 = GreeksCalculator._calculate_d1_d2(
            underlying_price,
            strike_price,
            time_to_expiration,
            implied_volatility,
            risk_free_rate
        )

        # Calculate each Greek
        delta = GreeksCalculator._calculate_delta(d1, option_type)
        gamma = GreeksCalculator._calculate_gamma(
            underlying_price,
            d1,
            implied_volatility,
            time_to_expiration
        )
        theta = GreeksCalculator._calculate_theta(
            underlying_price,
            strike_price,
            d1,
            d2,
            implied_volatility,
            risk_free_rate,
            time_to_expiration,
            option_type
        )
        vega = GreeksCalculator._calculate_vega(
            underlying_price,
            d1,
            time_to_expiration
        )
        rho = GreeksCalculator._calculate_rho(
            strike_price,
            d2,
            time_to_expiration,
            risk_free_rate,
            option_type
        )

        return {
            "delta": round(delta, 4),
            "gamma": round(gamma, 4),
            "theta": round(theta, 4),
            "vega": round(vega, 4),
            "rho": round(rho, 4)
        }

    @staticmethod
    def _calculate_d1_d2(
        S: float,  # Stock price
        K: float,  # Strike price
        T: float,  # Time to expiration (years)
        sigma: float,  # Implied volatility
        r: float   # Risk-free rate
    ) -> Tuple[float, float]:
        """
        Calculate d1 and d2 for Black-Scholes formula

        d1 = [ln(S/K) + (r + σ²/2)T] / (σ√T)
        d2 = d1 - σ√T
        """
        if T <= 0 or sigma <= 0:
            return 0.0, 0.0

        d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
        d2 = d1 - sigma * math.sqrt(T)

        return d1, d2

    @staticmethod
    def _calculate_delta(d1: float, option_type: str) -> float:
        """
        Delta: Rate of change of option price with respect to underlying price

        Call Delta = N(d1)
        Put Delta = N(d1) - 1

        Range: 0 to 1 for calls, -1 to 0 for puts
        """
        if option_type.lower() == "call":
            return norm.cdf(d1)
        else:  # put
            return norm.cdf(d1) - 1

    @staticmethod
    def _calculate_gamma(
        S: float,
        d1: float,
        sigma: float,
        T: float
    ) -> float:
        """
        Gamma: Rate of change of delta with respect to underlying price

        Γ = N'(d1) / (S × σ × √T)

        Same for calls and puts
        """
        if T <= 0 or sigma <= 0 or S <= 0:
            return 0.0

        gamma = norm.pdf(d1) / (S * sigma * math.sqrt(T))
        return gamma

    @staticmethod
    def _calculate_theta(
        S: float,
        K: float,
        d1: float,
        d2: float,
        sigma: float,
        r: float,
        T: float,
        option_type: str
    ) -> float:
        """
        Theta: Rate of change of option price with respect to time (time decay)

        Usually expressed as daily decay (divide by 365)

        Negative for long options (time decay hurts)
        """
        if T <= 0:
            return 0.0

        # First term (same for calls and puts)
        term1 = -(S * norm.pdf(d1) * sigma) / (2 * math.sqrt(T))

        if option_type.lower() == "call":
            term2 = -r * K * math.exp(-r * T) * norm.cdf(d2)
            theta_annual = term1 + term2
        else:  # put
            term2 = r * K * math.exp(-r * T) * norm.cdf(-d2)
            theta_annual = term1 + term2

        # Convert to daily theta
        theta_daily = theta_annual / 365.0

        return theta_daily

    @staticmethod
    def _calculate_vega(
        S: float,
        d1: float,
        T: float
    ) -> float:
        """
        Vega: Rate of change of option price with respect to volatility

        ν = S × N'(d1) × √T

        Usually expressed per 1% change in IV
        Same for calls and puts
        """
        if T <= 0:
            return 0.0

        vega = S * norm.pdf(d1) * math.sqrt(T)

        # Express per 1% IV change
        return vega / 100.0

    @staticmethod
    def _calculate_rho(
        K: float,
        d2: float,
        T: float,
        r: float,
        option_type: str
    ) -> float:
        """
        Rho: Rate of change of option price with respect to interest rate

        Usually expressed per 1% change in interest rate
        """
        if T <= 0:
            return 0.0

        if option_type.lower() == "call":
            rho = K * T * math.exp(-r * T) * norm.cdf(d2)
        else:  # put
            rho = -K * T * math.exp(-r * T) * norm.cdf(-d2)

        # Express per 1% rate change
        return rho / 100.0

    @staticmethod
    def calculate_implied_volatility(
        option_price: float,
        underlying_price: float,
        strike_price: float,
        days_to_expiration: int,
        risk_free_rate: float = 0.05,
        option_type: str = "call",
        max_iterations: int = 100,
        tolerance: float = 0.0001
    ) -> float:
        """
        Calculate implied volatility using Newton-Raphson method

        This is the REVERSE of Black-Scholes:
        Given option price, find the IV that produces that price

        Args:
            option_price: Current market price of option
            underlying_price: Stock price
            strike_price: Strike price
            days_to_expiration: Days to expiration
            risk_free_rate: Risk-free rate
            option_type: "call" or "put"
            max_iterations: Max iterations for convergence
            tolerance: Convergence tolerance

        Returns:
            Implied volatility (as decimal)
        """
        # Initial guess
        iv = 0.30  # Start with 30% volatility

        time_to_expiration = days_to_expiration / 365.0

        for _ in range(max_iterations):
            # Calculate option price with current IV guess
            price = GreeksCalculator._black_scholes_price(
                underlying_price,
                strike_price,
                time_to_expiration,
                iv,
                risk_free_rate,
                option_type
            )

            # Calculate vega (derivative of price with respect to IV)
            d1, d2 = GreeksCalculator._calculate_d1_d2(
                underlying_price,
                strike_price,
                time_to_expiration,
                iv,
                risk_free_rate
            )

            vega = GreeksCalculator._calculate_vega(
                underlying_price,
                d1,
                time_to_expiration
            ) * 100  # Convert back from per-1% to per-unit

            if abs(vega) < 1e-10:
                break

            # Newton-Raphson update
            price_diff = option_price - price
            iv = iv + price_diff / vega

            # Ensure IV stays positive
            iv = max(0.001, min(5.0, iv))

            # Check convergence
            if abs(price_diff) < tolerance:
                return iv

        logger.warning(f"IV calculation did not converge, returning {iv:.4f}")
        return iv

    @staticmethod
    def _black_scholes_price(
        S: float,
        K: float,
        T: float,
        sigma: float,
        r: float,
        option_type: str
    ) -> float:
        """
        Calculate Black-Scholes option price

        Call = S×N(d1) - K×e^(-rT)×N(d2)
        Put = K×e^(-rT)×N(-d2) - S×N(-d1)
        """
        if T <= 0:
            if option_type.lower() == "call":
                return max(0, S - K)
            else:
                return max(0, K - S)

        d1, d2 = GreeksCalculator._calculate_d1_d2(S, K, T, sigma, r)

        if option_type.lower() == "call":
            price = S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)
        else:  # put
            price = K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

        return max(0, price)


class ImpliedVolatilityMetrics:
    """
    Calculate IV rank and percentile metrics
    """

    @staticmethod
    def calculate_iv_rank(
        current_iv: float,
        iv_history_52w: list[float]
    ) -> float:
        """
        Calculate IV Rank (52-week)

        IV Rank = (Current IV - 52w Low) / (52w High - 52w Low) × 100

        Args:
            current_iv: Current implied volatility
            iv_history_52w: 52 weeks of IV history

        Returns:
            IV Rank (0-100)
        """
        if not iv_history_52w or len(iv_history_52w) < 2:
            return 50.0  # Neutral if no history

        iv_low = min(iv_history_52w)
        iv_high = max(iv_history_52w)

        if iv_high == iv_low:
            return 50.0

        iv_rank = ((current_iv - iv_low) / (iv_high - iv_low)) * 100
        return max(0, min(100, iv_rank))

    @staticmethod
    def calculate_iv_percentile(
        current_iv: float,
        iv_history: list[float]
    ) -> float:
        """
        Calculate IV Percentile

        What percentage of historical IVs are below current IV

        Args:
            current_iv: Current implied volatility
            iv_history: Historical IV data

        Returns:
            IV Percentile (0-100)
        """
        if not iv_history:
            return 50.0

        below_count = sum(1 for iv in iv_history if iv < current_iv)
        percentile = (below_count / len(iv_history)) * 100

        return percentile


# Add scipy to requirements.txt if not already there:
# scipy>=1.11.0
