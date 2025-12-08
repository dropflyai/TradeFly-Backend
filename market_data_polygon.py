"""
Polygon.io Market Data Provider
Real-time and accurate market data with professional-grade quality
"""
import logging
from datetime import datetime, timedelta
from typing import Optional
import requests
import pandas as pd
from models import MarketData

logger = logging.getLogger(__name__)


class PolygonMarketDataService:
    """
    Professional market data from Polygon.io
    - Real-time quotes
    - Accurate pricing
    - High-quality historical data
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.polygon.io"
        logger.info("Polygon.io data service initialized")

    def get_latest_data(self, ticker: str) -> Optional[MarketData]:
        """
        Get latest market data with technical indicators for a ticker

        Args:
            ticker: Stock symbol (e.g., "AAPL")

        Returns:
            MarketData object with latest price and indicators
        """
        try:
            # Get latest quote for current price
            quote_url = f"{self.base_url}/v2/last/trade/{ticker}"
            quote_params = {"apiKey": self.api_key}

            quote_response = requests.get(quote_url, params=quote_params, timeout=10)
            quote_response.raise_for_status()
            quote_data = quote_response.json()

            if quote_data.get("status") != "OK":
                logger.warning(f"No quote data for {ticker}: {quote_data.get('status')}")
                return None

            current_price = quote_data["results"]["p"]  # Latest trade price

            # Get aggregates (bars) for indicators - last 100 1-minute bars
            end_date = datetime.now()
            start_date = end_date - timedelta(hours=3)

            aggs_url = f"{self.base_url}/v2/aggs/ticker/{ticker}/range/1/minute/{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}"
            aggs_params = {
                "apiKey": self.api_key,
                "adjusted": "true",
                "sort": "asc",
                "limit": 100
            }

            aggs_response = requests.get(aggs_url, params=aggs_params, timeout=10)
            aggs_response.raise_for_status()
            aggs_data = aggs_response.json()

            if aggs_data.get("resultsCount", 0) == 0:
                logger.warning(f"No aggregate data for {ticker}")
                # Return basic data without indicators
                return MarketData(
                    ticker=ticker,
                    timestamp=datetime.now(),
                    price=current_price,
                    open=current_price,
                    high=current_price,
                    low=current_price,
                    volume=0,
                    vwap=current_price,
                    ema9=current_price,
                    ema20=current_price,
                    ema50=current_price
                )

            # Convert to DataFrame
            bars = aggs_data["results"]
            df = pd.DataFrame(bars)

            # Rename columns to match our expected format
            df = df.rename(columns={
                "o": "open",
                "h": "high",
                "l": "low",
                "c": "close",
                "v": "volume",
                "t": "timestamp"
            })

            # Calculate technical indicators
            df['ema9'] = df['close'].ewm(span=9, adjust=False).mean()
            df['ema20'] = df['close'].ewm(span=20, adjust=False).mean()
            df['ema50'] = df['close'].ewm(span=50, adjust=False).mean()

            # Calculate VWAP
            df['typical_price'] = (df['high'] + df['low'] + df['close']) / 3
            df['tpv'] = df['typical_price'] * df['volume']
            df['vwap'] = df['tpv'].cumsum() / df['volume'].cumsum()

            # Get latest values
            latest = df.iloc[-1]
            first = df.iloc[0]

            return MarketData(
                ticker=ticker,
                timestamp=datetime.now(),
                price=current_price,  # Use real-time price from quote
                open=float(first['open']),
                high=float(df['high'].max()),
                low=float(df['low'].min()),
                volume=int(df['volume'].sum()),
                vwap=float(latest['vwap']),
                ema9=float(latest['ema9']),
                ema20=float(latest['ema20']),
                ema50=float(latest['ema50']) if len(df) >= 50 else float(latest['ema20'])
            )

        except requests.exceptions.RequestException as e:
            logger.error(f"Network error fetching Polygon data for {ticker}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error fetching Polygon data for {ticker}: {e}")
            return None

    def get_average_volume(self, ticker: str, periods: int = 20) -> int:
        """
        Get average volume over last N periods

        Args:
            ticker: Stock symbol
            periods: Number of periods to average

        Returns:
            Average volume
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(hours=3)

            url = f"{self.base_url}/v2/aggs/ticker/{ticker}/range/1/minute/{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}"
            params = {
                "apiKey": self.api_key,
                "adjusted": "true",
                "sort": "asc",
                "limit": periods
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get("resultsCount", 0) == 0:
                return 0

            bars = data["results"]
            volumes = [bar["v"] for bar in bars]

            return int(sum(volumes) / len(volumes)) if volumes else 0

        except Exception as e:
            logger.error(f"Error calculating average volume for {ticker}: {e}")
            return 0

    def get_snapshot(self, ticker: str) -> Optional[dict]:
        """
        Get real-time snapshot of a ticker

        Args:
            ticker: Stock symbol

        Returns:
            Dictionary with snapshot data
        """
        try:
            url = f"{self.base_url}/v2/snapshot/locale/us/markets/stocks/tickers/{ticker}"
            params = {"apiKey": self.api_key}

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get("status") != "OK":
                return None

            return data.get("ticker")

        except Exception as e:
            logger.error(f"Error fetching snapshot for {ticker}: {e}")
            return None


# Add to requirements.txt if not already there:
# requests>=2.31.0
