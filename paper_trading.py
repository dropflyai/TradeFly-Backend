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

from options_models import OptionsSignal, SignalAction, StrategyType, OptionType

logger = logging.getLogger(__name__)

# Import training data manager for AI learning
try:
    from training_data import training_data_manager, SignalOutcome
    TRAINING_DATA_ENABLED = True
except ImportError:
    logger.warning("Training data module not available - AI learning disabled")
    TRAINING_DATA_ENABLED = False


class TradeOutcome(Enum):
    """Possible trade outcomes"""
    PENDING = "pending"           # Still open
    HIT_TARGET = "hit_target"     # Won - hit profit target
    HIT_STOP = "hit_stop"         # Lost - hit stop loss
    EXPIRED_WORTHLESS = "expired" # Lost - option expired
    CLOSED_MANUAL = "closed"      # Manually closed
    BREAKEVEN = "breakeven"       # Closed near entry


class ExitReason(Enum):
    """Exit signal reasons for paper trades"""
    TARGET_HIT = "target_hit"
    STOP_HIT = "stop_hit"
    TRAILING_STOP = "trailing_stop"
    BREAKEVEN = "breakeven"
    TIME_EXIT = "time_exit"
    EXPIRATION_WARNING = "exp_warning"


@dataclass
class ExitSignal:
    """Exit signal for a paper trade"""
    trade_id: str
    reason: ExitReason
    urgency: str  # "high", "medium", "low"
    message: str
    current_price: float
    suggested_exit_price: float
    profit_loss_percent: float


@dataclass
class PaperTrade:
    """A paper trade tracking entry with exit signal monitoring"""
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

    # Greeks at entry (for training data)
    delta: float = 0.0
    gamma: float = 0.0
    theta: float = 0.0
    vega: float = 0.0

    # Technical indicators at entry (for training data)
    rsi_14: float = 50.0
    macd_histogram: float = 0.0
    iv_rank: float = 50.0
    price_momentum_15m: float = 0.0
    volume_ratio: float = 1.0
    bid_ask_spread_percent: float = 0.0

    # Market context at entry
    overall_market_direction: str = "neutral"  # "up", "down", "sideways"

    # Tracking
    outcome: TradeOutcome = TradeOutcome.PENDING
    exit_price: Optional[float] = None
    exit_time: Optional[datetime] = None
    current_price: Optional[float] = None
    last_update: Optional[datetime] = None

    # Performance metrics
    profit_loss: Optional[float] = None
    profit_loss_percent: Optional[float] = None

    # Original confidence
    original_confidence: float = 0.0

    # Exit signal tracking (like real positions)
    highest_price: Optional[float] = None  # For trailing stops
    breakeven_moved: bool = False
    exit_signals: List[ExitSignal] = None

    # Notes
    notes: str = ""

    def __post_init__(self):
        if self.exit_signals is None:
            self.exit_signals = []


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
            data = []
            for trade in self.trades:
                trade_dict = asdict(trade)

                # Convert datetime objects
                trade_dict['entry_time'] = trade.entry_time.isoformat()
                trade_dict['exit_time'] = trade.exit_time.isoformat() if trade.exit_time else None
                trade_dict['last_update'] = trade.last_update.isoformat() if trade.last_update else None
                trade_dict['outcome'] = trade.outcome.value

                # Convert exit_signals (ExitSignal objects with ExitReason enums)
                if trade.exit_signals:
                    trade_dict['exit_signals'] = [
                        {
                            'trade_id': sig.trade_id,
                            'reason': sig.reason.value,  # Convert enum to string
                            'urgency': sig.urgency,
                            'message': sig.message,
                            'current_price': sig.current_price,
                            'suggested_exit_price': sig.suggested_exit_price,
                            'profit_loss_percent': sig.profit_loss_percent
                        }
                        for sig in trade.exit_signals
                    ]

                data.append(trade_dict)

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
        NOW INCLUDES EXIT SIGNAL MONITORING

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

        # Update current price and tracking
        trade.current_price = current_price
        trade.last_update = current_time

        # Track highest price for trailing stops
        if trade.highest_price is None or current_price > trade.highest_price:
            trade.highest_price = current_price

        # Calculate current P/L
        trade.profit_loss = current_price - trade.entry_price
        trade.profit_loss_percent = (trade.profit_loss / trade.entry_price) * 100

        # Check for exit signals (generate warnings before auto-closing)
        trade.exit_signals = self.check_exit_signals(trade)

        # Auto-close if hit target or stop
        # Check if hit target
        if current_price >= trade.target_price:
            trade.outcome = TradeOutcome.HIT_TARGET
            trade.exit_price = trade.target_price
            trade.exit_time = current_time
            trade.profit_loss = trade.target_price - trade.entry_price
            trade.profit_loss_percent = (trade.profit_loss / trade.entry_price) * 100
            trade.notes = "target_hit"
            logger.info(f"✅ WINNER: {trade.symbol} hit target! +{trade.profit_loss_percent:.1f}%")

            # Record to training data for AI learning
            self._record_to_training_data(trade)

            self.save_trades()
            return trade

        # Check if hit stop
        if current_price <= trade.stop_loss:
            trade.outcome = TradeOutcome.HIT_STOP
            trade.exit_price = trade.stop_loss
            trade.exit_time = current_time
            trade.profit_loss = trade.stop_loss - trade.entry_price
            trade.profit_loss_percent = (trade.profit_loss / trade.entry_price) * 100
            trade.notes = "stop_hit"
            logger.info(f"❌ LOSER: {trade.symbol} hit stop. {trade.profit_loss_percent:.1f}%")

            # Record to training data for AI learning
            self._record_to_training_data(trade)

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
                trade.notes = "Expired"
                logger.info(f"💀 EXPIRED: {trade.symbol} expired worthless. -100%")

                # Record to training data for AI learning
                self._record_to_training_data(trade)

                self.save_trades()
                return trade
        except:
            pass

        self.save_trades()
        return trade

    def check_exit_signals(self, trade: PaperTrade) -> List[ExitSignal]:
        """
        Check if paper trade should be exited (mirrors position_tracker logic)

        Returns:
            List of exit signals (warnings before auto-close)
        """
        if trade.outcome != TradeOutcome.PENDING:
            return []

        signals = []
        current_price = trade.current_price or trade.entry_price
        pnl_percent = trade.profit_loss_percent or 0.0

        # 1. TARGET APPROACHING (within 5%)
        if current_price >= trade.target_price * 0.95 and current_price < trade.target_price:
            signals.append(ExitSignal(
                trade_id=trade.signal_id,
                reason=ExitReason.TARGET_HIT,
                urgency="high",
                message=f"🎯 Near target! {pnl_percent:+.1f}% - Consider taking profits",
                current_price=current_price,
                suggested_exit_price=current_price,
                profit_loss_percent=pnl_percent
            ))

        # 2. STOP APPROACHING (within 10%)
        if current_price <= trade.stop_loss * 1.10 and current_price > trade.stop_loss:
            signals.append(ExitSignal(
                trade_id=trade.signal_id,
                reason=ExitReason.STOP_HIT,
                urgency="high",
                message=f"⚠️ Near stop loss! {pnl_percent:+.1f}% - Watch closely",
                current_price=current_price,
                suggested_exit_price=current_price,
                profit_loss_percent=pnl_percent
            ))

        # 3. TRAILING STOP (if up 15%+, trail by 50%)
        if pnl_percent >= 15 and trade.highest_price:
            trailing_stop = trade.highest_price * 0.85  # 15% below highest
            if current_price <= trailing_stop:
                signals.append(ExitSignal(
                    trade_id=trade.signal_id,
                    reason=ExitReason.TRAILING_STOP,
                    urgency="high",
                    message=f"📉 Trailing stop! Was up {((trade.highest_price - trade.entry_price) / trade.entry_price * 100):.1f}%, now {pnl_percent:+.1f}% - LOCK PROFITS",
                    current_price=current_price,
                    suggested_exit_price=current_price,
                    profit_loss_percent=pnl_percent
                ))

        # 4. BREAKEVEN SUGGESTION (if up 10%+)
        if pnl_percent >= 10 and not trade.breakeven_moved:
            signals.append(ExitSignal(
                trade_id=trade.signal_id,
                reason=ExitReason.BREAKEVEN,
                urgency="medium",
                message=f"✅ Up {pnl_percent:+.1f}%! Consider moving stop to breakeven (${trade.entry_price:.2f})",
                current_price=current_price,
                suggested_exit_price=trade.entry_price,
                profit_loss_percent=pnl_percent
            ))

        # 5. TIME-BASED EXIT
        time_held = datetime.now() - trade.entry_time

        if trade.strategy == "SCALPING":
            # Scalping: Exit after 5 minutes if not moving
            if time_held > timedelta(minutes=5):
                if abs(pnl_percent) < 5:  # Less than 5% move
                    signals.append(ExitSignal(
                        trade_id=trade.signal_id,
                        reason=ExitReason.TIME_EXIT,
                        urgency="medium",
                        message=f"⏰ Held {time_held.seconds // 60} min, sideways - consider exiting",
                        current_price=current_price,
                        suggested_exit_price=current_price,
                        profit_loss_percent=pnl_percent
                    ))

        elif trade.strategy == "SWING":
            # Swing: Exit after 5 days
            if time_held > timedelta(days=5):
                signals.append(ExitSignal(
                    trade_id=trade.signal_id,
                    reason=ExitReason.TIME_EXIT,
                    urgency="medium",
                    message=f"⏰ Held {time_held.days} days - swing time limit reached",
                    current_price=current_price,
                    suggested_exit_price=current_price,
                    profit_loss_percent=pnl_percent
                ))

        # 6. EXPIRATION WARNING
        try:
            exp_date = datetime.strptime(trade.expiration, "%Y-%m-%d")
            days_to_exp = (exp_date - datetime.now()).days

            if days_to_exp <= 1:
                signals.append(ExitSignal(
                    trade_id=trade.signal_id,
                    reason=ExitReason.EXPIRATION_WARNING,
                    urgency="high",
                    message=f"⚠️ EXPIRES IN {days_to_exp} DAY(S)! Heavy theta decay - EXIT SOON",
                    current_price=current_price,
                    suggested_exit_price=current_price,
                    profit_loss_percent=pnl_percent
                ))
            elif days_to_exp <= 3:
                signals.append(ExitSignal(
                    trade_id=trade.signal_id,
                    reason=ExitReason.EXPIRATION_WARNING,
                    urgency="medium",
                    message=f"⏰ Expires in {days_to_exp} days - theta accelerating",
                    current_price=current_price,
                    suggested_exit_price=current_price,
                    profit_loss_percent=pnl_percent
                ))
        except:
            pass

        return signals

    def _record_to_training_data(self, trade: PaperTrade) -> bool:
        """
        Record completed trade to training data for AI learning

        Args:
            trade: Completed PaperTrade with exit info

        Returns:
            True if successfully recorded
        """
        if not TRAINING_DATA_ENABLED:
            return False

        if not trade.exit_time or not trade.exit_price:
            logger.warning(f"Cannot record incomplete trade {trade.signal_id}")
            return False

        try:
            # Calculate days to expiration at entry
            try:
                exp_date = datetime.strptime(trade.expiration, "%Y-%m-%d")
                dte = (exp_date - trade.entry_time).days
            except:
                dte = 7  # Default fallback

            # Calculate hold duration in minutes
            hold_duration_minutes = int((trade.exit_time - trade.entry_time).total_seconds() / 60)

            # Determine outcome
            if trade.outcome == TradeOutcome.HIT_TARGET:
                outcome_str = "win"
                hit_target = True
                hit_stop = False
            elif trade.outcome == TradeOutcome.HIT_STOP:
                outcome_str = "loss"
                hit_target = False
                hit_stop = True
            elif trade.outcome == TradeOutcome.EXPIRED_WORTHLESS:
                outcome_str = "loss"
                hit_target = False
                hit_stop = False
            elif abs(trade.profit_loss_percent) < 5:
                outcome_str = "breakeven"
                hit_target = False
                hit_stop = False
            else:
                outcome_str = "win" if trade.profit_loss > 0 else "loss"
                hit_target = trade.profit_loss > 0
                hit_stop = trade.profit_loss < 0

            # Map exit reason
            exit_reason_map = {
                "target_hit": "target",
                "stop_hit": "stop",
                "trailing_stop": "trailing_stop",
                "Manual close": "manual",
                "Time-based exit": "time",
                "Expired": "expiration"
            }
            exit_reason = exit_reason_map.get(trade.notes, "manual")

            # Get time context
            time_of_day = trade.entry_time.strftime("%H:%M")
            day_of_week = trade.entry_time.weekday()

            # Create SignalOutcome record
            signal_outcome = SignalOutcome(
                signal_id=trade.signal_id,
                timestamp=trade.exit_time,
                symbol=trade.symbol,
                strategy=StrategyType(trade.strategy.upper()),
                confidence=trade.original_confidence,
                action=SignalAction(trade.action.upper()),
                entry_price=trade.entry_price,
                strike=trade.strike,
                dte=dte,
                option_type=OptionType(trade.option_type.lower()),  # lowercase: "call" or "put"
                # Technical indicators
                rsi_14=trade.rsi_14,
                macd_histogram=trade.macd_histogram,
                price_momentum_15m=trade.price_momentum_15m,
                volume_ratio=trade.volume_ratio,
                iv_rank=trade.iv_rank,
                delta=trade.delta,
                gamma=trade.gamma,
                theta=trade.theta,
                bid_ask_spread_percent=trade.bid_ask_spread_percent,
                # Market context
                time_of_day=time_of_day,
                day_of_week=day_of_week,
                overall_market_direction=trade.overall_market_direction,
                # Outcome
                exit_price=trade.exit_price,
                profit_loss_percent=trade.profit_loss_percent,
                hold_duration_minutes=hold_duration_minutes,
                exit_reason=exit_reason,
                outcome=outcome_str,
                hit_target=hit_target,
                hit_stop=hit_stop
            )

            # Record to training data
            success = training_data_manager.record_outcome(signal_outcome)

            if success:
                logger.info(f"📊 Recorded to training data: {trade.symbol} {outcome_str} ({trade.profit_loss_percent:.1f}%)")

            return success

        except Exception as e:
            logger.error(f"Error recording to training data: {e}")
            return False

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

        # Record to training data for AI learning
        self._record_to_training_data(trade)

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
