"""
Top Market Movers Scanner
Dynamically identifies stocks with significant movement for options scanning

Uses Massive API (formerly Polygon.io) to get ALL optionable stocks
Then filters by daily volume and % change to find the best opportunities
"""
import logging
from typing import List, Dict
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
import os
import requests
from supabase_client import get_db

logger = logging.getLogger(__name__)


class TopMoversScanner:
    """
    Scan market for top moving stocks to trade options on
    Uses Massive API to get ALL optionable stocks, then filters by movement
    Updates every 5 minutes with fresh movers
    """

    def __init__(self):
        self.last_update = None
        self.cache_ttl = 300  # 5 minutes
        self.cached_movers = []  # List of symbols
        self.cached_movers_data = []  # Full data with prices, volume, etc.
        self.api_key = os.getenv('MASSIVE_API_KEY')

        # Cache for all optionable tickers (updated daily)
        self.all_optionable_tickers = []
        self.tickers_last_update = None
        self.tickers_cache_ttl = 86400  # 24 hours

    def get_dynamic_watchlist(
        self,
        min_change_percent: float = 0.5,  # Lower threshold to catch more stocks
        max_stocks: int = 500  # Dramatically increased from 100
    ) -> List[str]:
        """
        Get dynamic watchlist of top moving stocks - TRUE MARKET-WIDE SCANNING
        Uses Massive API to scan ALL optionable stocks

        Args:
            min_change_percent: Minimum % move to include (default 0.5% - very sensitive)
            max_stocks: Maximum stocks to return (default 500)

        Returns:
            List of ticker symbols with significant movement across ENTIRE market
        """
        # Check cache
        if self.last_update and (datetime.now() - self.last_update).seconds < self.cache_ttl:
            logger.info(f"⚡ Using cached watchlist ({len(self.cached_movers)} stocks)")
            return self.cached_movers[:max_stocks]

        logger.info("🔍 MASSIVE API MARKET-WIDE SCAN - Analyzing ALL optionable stocks...")

        # Get all stocks with active options from Massive API
        all_tickers = self._get_all_optionable_tickers()
        logger.info(f"  📊 Found {len(all_tickers)} total optionable stocks")

        # Get current day's snapshots with volume and price change
        movers = self._get_market_snapshots(all_tickers, max_stocks=max_stocks * 2)  # Get 2x for filtering
        logger.info(f"  ✅ Retrieved market data for {len(movers)} stocks")

        # Filter by minimum change and sort
        filtered_movers = [
            m for m in movers
            if abs(m.get("change_percent", 0)) >= min_change_percent
        ]

        # Sort by absolute % change (biggest movers first)
        sorted_movers = sorted(
            filtered_movers,
            key=lambda x: abs(x.get("change_percent", 0)),
            reverse=True
        )

        # Extract symbols
        symbols = [m["symbol"] for m in sorted_movers][:max_stocks]

        # Update cache
        self.cached_movers = symbols
        self.cached_movers_data = sorted_movers[:max_stocks]  # Cache full data
        self.last_update = datetime.now()

        # Save to Supabase database
        db = get_db()
        if db.is_connected():
            try:
                db.save_market_movers(sorted_movers[:max_stocks], category="mixed")
            except Exception as e:
                logger.warning(f"Failed to save market movers to database: {e}")

        logger.info(f"📊 MARKET-WIDE WATCHLIST: {len(symbols)} stocks (>{min_change_percent}% move) from {len(all_tickers)} optionable stocks")
        return symbols

    def _get_all_optionable_tickers(self) -> List[str]:
        """
        Get ALL stocks with active options from Massive API
        Cached for 24 hours since this list doesn't change often
        """
        # Check cache
        now = datetime.now()
        if self.tickers_last_update and (now - self.tickers_last_update).seconds < self.tickers_cache_ttl:
            if self.all_optionable_tickers:
                logger.info(f"⚡ Using cached optionable tickers list ({len(self.all_optionable_tickers)} stocks)")
                return self.all_optionable_tickers

        logger.info("📥 Fetching ALL optionable tickers from Massive API...")

        try:
            # Use Massive API's grouped daily bars to get all active stocks
            # This is more efficient than querying the tickers endpoint
            url = f"https://api.massive.com/v2/aggs/grouped/locale/us/market/stocks/{(datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')}"

            params = {
                'adjusted': 'true',
                'apiKey': self.api_key
            }

            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            if data.get('resultsCount', 0) > 0:
                results = data.get('results', [])

                # Filter for stocks with reasonable volume (likely have options)
                tickers = [
                    r['T'] for r in results
                    if r.get('v', 0) > 100000  # At least 100K volume
                    and '.' not in r['T']  # Exclude OTC/special symbols
                    and len(r['T']) <= 5  # Reasonable ticker length
                ]

                self.all_optionable_tickers = tickers
                self.tickers_last_update = now

                logger.info(f"✅ Fetched {len(tickers)} liquid stocks from Massive API")
                return tickers

        except Exception as e:
            logger.error(f"❌ Error fetching tickers from Massive API: {e}")

        # Fallback: Use comprehensive stock list
        fallback_tickers = self._get_comprehensive_fallback_list()
        logger.warning(f"⚠️  Using fallback ticker list ({len(fallback_tickers)} stocks)")
        return fallback_tickers

    def _get_market_snapshots(self, tickers: List[str], max_stocks: int = 1000) -> List[Dict]:
        """
        Get REAL-TIME market snapshots using Stock Advanced plan
        Uses Massive API's snapshot endpoint for intraday data during market hours
        Falls back to daily aggregates when market is closed
        """
        movers = []
        now = datetime.now()

        # Market hours: 9:30 AM - 4:00 PM ET (Monday-Friday)
        # During market hours, use REAL-TIME snapshots from Stock Advanced
        market_open_hour = 9
        market_open_minute = 30
        market_close_hour = 16

        is_market_hours = (
            now.weekday() < 5 and  # Monday-Friday
            (now.hour > market_open_hour or (now.hour == market_open_hour and now.minute >= market_open_minute)) and
            now.hour < market_close_hour
        )

        if is_market_hours:
            logger.info("📊 MARKET IS OPEN - Using REAL-TIME Stock Advanced snapshots!")
            movers = self._get_realtime_snapshots(tickers, max_stocks)
            if movers:
                return movers
            logger.warning("⚠️  Real-time snapshots failed, falling back to daily aggregates...")

        # Market closed or real-time failed - use daily aggregates (end-of-day data)
        try:
            # Use grouped daily bars for after-hours or when real-time fails
            today = datetime.now().strftime('%Y-%m-%d')
            url = f"https://api.massive.com/v2/aggs/grouped/locale/us/market/stocks/{today}"

            params = {
                'adjusted': 'true',
                'apiKey': self.api_key
            }

            logger.info(f"📡 Fetching daily aggregates from Massive API...")
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            if data.get('resultsCount', 0) > 0:
                all_results = data.get('results', [])
                logger.info(f"  ✅ Received {len(all_results)} stock records from Massive API")

                # Filter for tickers we care about and extract % change
                ticker_set = set(tickers)  # Convert to set for O(1) lookup

                for result in all_results:
                    ticker = result.get('T')

                    if ticker not in ticker_set:
                        continue

                    # Calculate % change from open to close
                    open_price = result.get('o', 0)
                    close_price = result.get('c', 0)
                    volume = result.get('v', 0)

                    if open_price and close_price and volume > 10000:
                        change_pct = ((close_price - open_price) / open_price) * 100

                        movers.append({
                            "symbol": ticker,
                            "change_percent": float(change_pct),
                            "volume": int(volume),
                            "price": float(close_price)
                        })

                logger.info(f"  ✅ Filtered {len(movers)} stocks with movement and volume")
                return movers[:max_stocks]

        except Exception as e:
            logger.error(f"❌ Error getting Massive API grouped daily data: {e}")
            logger.warning("⚠️  Falling back to yesterday's data...")

        # Try yesterday's data if today isn't available yet
        try:
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            url = f"https://api.massive.com/v2/aggs/grouped/locale/us/market/stocks/{yesterday}"

            params = {
                'adjusted': 'true',
                'apiKey': self.api_key
            }

            logger.info(f"📡 Fetching yesterday's market data from Massive API...")
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            if data.get('resultsCount', 0) > 0:
                all_results = data.get('results', [])
                ticker_set = set(tickers)

                for result in all_results:
                    ticker = result.get('T')
                    if ticker not in ticker_set:
                        continue

                    open_price = result.get('o', 0)
                    close_price = result.get('c', 0)
                    volume = result.get('v', 0)

                    if open_price and close_price and volume > 10000:
                        change_pct = ((close_price - open_price) / open_price) * 100

                        movers.append({
                            "symbol": ticker,
                            "change_percent": float(change_pct),
                            "volume": int(volume),
                            "price": float(close_price)
                        })

                logger.info(f"  ✅ Using yesterday's data: {len(movers)} stocks")
                return movers[:max_stocks]

        except Exception as e2:
            logger.error(f"❌ Error getting yesterday's data: {e2}")

        return movers

    def _get_realtime_snapshots(self, tickers: List[str], max_stocks: int = 1000) -> List[Dict]:
        """
        Get REAL-TIME snapshots using Stock Advanced plan
        This provides live intraday prices and % changes during market hours

        Uses Massive API's /v2/snapshot/locale/us/markets/stocks/tickers endpoint
        Included in Stock Advanced plan ($199/month)
        """
        movers = []

        try:
            # Stock Advanced allows batch snapshot requests
            # Process in batches of 100 tickers per request
            batch_size = 100

            for i in range(0, min(len(tickers), max_stocks), batch_size):
                batch_tickers = tickers[i:i+batch_size]
                ticker_list = ','.join(batch_tickers)

                url = f"https://api.massive.com/v2/snapshot/locale/us/markets/stocks/tickers"

                params = {
                    'tickers': ticker_list,
                    'apiKey': self.api_key
                }

                logger.info(f"📡 Fetching REAL-TIME snapshots for {len(batch_tickers)} stocks (batch {i//batch_size + 1})...")
                response = requests.get(url, params=params, timeout=15)
                response.raise_for_status()

                data = response.json()

                if data.get('status') == 'OK' and 'tickers' in data:
                    for ticker_data in data['tickers']:
                        ticker = ticker_data.get('ticker')

                        # Get real-time data from snapshot
                        day_data = ticker_data.get('day', {})
                        prev_day = ticker_data.get('prevDay', {})

                        # Current price and volume
                        current_price = day_data.get('c', 0)  # Current close
                        open_price = day_data.get('o', 0)      # Today's open
                        volume = day_data.get('v', 0)          # Current volume

                        # Calculate REAL-TIME % change from today's open
                        if open_price and current_price and volume > 10000:
                            change_pct = ((current_price - open_price) / open_price) * 100

                            movers.append({
                                "symbol": ticker,
                                "change_percent": float(change_pct),
                                "volume": int(volume),
                                "price": float(current_price)
                            })

                logger.info(f"  ✅ Retrieved {len(movers)} real-time movers so far...")

            logger.info(f"🎯 Stock Advanced REAL-TIME SCAN: Found {len(movers)} stocks with movement")
            return movers[:max_stocks]

        except Exception as e:
            logger.error(f"❌ Error getting real-time snapshots from Stock Advanced: {e}")
            return []


    def _get_comprehensive_fallback_list(self) -> List[str]:
        """
        Comprehensive list of 500+ actively traded stocks with options
        Includes S&P 500 + popular mid-caps like CVNA
        """
        return [
            # === MEGA CAPS & ETFs ===
            "SPY", "QQQ", "IWM", "DIA", "AAPL", "MSFT", "GOOGL", "GOOG", "AMZN", "NVDA",
            "META", "TSLA", "BRK.B", "UNH", "JNJ", "XOM", "V", "PG", "JPM", "MA",

            # === LARGE CAPS ===
            "HD", "CVX", "LLY", "ABBV", "MRK", "KO", "PEP", "COST", "AVGO", "TMO",
            "WMT", "MCD", "ACN", "CSCO", "ABT", "CRM", "DHR", "VZ", "ADBE", "NKE",
            "NFLX", "DIS", "CMCSA", "TXN", "PM", "UPS", "RTX", "HON", "INTC", "AMD",

            # === MID-CAPS WITH HIGH OPTIONS VOLUME ===
            "CVNA",  # Carvana - user mentioned this!
            "PLTR", "RIVN", "LCID", "NIO", "SOFI", "COIN", "HOOD", "GME", "AMC",
            "BB", "SNAP", "UBER", "LYFT", "DKNG", "DASH", "ABNB", "RBLX", "U",

            # === TECH ===
            "ORCL", "QCOM", "AMAT", "ADI", "NOW", "INTU", "PANW", "SNOW", "NET", "DDOG",
            "CRWD", "ZS", "OKTA", "MDB", "TEAM", "WDAY", "FTNT", "CDNS", "SNPS", "LRCX",

            # === FINANCE ===
            "BAC", "WFC", "C", "GS", "MS", "SCHW", "AXP", "BLK", "SPGI", "MMC",
            "BX", "APO", "KKR", "ICE", "CME", "COF", "USB", "PNC", "TFC", "FITB",

            # === HEALTHCARE ===
            "PFE", "TMO", "ABT", "DHR", "BMY", "AMGN", "GILD", "REGN", "VRTX", "ISRG",
            "CI", "CVS", "HUM", "BIIB", "ILMN", "MRNA", "BSX", "SYK", "MDT", "ZTS",

            # === CONSUMER ===
            "SBUX", "CMG", "YUM", "QSR", "MCD", "DPZ", "LULU", "DECK", "ULTA", "TJX",
            "LOW", "TGT", "COST", "WMT", "AMZN", "ETSY", "SHOP", "MELI", "SE", "BABA",

            # === ENERGY ===
            "XOM", "CVX", "COP", "SLB", "EOG", "MPC", "PSX", "VLO", "OXY", "HAL",
            "BKR", "DVN", "FANG", "HES", "MRO", "APA", "CTRA", "OVV", "PR", "EQT",

            # === INDUSTRIALS ===
            "CAT", "DE", "BA", "GE", "RTX", "LMT", "NOC", "GD", "HON", "MMM",
            "UPS", "FDX", "NSC", "UNP", "CSX", "DAL", "UAL", "AAL", "LUV", "JBLU",

            # === MATERIALS ===
            "LIN", "APD", "ECL", "SHW", "DD", "DOW", "NEM", "FCX", "GOLD", "SCCO",

            # === UTILITIES ===
            "NEE", "DUK", "SO", "D", "AEP", "EXC", "SRE", "XEL", "WEC", "ES",

            # === REAL ESTATE ===
            "PLD", "AMT", "EQIX", "PSA", "DLR", "WELL", "AVB", "EQR", "VTR", "O",

            # === COMMUNICATION ===
            "GOOGL", "META", "DIS", "NFLX", "CMCSA", "VZ", "T", "TMUS", "CHTR", "PARA",

            # === SEMICONDUCTORS ===
            "NVDA", "AMD", "INTC", "QCOM", "AVGO", "TXN", "ADI", "AMAT", "LRCX", "KLAC",
            "ASML", "MRVL", "NXPI", "MCHP", "ON", "SWKS", "QRVO", "MU", "WDC", "STX",

            # === BIOTECH ===
            "GILD", "AMGN", "REGN", "VRTX", "BIIB", "ILMN", "MRNA", "ALNY", "SGEN", "INCY",
            "BGNE", "EXAS", "SRPT", "TECH", "UTHR", "JAZZ", "IONS", "RARE", "FOLD", "ARWR",

            # === RETAIL ===
            "AMZN", "WMT", "HD", "COST", "TGT", "LOW", "TJX", "ROST", "BBY", "DG",

            # === AUTOMOTIVE ===
            "TSLA", "F", "GM", "RIVN", "LCID", "NIO", "XPEV", "LI", "TM", "HMC",

            # === SOFTWARE ===
            "MSFT", "ORCL", "CRM", "ADBE", "NOW", "INTU", "WDAY", "TEAM", "ZM", "DOCU",
            "SNOW", "DDOG", "NET", "CRWD", "ZS", "OKTA", "MDB", "TWLO", "ESTC", "DOMO",

            # === PAYMENTS ===
            "V", "MA", "AXP", "PYPL", "SQ", "COIN", "AFRM", "SOFI", "NU", "MELI",

            # === E-COMMERCE ===
            "AMZN", "SHOP", "EBAY", "ETSY", "MELI", "SE", "BABA", "JD", "PDD", "CPNG",

            # === CLOUD/AI ===
            "MSFT", "GOOGL", "AMZN", "CRM", "NOW", "SNOW", "AI", "PLTR", "PATH", "GTLB",

            # === GAMING ===
            "RBLX", "EA", "TTWO", "ATVI", "U", "DKNG", "PENN", "LVS", "MGM", "WYNN",

            # === TRANSPORTATION ===
            "UPS", "FDX", "XPO", "JBHT", "ODFL", "CHRW", "KNX", "EXPD", "LSTR", "ARCB",

            # === BANKS (REGIONAL) ===
            "BAC", "WFC", "C", "USB", "PNC", "TFC", "CFG", "KEY", "HBAN", "RF",
            "FITB", "MTB", "ZION", "CMA", "WTFC", "FHN", "SNV", "BOKF", "EWBC", "SBCF",

            # === INSURANCE ===
            "BRK.B", "PGR", "ALL", "TRV", "CB", "AIG", "MET", "PRU", "AFL", "HIG",

            # === RESTAURANTS ===
            "MCD", "SBUX", "CMG", "YUM", "QSR", "DPZ", "WEN", "JACK", "TXRH", "DRI",

            # === APPAREL ===
            "NKE", "LULU", "DECK", "UAA", "VFC", "HBI", "PVH", "RL", "CPRI", "TPI"
        ]

    def _get_yahoo_gainers(self) -> List[Dict]:
        """Get top gainers from Yahoo Finance screener - REAL DATA"""
        try:
            import requests
            from bs4 import BeautifulSoup

            # Yahoo Finance day gainers URL (updated to new endpoint)
            url = "https://finance.yahoo.com/research-hub/screener/day_gainers"

            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }

            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            gainers = []

            # Try pandas read_html method (more reliable)
            try:
                tables = pd.read_html(response.content)
                if tables and len(tables) > 0:
                    df = tables[0]

                    for _, row in df.head(250).iterrows():  # Top 250 gainers (5x increase)
                        try:
                            symbol = row.get('Symbol', '')
                            change_pct = row.get('% Change', 0)

                            # Clean up the percentage
                            if isinstance(change_pct, str):
                                change_pct = float(change_pct.replace('%', '').replace('+', ''))

                            if symbol and abs(change_pct) > 0:
                                gainers.append({
                                    "symbol": symbol,
                                    "change_percent": float(change_pct)
                                })
                        except Exception:
                            continue

                    logger.info(f"✅ Fetched {len(gainers)} real gainers from Yahoo Finance")
                    return gainers
            except Exception as e:
                logger.debug(f"pandas read_html failed: {e}")

            # Fallback: Use yfinance to get movers from popular stocks
            logger.warning("Yahoo scraping failed, using yfinance fallback for gainers")
            return self._get_fallback_movers(direction="gainers")

        except Exception as e:
            logger.error(f"Error getting gainers: {e}")
            return self._get_fallback_movers(direction="gainers")

    def _get_yahoo_losers(self) -> List[Dict]:
        """Get top losers from Yahoo Finance screener - REAL DATA"""
        try:
            import requests

            url = "https://finance.yahoo.com/research-hub/screener/day_losers"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }

            response = requests.get(url, headers=headers, timeout=10)

            try:
                tables = pd.read_html(response.content)
                if tables and len(tables) > 0:
                    df = tables[0]

                    losers = []
                    for _, row in df.head(250).iterrows():  # Top 250 losers (5x increase)
                        try:
                            symbol = row.get('Symbol', '')
                            change_pct = row.get('% Change', 0)

                            if isinstance(change_pct, str):
                                change_pct = float(change_pct.replace('%', '').replace('+', ''))

                            if symbol and change_pct < 0:
                                losers.append({
                                    "symbol": symbol,
                                    "change_percent": float(change_pct)
                                })
                        except Exception:
                            continue

                    logger.info(f"✅ Fetched {len(losers)} real losers from Yahoo Finance")
                    return losers
            except Exception:
                pass

            logger.warning("Yahoo scraping failed, using yfinance fallback for losers")
            return self._get_fallback_movers(direction="losers")

        except Exception as e:
            logger.error(f"Error getting losers: {e}")
            return self._get_fallback_movers(direction="losers")

    def _get_yahoo_active(self) -> List[Dict]:
        """Get most active stocks from Yahoo Finance - REAL DATA"""
        try:
            import requests

            url = "https://finance.yahoo.com/markets/stocks/most-active/"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }

            response = requests.get(url, headers=headers, timeout=10)

            try:
                tables = pd.read_html(response.content)
                if tables and len(tables) > 0:
                    df = tables[0]

                    actives = []
                    for _, row in df.head(250).iterrows():  # Top 250 most active (5x increase)
                        try:
                            symbol = row.get('Symbol', '')
                            change_pct = row.get('% Change', 0)

                            if isinstance(change_pct, str):
                                change_pct = float(change_pct.replace('%', '').replace('+', ''))

                            if symbol:
                                actives.append({
                                    "symbol": symbol,
                                    "change_percent": float(change_pct) if change_pct else 0.0
                                })
                        except Exception:
                            continue

                    logger.info(f"✅ Fetched {len(actives)} real most active from Yahoo Finance")
                    return actives
            except Exception:
                pass

            logger.warning("Yahoo scraping failed, using yfinance fallback for most active")
            return self._get_fallback_movers(direction="active")

        except Exception as e:
            logger.error(f"Error getting most active: {e}")
            return self._get_fallback_movers(direction="active")

    def _get_yahoo_undervalued(self) -> List[Dict]:
        """Get undervalued stocks from Yahoo Finance screener - captures value plays"""
        try:
            import requests

            url = "https://finance.yahoo.com/research-hub/screener/undervalued_large_caps"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }

            response = requests.get(url, headers=headers, timeout=10)

            try:
                tables = pd.read_html(response.content)
                if tables and len(tables) > 0:
                    df = tables[0]

                    undervalued = []
                    for _, row in df.head(100).iterrows():  # Top 100 undervalued
                        try:
                            symbol = row.get('Symbol', '')
                            change_pct = row.get('% Change', 0)

                            if isinstance(change_pct, str):
                                change_pct = float(change_pct.replace('%', '').replace('+', ''))

                            if symbol:
                                undervalued.append({
                                    "symbol": symbol,
                                    "change_percent": float(change_pct) if change_pct else 0.0
                                })
                        except Exception:
                            continue

                    logger.info(f"✅ Fetched {len(undervalued)} undervalued stocks from Yahoo Finance")
                    return undervalued
            except Exception:
                pass

            logger.warning("Yahoo undervalued scraping failed")
            return []

        except Exception as e:
            logger.error(f"Error getting undervalued: {e}")
            return []

    def _get_yahoo_growth_tech(self) -> List[Dict]:
        """Get growth technology stocks from Yahoo Finance screener"""
        try:
            import requests

            url = "https://finance.yahoo.com/research-hub/screener/growth_technology_stocks"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }

            response = requests.get(url, headers=headers, timeout=10)

            try:
                tables = pd.read_html(response.content)
                if tables and len(tables) > 0:
                    df = tables[0]

                    growth_tech = []
                    for _, row in df.head(100).iterrows():  # Top 100 growth tech
                        try:
                            symbol = row.get('Symbol', '')
                            change_pct = row.get('% Change', 0)

                            if isinstance(change_pct, str):
                                change_pct = float(change_pct.replace('%', '').replace('+', ''))

                            if symbol:
                                growth_tech.append({
                                    "symbol": symbol,
                                    "change_percent": float(change_pct) if change_pct else 0.0
                                })
                        except Exception:
                            continue

                    logger.info(f"✅ Fetched {len(growth_tech)} growth tech stocks from Yahoo Finance")
                    return growth_tech
            except Exception:
                pass

            logger.warning("Yahoo growth tech scraping failed")
            return []

        except Exception as e:
            logger.error(f"Error getting growth tech: {e}")
            return []

    def _get_fallback_movers(self, direction: str = "gainers") -> List[Dict]:
        """
        Fallback method: Scan a large universe of stocks using yfinance
        when Yahoo Finance scraping fails
        """
        try:
            # Get a broad market universe (S&P 500 + popular stocks)
            popular_stocks = [
                # Mega caps
                "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK-B",
                # Tech
                "AMD", "INTC", "CRM", "ORCL", "ADBE", "CSCO", "AVGO",
                # Finance
                "JPM", "BAC", "WFC", "GS", "MS", "C", "V", "MA",
                # Consumer
                "WMT", "HD", "NKE", "MCD", "SBUX", "DIS", "NFLX",
                # Energy
                "XOM", "CVX", "COP", "SLB",
                # Healthcare
                "JNJ", "UNH", "PFE", "ABBV", "MRK",
                # Crypto/Fintech
                "COIN", "SQ", "PYPL", "SOFI", "HOOD",
                # EV/Auto
                "F", "GM", "RIVN", "LCID", "NIO",
                # Meme/Volatile
                "GME", "AMC", "BB", "PLTR", "SNAP",
                # ETFs
                "SPY", "QQQ", "IWM", "DIA"
            ]

            movers = []
            for symbol in popular_stocks[:30]:  # Check first 30 to avoid timeout
                try:
                    ticker = yf.Ticker(symbol)
                    info = ticker.info
                    change_pct = info.get('regularMarketChangePercent', 0)

                    if change_pct:
                        movers.append({
                            "symbol": symbol,
                            "change_percent": float(change_pct)
                        })
                except Exception:
                    continue

            # Filter based on direction
            if direction == "gainers":
                movers = [m for m in movers if m["change_percent"] > 0]
                movers.sort(key=lambda x: x["change_percent"], reverse=True)
            elif direction == "losers":
                movers = [m for m in movers if m["change_percent"] < 0]
                movers.sort(key=lambda x: x["change_percent"])
            else:  # active
                movers.sort(key=lambda x: abs(x["change_percent"]), reverse=True)

            return movers[:20]  # Return top 20

        except Exception as e:
            logger.error(f"Fallback movers failed: {e}")
            return []

    def get_market_movers_display(self) -> List[Dict]:
        """
        Get formatted market movers for frontend display

        Returns:
            List of dicts with symbol, price, change, volume
        """
        # Ensure we have cached movers - trigger scan if needed
        if not self.cached_movers_data:
            self.get_dynamic_watchlist()

        # Return cached data from Massive API (no Yahoo Finance calls needed)
        return self.cached_movers_data[:20]  # Top 20 for display
