"""
Supabase client for storing signals and user data
"""
import logging
from datetime import datetime
from typing import List, Optional
from supabase import create_client, Client
from config import settings
from models import TradingSignal

logger = logging.getLogger(__name__)


class SupabaseClient:
    """Client for Supabase database operations"""

    def __init__(self):
        self.client: Client = create_client(
            settings.supabase_url,
            settings.supabase_service_key
        )
        logger.info("Supabase client initialized")

    def save_signal(self, signal: TradingSignal) -> bool:
        """
        Save a trading signal to Supabase

        Args:
            signal: TradingSignal object to save

        Returns:
            True if successful, False otherwise
        """
        try:
            data = {
                "ticker": signal.ticker,
                "signal_type": signal.signal_type.value,
                "quality": signal.quality.value,
                "current_price": signal.current_price,
                "entry_price": signal.entry_price,
                "stop_loss": signal.stop_loss,
                "take_profit_1": signal.take_profit_1,
                "take_profit_2": signal.take_profit_2,
                "vwap": signal.vwap,
                "ema_9": signal.ema9,  # Database uses underscore format
                "ema_20": signal.ema20,  # Database uses underscore format
                # Note: ema50 not in database schema, omitting
                "volume": signal.volume,
                "avg_volume": signal.avg_volume,
                "ai_reasoning": signal.ai_reasoning,
                "confidence_score": signal.confidence_score,
                "risk_factors": signal.risk_factors,
                # Note: related_news and market_news not in original schema, might need migration
                "timeframe": signal.timeframe,
                "is_active": signal.is_active,
                "created_at": signal.timestamp.isoformat()
            }

            result = self.client.table("trading_signals").insert(data).execute()
            logger.info(f"Saved signal for {signal.ticker}: {signal.signal_type.value} ({signal.quality.value})")
            return True

        except Exception as e:
            logger.error(f"Error saving signal to Supabase: {e}")
            return False

    def get_active_signals(self) -> List[dict]:
        """
        Get all active signals from Supabase

        Returns:
            List of active signal dictionaries
        """
        try:
            result = self.client.table("trading_signals")\
                .select("*")\
                .eq("is_active", True)\
                .order("created_at", desc=True)\
                .execute()

            return result.data

        except Exception as e:
            logger.error(f"Error fetching active signals: {e}")
            return []

    def deactivate_old_signals(self, hours_old: int = 2):
        """
        Deactivate signals older than specified hours

        Args:
            hours_old: Number of hours after which to deactivate signals
        """
        try:
            cutoff_time = datetime.now().isoformat()

            # Deactivate signals older than cutoff
            result = self.client.table("trading_signals")\
                .update({"is_active": False})\
                .lt("created_at", cutoff_time)\
                .eq("is_active", True)\
                .execute()

            if result.data:
                logger.info(f"Deactivated {len(result.data)} old signals")

        except Exception as e:
            logger.error(f"Error deactivating old signals: {e}")

    def get_signal_count_today(self, ticker: Optional[str] = None) -> int:
        """
        Get count of signals created today

        Args:
            ticker: Optional ticker to filter by

        Returns:
            Number of signals today
        """
        try:
            today = datetime.now().date().isoformat()

            query = self.client.table("trading_signals")\
                .select("id", count="exact")\
                .gte("created_at", today)

            if ticker:
                query = query.eq("ticker", ticker)

            result = query.execute()
            return result.count or 0

        except Exception as e:
            logger.error(f"Error getting signal count: {e}")
            return 0

    def delete_duplicate_signals(self):
        """
        Delete duplicate signals for same ticker/type within 5 minutes
        Keeps the highest quality signal
        """
        try:
            # Get all active signals
            signals = self.get_active_signals()

            # Group by ticker and signal_type
            seen = {}
            duplicates = []

            for signal in signals:
                key = f"{signal['ticker']}_{signal['signal_type']}"

                if key in seen:
                    # Found duplicate - keep higher quality one
                    existing = seen[key]
                    quality_order = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}

                    if quality_order[signal['quality']] > quality_order[existing['quality']]:
                        # New signal is better, mark old as duplicate
                        duplicates.append(existing['id'])
                        seen[key] = signal
                    else:
                        # Existing is better, mark new as duplicate
                        duplicates.append(signal['id'])
                else:
                    seen[key] = signal

            # Delete duplicates
            if duplicates:
                for dup_id in duplicates:
                    self.client.table("trading_signals")\
                        .delete()\
                        .eq("id", dup_id)\
                        .execute()

                logger.info(f"Deleted {len(duplicates)} duplicate signals")

        except Exception as e:
            logger.error(f"Error deleting duplicates: {e}")
