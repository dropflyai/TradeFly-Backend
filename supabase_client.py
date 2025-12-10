"""
Supabase Database Client for TradeFly AI
Handles all database operations for signals, market movers, and paper trading
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from supabase import create_client, Client

logger = logging.getLogger(__name__)

class SupabaseDB:
    """Supabase database client for TradeFly"""

    def __init__(self):
        """Initialize Supabase client"""
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_SERVICE_KEY")  # Use service key for server-side

        if not self.url or not self.key:
            logger.warning("⚠️  Supabase credentials not found. Database features disabled.")
            self.client = None
            return

        try:
            self.client: Client = create_client(self.url, self.key)
            logger.info("✅ Supabase client initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Supabase: {e}")
            self.client = None

    def is_connected(self) -> bool:
        """Check if database is connected"""
        return self.client is not None

    def save_market_movers(self, movers: List[Dict], category: str = "mixed") -> bool:
        """Save market movers to database"""
        if not self.client:
            return False

        try:
            records = []
            now = datetime.utcnow().isoformat()

            for mover in movers:
                records.append({
                    "symbol": mover["symbol"],
                    "price": float(mover["price"]),
                    "change_percent": float(mover["change_percent"]),
                    "volume": int(mover["volume"]),
                    "category": category,
                    "scanned_at": now
                })

            for i in range(0, len(records), 100):
                batch = records[i:i+100]
                self.client.table("market_movers").insert(batch).execute()

            logger.info(f"💾 Saved {len(records)} market movers to database")
            return True

        except Exception as e:
            logger.error(f"❌ Error saving market movers: {e}")
            return False

    def save_signal(self, signal: Dict) -> bool:
        """Save options signal to database"""
        if not self.client:
            return False

        try:
            contract = signal.get("contract", {})
            greeks = contract.get("greeks", {})

            record = {
                "signal_id": signal.get("signal_id"),
                "symbol": contract.get("symbol"),
                "strategy": signal.get("strategy"),
                "action": signal.get("action"),
                "strike": float(contract.get("strike", 0)),
                "expiration": contract.get("expiration"),
                "option_type": contract.get("option_type"),
                "days_to_expiry": int(contract.get("days_to_expiry", 0)),
                "entry_price": float(signal.get("entry", 0)),
                "target_price": float(signal.get("target", 0)),
                "stop_loss": float(signal.get("stop_loss", 0)),
                "confidence": float(signal.get("confidence", 0)),
                "delta": float(greeks.get("delta", 0)) if greeks.get("delta") else None,
                "gamma": float(greeks.get("gamma", 0)) if greeks.get("gamma") else None,
                "theta": float(greeks.get("theta", 0)) if greeks.get("theta") else None,
                "vega": float(greeks.get("vega", 0)) if greeks.get("vega") else None,
                "underlying_price": float(contract.get("underlying_price", 0)) if contract.get("underlying_price") else None,
                "volume": int(contract.get("volume_metrics", {}).get("volume", 0)) if contract.get("volume_metrics") else None,
                "open_interest": int(contract.get("volume_metrics", {}).get("open_interest", 0)) if contract.get("volume_metrics") else None,
                "contract_data": json.dumps(signal),
                "expires_at": (datetime.utcnow() + timedelta(days=1)).isoformat()
            }

            self.client.table("options_signals").upsert(record).execute()
            return True

        except Exception as e:
            logger.error(f"❌ Error saving signal: {e}")
            return False

    def get_signals(self, strategy: Optional[str] = None, min_confidence: float = 0.0, limit: int = 20) -> List[Dict]:
        """Get options signals from database"""
        if not self.client:
            return []

        try:
            query = self.client.table("options_signals").select("*")

            if strategy:
                query = query.eq("strategy", strategy)

            if min_confidence > 0:
                query = query.gte("confidence", min_confidence)

            result = query.order("created_at", desc=True).limit(limit).execute()

            signals = []
            for row in result.data:
                signal_data = json.loads(row["contract_data"])
                signals.append(signal_data)

            return signals

        except Exception as e:
            logger.error(f"❌ Error getting signals: {e}")
            return []


# Global instance
_db_instance = None

def get_db() -> SupabaseDB:
    """Get global database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = SupabaseDB()
    return _db_instance
