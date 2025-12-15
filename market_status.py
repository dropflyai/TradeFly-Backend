"""
Market Status Verification using Massive API
Provides real-time market status, handles holidays, early closes, and timezone
"""
import logging
import requests
from datetime import datetime
from typing import Dict, Optional
from dateutil import parser
import os

logger = logging.getLogger(__name__)


class MarketStatus:
    """
    Real-time market status verification using Massive API
    Replaces manual time calculations with API-verified market status
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.massive.com"
        self._cached_status = None
        self._cache_timestamp = None
        self._cache_ttl = 60  # Cache for 60 seconds

    def get_current_status(self) -> Dict:
        """
        Get current market status from Massive API

        Returns:
            Dict with keys:
                - market: "open", "closed", "extended-hours"
                - is_open: bool
                - is_pre_market: bool
                - is_after_hours: bool
                - server_time: datetime object (Eastern Time)
                - server_time_str: ISO format string
                - exchanges: dict of exchange statuses
        """
        # Check cache
        now = datetime.now()
        if self._cached_status and self._cache_timestamp:
            cache_age = (now - self._cache_timestamp).total_seconds()
            if cache_age < self._cache_ttl:
                logger.debug(f"Using cached market status (age: {cache_age:.1f}s)")
                return self._cached_status

        try:
            url = f"{self.base_url}/v1/marketstatus/now"
            params = {'apiKey': self.api_key}

            logger.info("📡 Fetching real-time market status from Massive API...")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            # Parse server time (comes in Eastern Time with timezone info)
            server_time = parser.parse(data['serverTime'])

            # Determine market state
            is_open = data['market'] == 'open'
            is_pre_market = data.get('earlyHours', False)
            is_after_hours = data.get('afterHours', False)

            # Normalize market status
            if is_open:
                market_state = "open"
            elif is_pre_market:
                market_state = "pre-market"
            elif is_after_hours:
                market_state = "after-hours"
            else:
                market_state = "closed"

            status = {
                'market': market_state,
                'is_open': is_open,
                'is_pre_market': is_pre_market,
                'is_after_hours': is_after_hours,
                'server_time': server_time,
                'server_time_str': data['serverTime'],
                'exchanges': data.get('exchanges', {}),
                'raw_response': data
            }

            # Cache the result
            self._cached_status = status
            self._cache_timestamp = now

            logger.info(
                f"✅ Market Status: {market_state.upper()} | "
                f"Time: {server_time.strftime('%Y-%m-%d %I:%M:%S %p %Z')} | "
                f"NYSE: {data['exchanges'].get('nyse', 'unknown')}"
            )

            return status

        except Exception as e:
            logger.error(f"❌ Error fetching market status: {e}")
            # Return conservative default (assume closed)
            return {
                'market': 'unknown',
                'is_open': False,
                'is_pre_market': False,
                'is_after_hours': False,
                'server_time': None,
                'server_time_str': None,
                'exchanges': {},
                'error': str(e)
            }

    def is_market_open(self) -> bool:
        """
        Check if market is currently open for trading

        Returns:
            True if market is open, False otherwise
        """
        status = self.get_current_status()
        return status.get('is_open', False)

    def is_extended_hours(self) -> bool:
        """
        Check if market is in extended hours (pre-market or after-hours)

        Returns:
            True if in extended hours, False otherwise
        """
        status = self.get_current_status()
        return status.get('is_pre_market', False) or status.get('is_after_hours', False)

    def get_market_time(self) -> Optional[datetime]:
        """
        Get current market time (Eastern Time)

        Returns:
            datetime object in Eastern Time, or None if unavailable
        """
        status = self.get_current_status()
        return status.get('server_time')

    def get_status_summary(self) -> str:
        """
        Get human-readable status summary

        Returns:
            String like "OPEN (Mon Dec 15, 2025 1:13 PM ET)"
        """
        status = self.get_current_status()

        if status.get('error'):
            return f"ERROR: {status['error']}"

        market_state = status['market'].upper()
        server_time = status.get('server_time')

        if server_time:
            time_str = server_time.strftime('%a %b %d, %Y %I:%M %p %Z')
            return f"{market_state} ({time_str})"
        else:
            return market_state


# Global instance (initialized in main app)
_market_status_instance: Optional[MarketStatus] = None


def init_market_status(api_key: str):
    """Initialize global market status instance"""
    global _market_status_instance
    _market_status_instance = MarketStatus(api_key)
    logger.info("✅ Market status verification initialized")


def get_market_status() -> Optional[MarketStatus]:
    """Get global market status instance"""
    return _market_status_instance


def is_market_open() -> bool:
    """Quick check if market is open"""
    if _market_status_instance:
        return _market_status_instance.is_market_open()
    logger.warning("Market status not initialized, assuming closed")
    return False
