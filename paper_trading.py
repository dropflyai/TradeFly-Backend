"""
Paper Trading System - Track Signal Performance
Learn which signals actually make money and improve over time
"""
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

from options_models import OptionsSignal, SignalAction

logger = logging.getLogger(__name__)


class TradeOutcome(Enum):
    """Possible trade outcomes"""
    PENDING = "pending"           # Still open
    HIT_TARGET = "hit_target"     # Won - hit profit target
    HIT_STOP = "hit_stop"         # Lost - hit stop loss
    EXPIRED_WORTHLESS = "expired" # Lost - option expired
    CLOSED_MANUAL = "closed"      # Manually closed
    BREAKEVEN = "breakeven"       # Closed near entry


@dataclass
class PaperTrade:
    """A paper trade tracking entry"""
    signal_id: str
    symbol: str
    strategy: str
    action: str

    # Entry details
    entry_price: float
    entry_time: datetime

    # Exit targets
    target_price: float
    stop_loss: float

    # Contract details
    strike: float
    option_type: str
    expiration: str

    # Tracking
    outcome: TradeOutcome = TradeOutcome.PENDING
    exit_price: Optional[float] = None
    exit_time: Optional[datetime] = None

    # Performance metrics
    profit_loss: Optional[float] = None
    profit_loss_percent: Optional[float] = None

    # Original confidence
    original_confidence: float = 0.0

    # Notes
    notes: str = ""


class PaperTradingEngine:
    """
    Paper trading engine to track signal performance
    Learns which signals actually work
    """

    def __init__(self, data_file: str = "paper_trades.json"):
        self.data_file = Path(data_file)
        self.trades: List[PaperTrade] = []
        self.load_trades()

    def load_trades(self):
        """Load existing paper trades from disk"""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.trades = [
                        PaperTrade(
                            **{**trade,
                               'entry_time': datetime.fromisoformat(trade['entry_time']),
                               'exit_time': datetime.fromisoformat(trade['exit_time']) if trade.get('exit_time') else None,
                               'outcome': TradeOutcome(trade['outcome'])
                            }
                        )
                        for trade in data
                    ]
                logger.info(f"Loaded {len(self.trades)} paper trades from {self.data_file}")
            except Exception as e:
                logger.error(f"Error loading paper trades: {e}")
                self.trades = []
        else:
            logger.info("No existing paper trades file - starting fresh")

    def save_trades(self):
        """Save paper trades to disk"""
        try:
            data = [
                {
                    **asdict(trade),
                    'entry_time': trade.entry_time.isoformat(),
                    'exit_time': trade.exit_time.isoformat() if trade.exit_time else None,
                    'outcome': trade.outcome.value
                }
                for trade in self.trades
            ]
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Saved {len(self.trades)} paper trades to {self.data_file}")
        except Exception as e:
            logger.error(f"Error saving paper trades: {e}")

    def add_signal(self, signal: OptionsSignal) -> PaperTrade:
        """
        Add a new signal to paper trading

        Args:
            signal: OptionsSignal to track

        Returns:
            PaperTrade object
        """
        trade = PaperTrade(
            signal_id=signal.signal_id,
            symbol=signal.contract.symbol,
            strategy=signal.strategy.value,
            action=signal.action.value,
            entry_price=signal.entry_price,
            entry_time=signal.timestamp,
            target_price=signal.target_price,
            stop_loss=signal.stop_loss,
            strike=signal.contract.strike,
            option_type=signal.contract.option_type,
            expiration=signal.contract.expiration,
            original_confidence=signal.confidence
        )

        self.trades.append(trade)
        self.save_trades()

        logger.info(f"Added paper trade: {signal.contract.symbol} ${signal.contract.strike} {signal.contract.option_type}")
        return trade

    def update_trade(
        self,
        signal_id: str,
        current_price: float,
        current_time: Optional[datetime] = None
    ) -> Optional[PaperTrade]:
        """
        Update a trade with current price and check if it hit targets

        Args:
            signal_id: ID of the signal/trade
            current_price: Current option price
            current_time: Current time (defaults to now)

        Returns:
            Updated PaperTrade if found
        """
        current_time = current_time or datetime.now()

        # Find the trade
        trade = next((t for t in self.trades if t.signal_id == signal_id), None)
        if not trade:
            return None

        # Skip if already closed
        if trade.outcome != TradeOutcome.PENDING:
            return trade

        # Check if hit target
        if current_price >= trade.target_price:
            trade.outcome = TradeOutcome.HIT_TARGET
            trade.exit_price = trade.target_price
            trade.exit_time = current_time
            trade.profit_loss = trade.target_price - trade.entry_price
            trade.profit_loss_percent = (trade.profit_loss / trade.entry_price) * 100
            trade.notes = f"Hit target at ${trade.target_price:.2f}"
            logger.info(f"✅ WINNER: {trade.symbol} hit target! +{trade.profit_loss_percent:.1f}%")
            self.save_trades()
            return trade

        # Check if hit stop
        if current_price <= trade.stop_loss:
            trade.outcome = TradeOutcome.HIT_STOP
            trade.exit_price = trade.stop_loss
            trade.exit_time = current_time
            trade.profit_loss = trade.stop_loss - trade.entry_price
            trade.profit_loss_percent = (trade.profit_loss / trade.entry_price) * 100
            trade.notes = f"Hit stop at ${trade.stop_loss:.2f}"
            logger.info(f"❌ LOSER: {trade.symbol} hit stop. {trade.profit_loss_percent:.1f}%")
            self.save_trades()
            return trade

        # Check if expired
        try:
            exp_date = datetime.strptime(trade.expiration, "%Y-%m-%d")
            if current_time >= exp_date:
                trade.outcome = TradeOutcome.EXPIRED_WORTHLESS
                trade.exit_price = 0.0
                trade.exit_time = current_time
                trade.profit_loss = -trade.entry_price
                trade.profit_loss_percent = -100.0
                trade.notes = "Expired worthless"
                logger.info(f"💀 EXPIRED: {trade.symbol} expired worthless. -100%")
                self.save_trades()
                return trade
        except:
            pass

        return trade

    def close_trade(
        self,
        signal_id: str,
        exit_price: float,
        reason: str = "Manual close"
    ) -> Optional[PaperTrade]:
        """
        Manually close a trade

        Args:
            signal_id: ID of the signal/trade
            exit_price: Price at which to close
            reason: Reason for closing

        Returns:
            Updated PaperTrade if found
        """
        trade = next((t for t in self.trades if t.signal_id == signal_id), None)
        if not trade or trade.outcome != TradeOutcome.PENDING:
            return trade

        trade.exit_price = exit_price
        trade.exit_time = datetime.now()
        trade.profit_loss = exit_price - trade.entry_price
        trade.profit_loss_percent = (trade.profit_loss / trade.entry_price) * 100
        trade.notes = reason

        # Determine outcome
        if abs(trade.profit_loss_percent) < 5:
            trade.outcome = TradeOutcome.BREAKEVEN
        elif trade.profit_loss > 0:
            trade.outcome = TradeOutcome.HIT_TARGET
        else:
            trade.outcome = TradeOutcome.HIT_STOP

        logger.info(f"Closed trade: {trade.symbol} at {exit_price:.2f} ({trade.profit_loss_percent:.1f}%) - {reason}")
        self.save_trades()
        return trade

    def get_performance_stats(self, strategy: Optional[str] = None) -> Dict:
        """
        Calculate performance statistics

        Args:
            strategy: Filter by strategy (optional)

        Returns:
            Dictionary of performance metrics
        """
        # Filter trades
        trades = self.trades
        if strategy:
            trades = [t for t in trades if t.strategy == strategy]

        # Only completed trades
        completed = [t for t in trades if t.outcome != TradeOutcome.PENDING]

        if not completed:
            return {
                "total_trades": 0,
                "win_rate": 0.0,
                "avg_profit": 0.0,
                "avg_loss": 0.0,
                "profit_factor": 0.0,
                "sharpe_ratio": 0.0
            }

        # Calculate stats
        winners = [t for t in completed if t.profit_loss and t.profit_loss > 0]
        losers = [t for t in completed if t.profit_loss and t.profit_loss <= 0]

        win_rate = len(winners) / len(completed) * 100 if completed else 0
        avg_profit = sum(t.profit_loss for t in winners) / len(winners) if winners else 0
        avg_loss = sum(abs(t.profit_loss) for t in losers) / len(losers) if losers else 0

        total_profit = sum(t.profit_loss for t in winners)
        total_loss = sum(abs(t.profit_loss) for t in losers)
        profit_factor = total_profit / total_loss if total_loss > 0 else 0

        return {
            "total_trades": len(completed),
            "pending_trades": len([t for t in trades if t.outcome == TradeOutcome.PENDING]),
            "winners": len(winners),
            "losers": len(losers),
            "win_rate": win_rate,
            "avg_profit": avg_profit,
            "avg_loss": avg_loss,
            "avg_profit_percent": sum(t.profit_loss_percent for t in winners) / len(winners) if winners else 0,
            "avg_loss_percent": sum(t.profit_loss_percent for t in losers) / len(losers) if losers else 0,
            "profit_factor": profit_factor,
            "total_pnl": sum(t.profit_loss for t in completed if t.profit_loss),
            "best_trade": max(completed, key=lambda t: t.profit_loss_percent).profit_loss_percent if completed else 0,
            "worst_trade": min(completed, key=lambda t: t.profit_loss_percent).profit_loss_percent if completed else 0
        }

    def get_probability_of_profit(self, strategy: str) -> float:
        """
        Get REAL probability of profit based on historical performance

        Args:
            strategy: Strategy name

        Returns:
            Historical win rate as probability (0-1)
        """
        stats = self.get_performance_stats(strategy)
        return stats["win_rate"] / 100.0

    def get_open_trades(self) -> List[PaperTrade]:
        """Get all open (pending) trades"""
        return [t for t in self.trades if t.outcome == TradeOutcome.PENDING]

    def get_closed_trades(self, limit: int = 50) -> List[PaperTrade]:
        """Get recently closed trades"""
        closed = [t for t in self.trades if t.outcome != TradeOutcome.PENDING]
        closed.sort(key=lambda t: t.exit_time or datetime.min, reverse=True)
        return closed[:limit]
