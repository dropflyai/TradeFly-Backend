"""
Yahoo Finance Market Data Provider (No API Key Required)
Alternative to Alpaca - completely free, no signup needed
"""
import logging
from datetime import datetime
import yfinance as yf
import pandas as pd
from models import MarketData

logger = logging.getLogger(__name__)


class YahooMarketDataService:
    """
    Free market data from Yahoo Finance
    No API keys, no verification, no limits
    """

    def __init__(self):
        logger.info("Yahoo Finance data service initialized (FREE)")

    def get_latest_data(self, ticker: str) -> MarketData:
        """
        Get latest 1-minute bar data from Yahoo Finance
        Works 24/7 for crypto, extended hours for stocks

        Args:
            ticker: Stock symbol (e.g., "AAPL") or crypto (e.g., "BTC-USD")

        Returns:
            MarketData object with latest price and indicators
        """
        try:
            # Download 1-minute data - use 2 days to ensure we get data even after hours
            stock = yf.Ticker(ticker)
            df = stock.history(period="2d", interval="1m", prepost=True)

            if df.empty:
                logger.warning(f"No data for {ticker}")
                return None

            # Get latest bar
            latest = df.iloc[-1]

            # Calculate indicators
            df['ema9'] = df['Close'].ewm(span=9, adjust=False).mean()
            df['ema20'] = df['Close'].ewm(span=20, adjust=False).mean()
            df['ema50'] = df['Close'].ewm(span=50, adjust=False).mean()

            # Calculate VWAP
            df['typical_price'] = (df['High'] + df['Low'] + df['Close']) / 3
            df['tpv'] = df['typical_price'] * df['Volume']
            vwap = df['tpv'].sum() / df['Volume'].sum()

            return MarketData(
                ticker=ticker,
                timestamp=datetime.now(),
                price=latest['Close'],
                open=df.iloc[0]['Open'],
                high=df['High'].max(),
                low=df['Low'].min(),
                volume=int(latest['Volume']),
                vwap=vwap,
                ema9=df['ema9'].iloc[-1],
                ema20=df['ema20'].iloc[-1],
                ema50=df['ema50'].iloc[-1] if len(df) >= 50 else df['ema20'].iloc[-1]
            )

        except Exception as e:
            logger.error(f"Error fetching Yahoo data for {ticker}: {e}")
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
            stock = yf.Ticker(ticker)
            df = stock.history(period="1d", interval="1m")

            if len(df) < periods:
                return df['Volume'].mean()

            return int(df['Volume'].tail(periods).mean())

        except Exception as e:
            logger.error(f"Error calculating average volume: {e}")
            return 0


# Add to requirements.txt:
# yfinance==0.2.33
