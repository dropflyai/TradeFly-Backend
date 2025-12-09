"""
Market Hours Detection - Live Trading Hours Tracking
"""
from datetime import datetime, time
import pytz

class MarketHours:
    """Track live market hours and trading sessions"""

    # US Market timezone
    ET = pytz.timezone('America/New_York')

    # Market hours (ET)
    MARKET_OPEN = time(9, 30)
    MARKET_CLOSE = time(16, 0)
    PREMARKET_START = time(4, 0)
    AFTERHOURS_END = time(20, 0)

    @classmethod
    def get_current_time(cls) -> datetime:
        """Get current time in ET"""
        return datetime.now(cls.ET)

    @classmethod
    def get_market_status(cls) -> dict:
        """
        Get current market status

        Returns:
            dict with:
            - status: OPEN, CLOSED, PRE_MARKET, AFTER_HOURS
            - current_time: Current ET time
            - next_open: Next market open time
            - next_close: Next market close time
        """
        now = cls.get_current_time()
        current_time = now.time()
        day_of_week = now.weekday()  # 0=Monday, 6=Sunday

        # Weekend check
        if day_of_week >= 5:  # Saturday or Sunday
            return {
                'status': 'CLOSED',
                'session': 'Weekend',
                'current_time': now.isoformat(),
                'is_market_open': False,
                'is_trading_hours': False,
                'message': 'Markets closed for weekend'
            }

        # Determine session
        if cls.MARKET_OPEN <= current_time < cls.MARKET_CLOSE:
            status = 'OPEN'
            session = 'Regular Hours'
            is_market_open = True
            is_trading_hours = True
            message = f'Market OPEN - Closes at {cls.MARKET_CLOSE.strftime("%I:%M %p")} ET'

        elif cls.PREMARKET_START <= current_time < cls.MARKET_OPEN:
            status = 'PRE_MARKET'
            session = 'Pre-Market'
            is_market_open = False
            is_trading_hours = False
            message = f'Pre-market - Opens at {cls.MARKET_OPEN.strftime("%I:%M %p")} ET'

        elif cls.MARKET_CLOSE <= current_time < cls.AFTERHOURS_END:
            status = 'AFTER_HOURS'
            session = 'After Hours'
            is_market_open = False
            is_trading_hours = False
            message = f'After hours - Closed at {cls.MARKET_CLOSE.strftime("%I:%M %p")} ET'

        else:
            status = 'CLOSED'
            session = 'Closed'
            is_market_open = False
            is_trading_hours = False
            message = 'Markets closed'

        return {
            'status': status,
            'session': session,
            'current_time': now.isoformat(),
            'current_time_et': now.strftime('%I:%M:%S %p ET'),
            'is_market_open': is_market_open,
            'is_trading_hours': is_trading_hours,
            'message': message,
            'day_of_week': now.strftime('%A')
        }

    @classmethod
    def is_market_open(cls) -> bool:
        """Check if market is currently open"""
        status = cls.get_market_status()
        return status['is_market_open']

    @classmethod
    def get_session_type(cls) -> str:
        """Get current session: REGULAR, PRE_MARKET, AFTER_HOURS, CLOSED"""
        return cls.get_market_status()['status']
