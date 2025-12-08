"""
News & Catalyst Service
Monitors news, Fed announcements, earnings, and market-moving events
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import httpx
from config import settings

logger = logging.getLogger(__name__)


class NewsService:
    """Service for fetching and analyzing market news and catalysts"""

    def __init__(self):
        self.benzinga_key = getattr(settings, 'benzinga_api_key', None)
        self.news_api_key = getattr(settings, 'news_api_key', None)
        logger.info("NewsService initialized")

    async def get_stock_news(self, ticker: str, hours_back: int = 2) -> List[Dict]:
        """
        Get recent news for a specific ticker

        Args:
            ticker: Stock symbol (e.g., 'NVDA')
            hours_back: How many hours back to search

        Returns:
            List of news items with sentiment and relevance
        """
        news_items = []

        # Try Benzinga first (best for trading)
        if self.benzinga_key:
            benzinga_news = await self._fetch_benzinga_news(ticker, hours_back)
            news_items.extend(benzinga_news)

        # Fallback to NewsAPI if Benzinga not available
        if not news_items and self.news_api_key:
            newsapi_news = await self._fetch_newsapi_news(ticker, hours_back)
            news_items.extend(newsapi_news)

        # Fallback to free sources (Yahoo Finance, etc.)
        if not news_items:
            free_news = await self._fetch_free_news(ticker, hours_back)
            news_items.extend(free_news)

        return news_items

    async def _fetch_benzinga_news(self, ticker: str, hours_back: int) -> List[Dict]:
        """Fetch news from Benzinga API (premium, trader-focused)"""
        if not self.benzinga_key:
            return []

        try:
            since = datetime.now() - timedelta(hours=hours_back)

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.benzinga.com/api/v2/news",
                    params={
                        "token": self.benzinga_key,
                        "tickers": ticker,
                        "since": since.isoformat(),
                        "pageSize": 10
                    },
                    timeout=10.0
                )

                if response.status_code == 200:
                    data = response.json()
                    return [{
                        "source": "Benzinga",
                        "title": item.get("title", ""),
                        "summary": item.get("body", "")[:200],
                        "url": item.get("url", ""),
                        "published": item.get("created", ""),
                        "sentiment": self._analyze_sentiment(item.get("title", "")),
                        "importance": "HIGH"  # Benzinga news is curated
                    } for item in data if ticker.upper() in item.get("stocks", [])]

        except Exception as e:
            logger.error(f"Error fetching Benzinga news: {e}")

        return []

    async def _fetch_newsapi_news(self, ticker: str, hours_back: int) -> List[Dict]:
        """Fetch news from NewsAPI.org"""
        if not self.news_api_key:
            return []

        try:
            since = datetime.now() - timedelta(hours=hours_back)

            # Search for ticker + company name for better results
            company_names = {
                "NVDA": "NVIDIA",
                "TSLA": "Tesla",
                "AAPL": "Apple",
                "AMD": "AMD",
                "MSFT": "Microsoft",
                "GOOGL": "Google Alphabet",
                "AMZN": "Amazon",
                "META": "Meta Facebook"
            }
            search_term = f"{ticker} OR {company_names.get(ticker, ticker)}"

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://newsapi.org/v2/everything",
                    params={
                        "apiKey": self.news_api_key,
                        "q": search_term,
                        "from": since.isoformat(),
                        "sortBy": "publishedAt",
                        "language": "en",
                        "pageSize": 10
                    },
                    timeout=10.0
                )

                if response.status_code == 200:
                    data = response.json()
                    return [{
                        "source": item["source"]["name"],
                        "title": item.get("title", ""),
                        "summary": item.get("description", "")[:200],
                        "url": item.get("url", ""),
                        "published": item.get("publishedAt", ""),
                        "sentiment": self._analyze_sentiment(item.get("title", "")),
                        "importance": self._assess_importance(item.get("title", ""))
                    } for item in data.get("articles", [])]

        except Exception as e:
            logger.error(f"Error fetching NewsAPI news: {e}")

        return []

    async def _fetch_free_news(self, ticker: str, hours_back: int) -> List[Dict]:
        """
        Fetch news from free sources (Yahoo Finance RSS, etc.)
        This is a fallback when no API keys are provided
        """
        try:
            # Yahoo Finance RSS feed
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US",
                    timeout=10.0
                )

                if response.status_code == 200:
                    # Parse RSS feed (simplified - you'd use feedparser library in production)
                    return [{
                        "source": "Yahoo Finance",
                        "title": f"News available for {ticker}",
                        "summary": "Free news feed - upgrade to paid API for details",
                        "url": f"https://finance.yahoo.com/quote/{ticker}/news",
                        "published": datetime.now().isoformat(),
                        "sentiment": "NEUTRAL",
                        "importance": "MEDIUM"
                    }]

        except Exception as e:
            logger.error(f"Error fetching free news: {e}")

        return []

    def _analyze_sentiment(self, text: str) -> str:
        """
        Simple sentiment analysis based on keywords
        In production, you'd use GPT-5 or a sentiment model
        """
        text_lower = text.lower()

        # Positive keywords
        positive = ["beats", "surges", "rally", "gains", "upgrade", "bullish",
                   "approval", "record", "strong", "growth", "jumps"]

        # Negative keywords
        negative = ["falls", "drops", "misses", "downgrade", "bearish", "concern",
                   "plunges", "crash", "weak", "decline", "losses"]

        pos_count = sum(1 for word in positive if word in text_lower)
        neg_count = sum(1 for word in negative if word in text_lower)

        if pos_count > neg_count:
            return "POSITIVE"
        elif neg_count > pos_count:
            return "NEGATIVE"
        else:
            return "NEUTRAL"

    def _assess_importance(self, title: str) -> str:
        """Assess news importance based on keywords"""
        title_lower = title.lower()

        # High importance keywords
        high_importance = ["earnings", "fda", "federal reserve", "fed", "merger",
                          "acquisition", "buyout", "ceo", "guidance", "lawsuit"]

        if any(keyword in title_lower for keyword in high_importance):
            return "HIGH"
        else:
            return "MEDIUM"

    async def get_market_news(self, hours_back: int = 4) -> List[Dict]:
        """
        Get broad market news (Fed announcements, CPI, etc.)
        """
        market_keywords = [
            "Federal Reserve",
            "Jerome Powell",
            "interest rates",
            "CPI",
            "inflation",
            "GDP",
            "jobs report",
            "unemployment"
        ]

        news_items = []

        for keyword in market_keywords:
            if self.news_api_key:
                try:
                    since = datetime.now() - timedelta(hours=hours_back)

                    async with httpx.AsyncClient() as client:
                        response = await client.get(
                            "https://newsapi.org/v2/everything",
                            params={
                                "apiKey": self.news_api_key,
                                "q": keyword,
                                "from": since.isoformat(),
                                "sortBy": "publishedAt",
                                "language": "en",
                                "pageSize": 3
                            },
                            timeout=10.0
                        )

                        if response.status_code == 200:
                            data = response.json()
                            for item in data.get("articles", []):
                                news_items.append({
                                    "source": item["source"]["name"],
                                    "title": item.get("title", ""),
                                    "summary": item.get("description", "")[:200],
                                    "url": item.get("url", ""),
                                    "published": item.get("publishedAt", ""),
                                    "sentiment": self._analyze_sentiment(item.get("title", "")),
                                    "importance": "HIGH",
                                    "category": "MARKET"
                                })

                except Exception as e:
                    logger.error(f"Error fetching market news for '{keyword}': {e}")
                    continue

        return news_items[:5]  # Return top 5 most recent

    async def get_economic_calendar_events(self) -> List[Dict]:
        """
        Get today's scheduled economic events (Fed announcements, etc.)
        This would integrate with Trading Economics API or similar
        """
        # Placeholder - in production, integrate with economic calendar API
        # For now, return common known events

        today = datetime.now()
        day_of_week = today.weekday()

        # Common scheduled events
        events = []

        # CPI usually second Wednesday of month
        # Fed announcements are scheduled (check fedcalendar.com)
        # Jobs report first Friday of month

        # This is a simplified placeholder
        events.append({
            "event": "Check economic calendar for today's events",
            "time": "Various",
            "importance": "HIGH",
            "impact": "Could cause high volatility",
            "url": "https://www.forexfactory.com/calendar"
        })

        return events

    def create_news_summary(self, ticker: str, news_items: List[Dict]) -> str:
        """
        Create a formatted summary of news for GPT-5 analysis

        Args:
            ticker: Stock symbol
            news_items: List of news items

        Returns:
            Formatted string for GPT-5
        """
        if not news_items:
            return f"No significant news for {ticker} in the past 2 hours."

        summary = f"\n═══ RECENT NEWS FOR {ticker} ═══\n\n"

        for idx, item in enumerate(news_items[:3], 1):  # Top 3 news items
            summary += f"{idx}. [{item['importance']}] {item['title']}\n"
            summary += f"   Source: {item['source']}\n"
            summary += f"   Sentiment: {item['sentiment']}\n"
            summary += f"   Summary: {item['summary']}\n\n"

        return summary

    def create_market_news_summary(self, market_news: List[Dict]) -> str:
        """Create a formatted summary of market-wide news"""
        if not market_news:
            return "No major market-moving news in the past 4 hours."

        summary = "\n═══ MARKET-WIDE NEWS & EVENTS ═══\n\n"

        for idx, item in enumerate(market_news[:3], 1):
            summary += f"{idx}. {item['title']}\n"
            summary += f"   Sentiment: {item['sentiment']}\n"
            summary += f"   Impact: Could affect overall market direction\n\n"

        return summary
