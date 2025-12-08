"""
Market data integration using Alpaca API
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest, StockLatestQuoteRequest
from alpaca.data.timeframe import TimeFrame
from config import settings
from models import MarketData

logger = logging.getLogger(__name__)


class MarketDataService:
    """Service for fetching real-time market data"""

    def __init__(self):
        """Initialize Alpaca client with API credentials"""
        self.client = StockHistoricalDataClient(
            api_key=settings.alpaca_api_key,
            secret_key=settings.alpaca_secret_key
        )
        logger.info("MarketDataService initialized with Alpaca")

    def get_latest_data(self, ticker: str) -> Optional[MarketData]:
        """
        Get latest market data with technical indicators for a ticker

        Args:
            ticker: Stock symbol (e.g., 'NVDA')

        Returns:
            MarketData object with price and indicators
        """
        try:
            # Get latest 1-minute bars (last 100 for indicator calculation)
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=2)

            request = StockBarsRequest(
                symbol_or_symbols=ticker,
                timeframe=TimeFrame.Minute,
                start=start_time,
                end=end_time
            )

            bars = self.client.get_stock_bars(request)

            if ticker not in bars or len(bars[ticker]) < 50:
                logger.warning(f"Insufficient data for {ticker}")
                return None

            # Convert to DataFrame for indicator calculation
            df = bars[ticker].df

            # Calculate technical indicators
            df['vwap'] = self._calculate_vwap(df)
            df['ema9'] = df['close'].ewm(span=9, adjust=False).mean()
            df['ema20'] = df['close'].ewm(span=20, adjust=False).mean()
            df['ema50'] = df['close'].ewm(span=50, adjust=False).mean()

            # Get latest row
            latest = df.iloc[-1]

            return MarketData(
                ticker=ticker,
                timestamp=latest.name,
                price=float(latest['close']),
                open=float(latest['open']),
                high=float(latest['high']),
                low=float(latest['low']),
                volume=int(latest['volume']),
                vwap=float(latest['vwap']),
                ema9=float(latest['ema9']),
                ema20=float(latest['ema20']),
                ema50=float(latest['ema50'])
            )

        except Exception as e:
            logger.error(f"Error fetching data for {ticker}: {e}")
            return None

    def get_multiple_tickers(self, tickers: List[str]) -> Dict[str, MarketData]:
        """
        Get latest data for multiple tickers

        Args:
            tickers: List of stock symbols

        Returns:
            Dictionary mapping ticker to MarketData
        """
        results = {}
        for ticker in tickers:
            data = self.get_latest_data(ticker)
            if data:
                results[ticker] = data
        return results

    def _calculate_vwap(self, df: pd.DataFrame) -> pd.Series:
        """
        Calculate Volume Weighted Average Price

        Args:
            df: DataFrame with OHLCV data

        Returns:
            Series with VWAP values
        """
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        return (typical_price * df['volume']).cumsum() / df['volume'].cumsum()

    def get_average_volume(self, ticker: str, periods: int = 20) -> int:
        """
        Get average volume over specified periods

        Args:
            ticker: Stock symbol
            periods: Number of periods to average

        Returns:
            Average volume
        """
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(days=5)  # Get more data to ensure we have enough

            request = StockBarsRequest(
                symbol_or_symbols=ticker,
                timeframe=TimeFrame.Minute,
                start=start_time,
                end=end_time
            )

            bars = self.client.get_stock_bars(request)

            if ticker not in bars or len(bars[ticker]) < periods:
                return 0

            df = bars[ticker].df
            return int(df['volume'].tail(periods).mean())

        except Exception as e:
            logger.error(f"Error calculating avg volume for {ticker}: {e}")
            return 0
