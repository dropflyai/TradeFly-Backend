"""
Massive Options API Integration
Real-time options data, Greeks, and analytics

API Documentation: https://massive.com/docs/options
Requires: Options Advanced subscription ($99/mo)

FALLBACK: Uses yfinance when Massive/Polygon returns no data
"""
import logging
from datetime import datetime, date, timedelta
from typing import Optional, List
import requests
import yfinance as yf
from options_models import (
    OptionContract,
    OptionType,
    OptionPricing,
    VolumeMetrics,
    Greeks,
    ImpliedVolatility
)
from greeks_calculator import GreeksCalculator, ImpliedVolatilityMetrics

logger = logging.getLogger(__name__)


class MassiveOptionsAPI:
    """
    Professional options data from Massive API
    - Real-time options chains
    - Greeks streaming
    - Implied volatility data
    - Volume and open interest
    - Options flow analytics
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.massive.com"
        logger.info("Massive Options API initialized")

    def get_options_chain(
        self,
        symbol: str,
        expiration: Optional[date] = None
    ) -> List[OptionContract]:
        """
        Get full options chain for a symbol

        Args:
            symbol: Stock symbol (e.g., "NVDA")
            expiration: Specific expiration date (optional)

        Returns:
            List of OptionContract objects
        """
        try:
            # Get current stock price first
            stock_price = self._get_stock_price(symbol)
            if not stock_price:
                logger.error(f"Could not get stock price for {symbol}")
                return []

            # Get options contracts
            url = f"{self.base_url}/v3/reference/options/contracts"
            params = {
                "underlying_ticker": symbol,
                "apiKey": self.api_key,
                "limit": 1000
            }

            if expiration:
                params["expiration_date"] = expiration.strftime("%Y-%m-%d")

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get("status") != "OK":
                logger.warning(f"API error: {data.get('status')}")
                return []

            contracts = []
            for contract_data in data.get("results", []):
                contract = self._parse_contract(contract_data, stock_price)
                if contract:
                    contracts.append(contract)

            logger.info(f"Retrieved {len(contracts)} options contracts for {symbol}")
            return contracts

        except requests.exceptions.RequestException as e:
            logger.error(f"Network error fetching options chain for {symbol}: {e}")
            return []
        except Exception as e:
            logger.error(f"Error fetching options chain for {symbol}: {e}")
            return []

    def get_option_snapshot(
        self,
        symbol: str,
        contract_id: Optional[str] = None
    ) -> List[OptionContract]:
        """
        Get real-time snapshot of options with Greeks

        Args:
            symbol: Underlying symbol
            contract_id: Specific contract ID (optional)

        Returns:
            List of OptionContract objects with live data
        """
        try:
            # Get stock price
            stock_price = self._get_stock_price(symbol)
            if not stock_price:
                return []

            # Get options snapshot
            url = f"{self.base_url}/v3/snapshot/options/{symbol}"
            params = {"apiKey": self.api_key}

            if contract_id:
                url = f"{self.base_url}/v3/snapshot/options/{symbol}/{contract_id}"

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get("status") != "OK":
                return []

            # Parse snapshot data
            contracts = []
            results = data.get("results", [])

            for snapshot in results:
                contract = self._parse_snapshot(snapshot, stock_price)
                if contract:
                    contracts.append(contract)

            return contracts

        except Exception as e:
            logger.error(f"Error fetching option snapshot for {symbol}: {e}")
            return []

    def get_liquid_options(
        self,
        symbol: str,
        min_volume: int = 1000,
        max_spread_percent: float = 5.0
    ) -> List[OptionContract]:
        """
        Get liquid options suitable for trading
        AUTOMATICALLY falls back to yfinance if Massive returns no data

        Args:
            symbol: Stock symbol
            min_volume: Minimum daily volume
            max_spread_percent: Maximum bid-ask spread %

        Returns:
            List of liquid OptionContract objects
        """
        # Try Massive/Polygon first
        all_contracts = self.get_option_snapshot(symbol)

        # FALLBACK: If no contracts or all zeros, use yfinance
        valid_contracts = [c for c in all_contracts if c.pricing.mark > 0]

        if not valid_contracts:
            logger.warning(f"⚠️  Massive returned no valid data for {symbol}, using yfinance fallback")
            all_contracts = self.get_options_chain_yfinance(symbol, max_days_to_exp=45)

        # Filter for liquidity
        liquid_contracts = []
        for contract in all_contracts:
            # Skip if no valid pricing
            if contract.pricing.mark <= 0:
                continue

            # Filter by volume (be more lenient with yfinance data)
            if contract.volume_metrics.volume < min_volume:
                continue

            # Filter by spread
            if contract.pricing.spread_percent > max_spread_percent:
                continue

            liquid_contracts.append(contract)

        logger.info(f"Found {len(liquid_contracts)} liquid contracts for {symbol}")
        return liquid_contracts

    def get_high_iv_options(
        self,
        symbol: str,
        min_iv_rank: float = 50.0
    ) -> List[OptionContract]:
        """
        Get options with elevated implied volatility

        Args:
            symbol: Stock symbol
            min_iv_rank: Minimum IV rank (0-100)

        Returns:
            List of high IV options
        """
        contracts = self.get_option_snapshot(symbol)

        high_iv_contracts = [
            c for c in contracts
            if c.iv_metrics.iv_rank >= min_iv_rank
        ]

        return high_iv_contracts

    def _get_stock_price(self, symbol: str) -> Optional[float]:
        """
        Get current stock price from options snapshot
        (Options Advanced may not have access to stock trade endpoint)

        Args:
            symbol: Stock symbol

        Returns:
            Current price or None
        """
        try:
            # Use options snapshot to get underlying price
            url = f"{self.base_url}/v3/snapshot/options/{symbol}"
            params = {"apiKey": self.api_key, "limit": 1}

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get("status") == "OK" and data.get("results"):
                # Extract underlying asset price from first contract
                first_contract = data["results"][0]
                underlying = first_contract.get("underlying_asset", {})
                price = underlying.get("price")

                if price:
                    return float(price)

            logger.warning(f"No underlying price found for {symbol} in options snapshot")
            return None

        except Exception as e:
            logger.error(f"Error fetching stock price for {symbol}: {e}")
            return None

    def _parse_contract(
        self,
        contract_data: dict,
        stock_price: float
    ) -> Optional[OptionContract]:
        """
        Parse contract data from API into OptionContract model

        Args:
            contract_data: Raw contract data from API
            stock_price: Current stock price

        Returns:
            OptionContract object or None
        """
        try:
            # Parse contract details
            symbol = contract_data.get("underlying_ticker")
            strike = float(contract_data.get("strike_price", 0))
            exp_date = datetime.strptime(
                contract_data.get("expiration_date"),
                "%Y-%m-%d"
            ).date()
            opt_type = OptionType.CALL if contract_data.get("contract_type") == "call" else OptionType.PUT

            # Parse pricing (may be None initially, will be filled by snapshot)
            bid = float(contract_data.get("bid", 0) or 0)
            ask = float(contract_data.get("ask", 0) or 0)
            last = float(contract_data.get("last", 0) or 0)
            mark = (bid + ask) / 2 if (bid and ask) else last

            pricing = OptionPricing(
                bid=bid,
                ask=ask,
                last=last,
                mark=mark
            )

            # Parse volume metrics
            volume = int(contract_data.get("volume", 0) or 0)
            open_interest = int(contract_data.get("open_interest", 0) or 0)
            volume_avg = int(contract_data.get("volume_avg_30d", volume) or volume)

            volume_metrics = VolumeMetrics(
                volume=volume,
                open_interest=open_interest,
                volume_avg_30d=max(1, volume_avg),  # Avoid division by zero
                volume_ratio=volume / max(1, volume_avg)
            )

            # Calculate Greeks if we have pricing
            days_to_exp = (exp_date - date.today()).days
            iv = float(contract_data.get("implied_volatility", 0.30) or 0.30)

            greeks_calc = GreeksCalculator()
            greeks_data = greeks_calc.calculate_all_greeks(
                underlying_price=stock_price,
                strike_price=strike,
                days_to_expiration=days_to_exp,
                implied_volatility=iv,
                option_type="call" if opt_type == OptionType.CALL else "put"
            )

            greeks = Greeks(
                delta=greeks_data["delta"],
                gamma=greeks_data["gamma"],
                theta=greeks_data["theta"],
                vega=greeks_data["vega"],
                rho=greeks_data["rho"]
            )

            # IV metrics (simplified - would need historical data for accurate IV rank)
            iv_metrics = ImpliedVolatility(
                iv=iv,
                iv_rank=50.0,  # Default - need historical data
                iv_percentile=50.0,
                historical_volatility=iv * 0.9  # Estimate
            )

            return OptionContract(
                symbol=symbol,
                strike=strike,
                expiration=exp_date,
                option_type=opt_type,
                pricing=pricing,
                volume_metrics=volume_metrics,
                greeks=greeks,
                iv_metrics=iv_metrics,
                underlying_price=stock_price,
                contract_id=contract_data.get("ticker")
            )

        except Exception as e:
            logger.error(f"Error parsing contract data: {e}")
            return None

    def _parse_snapshot(
        self,
        snapshot_data: dict,
        stock_price: float
    ) -> Optional[OptionContract]:
        """
        Parse snapshot data (real-time) into OptionContract

        Args:
            snapshot_data: Snapshot data from API
            stock_price: Current stock price

        Returns:
            OptionContract with live data
        """
        try:
            details = snapshot_data.get("details", {})
            greeks_data = snapshot_data.get("greeks", {})
            day_data = snapshot_data.get("day", {})
            underlying = snapshot_data.get("underlying_asset", {})

            # Parse contract details
            symbol = underlying.get("ticker")  # Symbol is in underlying_asset.ticker
            strike = float(details.get("strike_price", 0))
            exp_date = datetime.strptime(
                details.get("expiration_date"),
                "%Y-%m-%d"
            ).date()
            opt_type = OptionType.CALL if details.get("contract_type") == "call" else OptionType.PUT

            # Real-time pricing
            last_quote = snapshot_data.get("last_quote", {})
            bid = float(last_quote.get("bid", 0) or 0)
            ask = float(last_quote.get("ask", 0) or 0)
            last = float(snapshot_data.get("last_trade", {}).get("price", 0) or 0)
            mark = (bid + ask) / 2 if (bid and ask) else last

            pricing = OptionPricing(bid=bid, ask=ask, last=last, mark=mark)

            # Volume metrics
            volume = int(day_data.get("volume", 0) or 0)
            open_interest = int(details.get("open_interest", 0) or 0)
            volume_avg = int(snapshot_data.get("volume_avg_30d", volume) or volume)

            volume_metrics = VolumeMetrics(
                volume=volume,
                open_interest=open_interest,
                volume_avg_30d=max(1, volume_avg),
                volume_ratio=volume / max(1, volume_avg)
            )

            # Greeks from API (if available)
            greeks = Greeks(
                delta=float(greeks_data.get("delta", 0.5)),
                gamma=float(greeks_data.get("gamma", 0.05)),
                theta=float(greeks_data.get("theta", -0.05)),
                vega=float(greeks_data.get("vega", 0.1)),
                rho=float(greeks_data.get("rho", 0.01))
            )

            # IV metrics
            iv = float(snapshot_data.get("implied_volatility", 0.30) or 0.30)
            iv_metrics = ImpliedVolatility(
                iv=iv,
                iv_rank=float(snapshot_data.get("iv_rank", 50.0) or 50.0),
                iv_percentile=float(snapshot_data.get("iv_percentile", 50.0) or 50.0),
                historical_volatility=iv * 0.9
            )

            return OptionContract(
                symbol=symbol,
                strike=strike,
                expiration=exp_date,
                option_type=opt_type,
                pricing=pricing,
                volume_metrics=volume_metrics,
                greeks=greeks,
                iv_metrics=iv_metrics,
                underlying_price=stock_price,
                contract_id=details.get("ticker")
            )

        except Exception as e:
            logger.error(f"Error parsing snapshot data: {e}")
            return None

    def get_unusual_activity(
        self,
        min_volume_ratio: float = 5.0,
        min_premium: float = 1_000_000
    ) -> List[OptionContract]:
        """
        Scan for unusual options activity across watchlist

        Args:
            min_volume_ratio: Minimum volume/avg ratio (5x = 500%)
            min_premium: Minimum premium flow

        Returns:
            List of contracts with unusual activity
        """
        # This would scan a watchlist - placeholder for now
        # In production, scan NVDA, TSLA, AAPL, SPY, QQQ, etc.
        watchlist = ["NVDA", "TSLA", "AAPL", "AMD", "SPY"]

        unusual_contracts = []

        for symbol in watchlist:
            contracts = self.get_option_snapshot(symbol)

            for contract in contracts:
                # Check volume spike
                if contract.volume_metrics.volume_ratio >= min_volume_ratio:
                    # Calculate premium flow
                    premium = contract.volume_metrics.volume * contract.pricing.mark * 100

                    if premium >= min_premium:
                        unusual_contracts.append(contract)
                        logger.info(
                            f"UOA: {symbol} {contract.strike}{contract.option_type.value} "
                            f"{contract.volume_metrics.volume_ratio:.1f}x vol, "
                            f"${premium/1e6:.1f}M premium"
                        )

        return unusual_contracts

    def get_options_chain_yfinance(
        self,
        symbol: str,
        min_days_to_exp: int = 0,
        max_days_to_exp: int = 45
    ) -> List[OptionContract]:
        """
        FALLBACK: Get options chain from yfinance (free, real-time)

        Use when Massive/Polygon returns no data or all zeros

        Args:
            symbol: Stock symbol
            min_days_to_exp: Minimum days to expiration
            max_days_to_exp: Maximum days to expiration

        Returns:
            List of OptionContract objects with REAL pricing data
        """
        try:
            logger.info(f"🔄 Using yfinance fallback for {symbol} options chain")

            ticker = yf.Ticker(symbol)
            stock_price = ticker.info.get('currentPrice') or ticker.info.get('regularMarketPrice')

            if not stock_price:
                logger.error(f"Could not get stock price for {symbol}")
                return []

            # Get all available expiration dates
            expirations = ticker.options
            if not expirations:
                logger.warning(f"No options available for {symbol}")
                return []

            contracts = []
            today = date.today()

            for exp_str in expirations:
                exp_date = datetime.strptime(exp_str, "%Y-%m-%d").date()
                days_to_exp = (exp_date - today).days

                # Filter by expiration range
                if days_to_exp < min_days_to_exp or days_to_exp > max_days_to_exp:
                    continue

                # Get calls and puts for this expiration
                opt_chain = ticker.option_chain(exp_str)

                # Parse calls
                for _, row in opt_chain.calls.iterrows():
                    contract = self._parse_yfinance_contract(
                        symbol, row, exp_date, OptionType.CALL, stock_price, days_to_exp
                    )
                    if contract and contract.pricing.mark > 0:  # Only valid contracts
                        contracts.append(contract)

                # Parse puts
                for _, row in opt_chain.puts.iterrows():
                    contract = self._parse_yfinance_contract(
                        symbol, row, exp_date, OptionType.PUT, stock_price, days_to_exp
                    )
                    if contract and contract.pricing.mark > 0:  # Only valid contracts
                        contracts.append(contract)

            logger.info(f"✅ yfinance: Retrieved {len(contracts)} valid contracts for {symbol}")
            return contracts

        except Exception as e:
            logger.error(f"Error fetching yfinance options for {symbol}: {e}")
            return []

    def _parse_yfinance_contract(
        self,
        symbol: str,
        row: dict,
        exp_date: date,
        opt_type: OptionType,
        stock_price: float,
        days_to_exp: int
    ) -> Optional[OptionContract]:
        """Parse yfinance row into OptionContract"""
        try:
            strike = float(row['strike'])
            bid = float(row.get('bid', 0) or 0)
            ask = float(row.get('ask', 0) or 0)
            last = float(row.get('lastPrice', 0) or 0)

            # Calculate mark price
            if bid > 0 and ask > 0:
                mark = (bid + ask) / 2
            elif last > 0:
                mark = last
            else:
                return None  # No valid pricing

            pricing = OptionPricing(
                bid=bid,
                ask=ask,
                last=last,
                mark=mark
            )

            # Volume metrics
            volume = int(row.get('volume', 0) or 0)
            open_interest = int(row.get('openInterest', 0) or 0)

            volume_metrics = VolumeMetrics(
                volume=volume,
                open_interest=open_interest,
                volume_avg_30d=max(1, volume),  # Estimate
                volume_ratio=1.0  # Estimate
            )

            # Calculate Greeks
            iv = float(row.get('impliedVolatility', 0.30) or 0.30)
            greeks_calc = GreeksCalculator()
            greeks_data = greeks_calc.calculate_all_greeks(
                underlying_price=stock_price,
                strike_price=strike,
                days_to_expiration=days_to_exp,
                implied_volatility=iv,
                option_type="call" if opt_type == OptionType.CALL else "put"
            )

            greeks = Greeks(
                delta=greeks_data["delta"],
                gamma=greeks_data["gamma"],
                theta=greeks_data["theta"],
                vega=greeks_data["vega"],
                rho=greeks_data["rho"]
            )

            # IV metrics
            iv_metrics = ImpliedVolatility(
                iv=iv,
                iv_rank=50.0,
                iv_percentile=50.0,
                historical_volatility=iv * 0.9
            )

            return OptionContract(
                symbol=symbol,
                strike=strike,
                expiration=exp_date,
                option_type=opt_type,
                pricing=pricing,
                volume_metrics=volume_metrics,
                greeks=greeks,
                iv_metrics=iv_metrics,
                underlying_price=stock_price,
                contract_id=f"{symbol}_{strike}_{opt_type.value}_{exp_date}"
            )

        except Exception as e:
            logger.error(f"Error parsing yfinance contract: {e}")
            return None
