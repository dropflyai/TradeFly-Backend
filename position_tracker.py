"""
Position Tracker - Monitor Bought Trades & Generate Exit Signals
Track positions you actually bought and get alerts when to sell
"""
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
import json
from enum import Enum

from options_models import OptionContract, SignalAction

logger = logging.getLogger(__name__)


class ExitReason(Enum):
    """Why we're suggesting an exit"""
    TARGET_HIT = "target_hit"           # Hit profit target
    STOP_HIT = "stop_hit"               # Hit stop loss
    TIME_EXIT = "time_exit"             # Held long enough
    EXPIRATION_WARNING = "exp_warning"  # Expires soon
    TRAILING_STOP = "trailing_stop"     # Trailing stop triggered
    BREAKEVEN = "breakeven"             # Move to breakeven


class ExitSignal:
    """Exit signal for a position"""
    def __init__(
        self,
        position_id: str,
        reason: ExitReason,
        urgency: str,  # "high", "medium", "low"
        message: str,
        current_price: float,
        suggested_exit_price: float,
        profit_loss_percent: float
    ):
        self.position_id = position_id
        self.reason = reason
        self.urgency = urgency
        self.message = message
        self.current_price = current_price
        self.suggested_exit_price = suggested_exit_price
        self.profit_loss_percent = profit_loss_percent
        self.timestamp = datetime.now()


@dataclass
class Position:
    """A tracked position (trade you actually bought)"""
    position_id: str
    signal_id: str
    symbol: str
    strategy: str  # "SCALPING" or "SWING"
    action: str    # "BUY_CALL" or "BUY_PUT"

    # Entry details
    entry_price: float
    entry_time: datetime
    contracts_bought: int  # How many contracts (default 1)

    # Exit plan
    target_price: float
    stop_loss: float

    # Contract details
    strike: float
    option_type: str  # "call" or "put"
    expiration: str   # "YYYY-MM-DD"

    # Current status
    status: str = "active"  # "active", "closed"
    current_price: Optional[float] = None
    last_update: Optional[datetime] = None

    # Exit tracking
    exit_price: Optional[float] = None
    exit_time: Optional[datetime] = None
    exit_reason: Optional[str] = None
    profit_loss: Optional[float] = None
    profit_loss_percent: Optional[float] = None

    # Risk management
    highest_price: Optional[float] = None  # For trailing stops
    breakeven_moved: bool = False  # Did we move stop to breakeven?
    partial_exit_taken: bool = False  # Did we take partial profits?

    notes: str = ""


class PositionTracker:
    """
    Track positions you actually bought and generate exit signals

    Features:
    - Mark signals as "bought"
    - Monitor current prices
    - Generate exit signals (target, stop, time-based)
    - Track P/L in real-time
    - Manage trailing stops
    """

    def __init__(self, data_file: str = "positions.json"):
        self.data_file = Path(data_file)
        self.positions: List[Position] = []
        self.load_positions()

    def load_positions(self):
        """Load positions from disk"""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.positions = [
                        Position(
                            **{
                                **pos,
                                'entry_time': datetime.fromisoformat(pos['entry_time']),
                                'last_update': datetime.fromisoformat(pos['last_update']) if pos.get('last_update') else None,
                                'exit_time': datetime.fromisoformat(pos['exit_time']) if pos.get('exit_time') else None
                            }
                        )
                        for pos in data
                    ]
                logger.info(f"✅ Loaded {len(self.positions)} positions from {self.data_file}")
            except Exception as e:
                logger.error(f"Error loading positions: {e}")
                self.positions = []
        else:
            logger.info("No existing positions file found")
            self.positions = []

    def save_positions(self):
        """Save positions to disk"""
        try:
            data = []
            for pos in self.positions:
                pos_dict = asdict(pos)
                # Convert datetime objects to strings
                pos_dict['entry_time'] = pos.entry_time.isoformat()
                if pos.last_update:
                    pos_dict['last_update'] = pos.last_update.isoformat()
                if pos.exit_time:
                    pos_dict['exit_time'] = pos.exit_time.isoformat()
                data.append(pos_dict)

            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)

            logger.debug(f"💾 Saved {len(self.positions)} positions")
        except Exception as e:
            logger.error(f"Error saving positions: {e}")

    def add_position(
        self,
        signal_id: str,
        symbol: str,
        strategy: str,
        action: str,
        entry_price: float,
        target_price: float,
        stop_loss: float,
        strike: float,
        option_type: str,
        expiration: str,
        contracts_bought: int = 1,
        notes: str = ""
    ) -> Position:
        """
        Mark a signal as bought and start tracking it

        Args:
            signal_id: Original signal ID
            symbol: Stock symbol
            strategy: "SCALPING" or "SWING"
            action: "BUY_CALL" or "BUY_PUT"
            entry_price: Price you bought at (per share)
            target_price: Target to sell at
            stop_loss: Stop loss price
            strike: Option strike price
            option_type: "call" or "put"
            expiration: Expiration date "YYYY-MM-DD"
            contracts_bought: Number of contracts (default 1)
            notes: Optional notes

        Returns:
            Position object
        """
        position_id = f"{symbol}_{signal_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        position = Position(
            position_id=position_id,
            signal_id=signal_id,
            symbol=symbol,
            strategy=strategy,
            action=action,
            entry_price=entry_price,
            entry_time=datetime.now(),
            contracts_bought=contracts_bought,
            target_price=target_price,
            stop_loss=stop_loss,
            strike=strike,
            option_type=option_type,
            expiration=expiration,
            status="active",
            current_price=entry_price,
            last_update=datetime.now(),
            highest_price=entry_price,
            notes=notes
        )

        self.positions.append(position)
        self.save_positions()

        logger.info(f"📍 Added position: {symbol} {strike}{option_type.upper()} @ ${entry_price:.2f}")
        return position

    def update_position(self, position_id: str, current_price: float) -> Optional[Position]:
        """
        Update position with current price

        Args:
            position_id: Position to update
            current_price: Current option price

        Returns:
            Updated position or None if not found
        """
        position = self._get_position(position_id)
        if not position:
            return None

        if position.status != "active":
            return position

        position.current_price = current_price
        position.last_update = datetime.now()

        # Track highest price for trailing stops
        if position.highest_price is None or current_price > position.highest_price:
            position.highest_price = current_price

        # Calculate P/L
        position.profit_loss = (current_price - position.entry_price) * 100 * position.contracts_bought
        position.profit_loss_percent = ((current_price - position.entry_price) / position.entry_price) * 100

        self.save_positions()
        return position

    def check_exit_signals(self, position_id: str) -> List[ExitSignal]:
        """
        Check if position should be exited

        Returns:
            List of exit signals (can be multiple reasons)
        """
        position = self._get_position(position_id)
        if not position or position.status != "active":
            return []

        signals = []
        current_price = position.current_price or position.entry_price
        pnl_percent = position.profit_loss_percent or 0.0

        # 1. TARGET HIT
        if current_price >= position.target_price:
            signals.append(ExitSignal(
                position_id=position_id,
                reason=ExitReason.TARGET_HIT,
                urgency="high",
                message=f"🎯 TARGET HIT! {pnl_percent:+.1f}% profit - SELL NOW",
                current_price=current_price,
                suggested_exit_price=current_price,
                profit_loss_percent=pnl_percent
            ))

        # 2. STOP LOSS HIT
        if current_price <= position.stop_loss:
            signals.append(ExitSignal(
                position_id=position_id,
                reason=ExitReason.STOP_HIT,
                urgency="high",
                message=f"🛑 STOP LOSS HIT! {pnl_percent:+.1f}% loss - CUT LOSSES NOW",
                current_price=current_price,
                suggested_exit_price=current_price,
                profit_loss_percent=pnl_percent
            ))

        # 3. TRAILING STOP (if up 15%+, trail by 50%)
        if pnl_percent >= 15 and position.highest_price:
            trailing_stop = position.highest_price * 0.85  # 15% below highest
            if current_price <= trailing_stop:
                signals.append(ExitSignal(
                    position_id=position_id,
                    reason=ExitReason.TRAILING_STOP,
                    urgency="high",
                    message=f"📉 Trailing stop hit! Was up {((position.highest_price - position.entry_price) / position.entry_price * 100):.1f}%, now {pnl_percent:+.1f}% - LOCK PROFITS",
                    current_price=current_price,
                    suggested_exit_price=current_price,
                    profit_loss_percent=pnl_percent
                ))

        # 4. MOVE TO BREAKEVEN (if up 10%+)
        if pnl_percent >= 10 and not position.breakeven_moved:
            signals.append(ExitSignal(
                position_id=position_id,
                reason=ExitReason.BREAKEVEN,
                urgency="medium",
                message=f"✅ Up {pnl_percent:+.1f}%! Consider moving stop to breakeven (${position.entry_price:.2f})",
                current_price=current_price,
                suggested_exit_price=position.entry_price,
                profit_loss_percent=pnl_percent
            ))

        # 5. TIME-BASED EXIT
        time_held = datetime.now() - position.entry_time

        if position.strategy == "SCALPING":
            # Scalping: Exit after 5 minutes if not moving
            if time_held > timedelta(minutes=5):
                if abs(pnl_percent) < 5:  # Less than 5% move either way
                    signals.append(ExitSignal(
                        position_id=position_id,
                        reason=ExitReason.TIME_EXIT,
                        urgency="medium",
                        message=f"⏰ Held {time_held.seconds // 60} min, sideways movement - consider exiting",
                        current_price=current_price,
                        suggested_exit_price=current_price,
                        profit_loss_percent=pnl_percent
                    ))

        elif position.strategy == "SWING":
            # Swing: Exit after 5 days
            if time_held > timedelta(days=5):
                signals.append(ExitSignal(
                    position_id=position_id,
                    reason=ExitReason.TIME_EXIT,
                    urgency="medium",
                    message=f"⏰ Held {time_held.days} days - swing trade time limit reached",
                    current_price=current_price,
                    suggested_exit_price=current_price,
                    profit_loss_percent=pnl_percent
                ))

        # 6. EXPIRATION WARNING
        try:
            exp_date = datetime.strptime(position.expiration, "%Y-%m-%d")
            days_to_exp = (exp_date - datetime.now()).days

            if days_to_exp <= 1:
                signals.append(ExitSignal(
                    position_id=position_id,
                    reason=ExitReason.EXPIRATION_WARNING,
                    urgency="high",
                    message=f"⚠️ EXPIRES IN {days_to_exp} DAY(S)! Heavy theta decay - EXIT SOON",
                    current_price=current_price,
                    suggested_exit_price=current_price,
                    profit_loss_percent=pnl_percent
                ))
            elif days_to_exp <= 3:
                signals.append(ExitSignal(
                    position_id=position_id,
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

    def close_position(
        self,
        position_id: str,
        exit_price: float,
        exit_reason: str = "Manual close"
    ) -> Optional[Position]:
        """
        Close a position (mark as sold)

        Args:
            position_id: Position to close
            exit_price: Price you sold at
            exit_reason: Why you closed it

        Returns:
            Closed position or None if not found
        """
        position = self._get_position(position_id)
        if not position:
            return None

        position.status = "closed"
        position.exit_price = exit_price
        position.exit_time = datetime.now()
        position.exit_reason = exit_reason
        position.profit_loss = (exit_price - position.entry_price) * 100 * position.contracts_bought
        position.profit_loss_percent = ((exit_price - position.entry_price) / position.entry_price) * 100

        self.save_positions()

        logger.info(f"✅ Closed position {position.symbol}: {position.profit_loss_percent:+.1f}% (${position.profit_loss:+.2f})")
        return position

    def get_active_positions(self) -> List[Position]:
        """Get all active positions"""
        return [p for p in self.positions if p.status == "active"]

    def get_closed_positions(self, limit: int = 50) -> List[Position]:
        """Get closed positions (most recent first)"""
        closed = [p for p in self.positions if p.status == "closed"]
        closed.sort(key=lambda p: p.exit_time or p.entry_time, reverse=True)
        return closed[:limit]

    def get_position_by_signal_id(self, signal_id: str) -> Optional[Position]:
        """Get position by original signal ID"""
        for pos in self.positions:
            if pos.signal_id == signal_id and pos.status == "active":
                return pos
        return None

    def _get_position(self, position_id: str) -> Optional[Position]:
        """Get position by ID"""
        for pos in self.positions:
            if pos.position_id == position_id:
                return pos
        return None

    def get_performance_summary(self, strategy: Optional[str] = None) -> Dict:
        """
        Get performance summary for tracked positions

        Args:
            strategy: Filter by strategy ("SCALPING" or "SWING")

        Returns:
            Performance metrics
        """
        positions = self.positions
        if strategy:
            positions = [p for p in positions if p.strategy == strategy]

        closed_positions = [p for p in positions if p.status == "closed" and p.profit_loss is not None]
        active_positions = [p for p in positions if p.status == "active"]

        if not closed_positions:
            return {
                "total_closed": 0,
                "active_positions": len(active_positions),
                "win_rate": 0.0,
                "avg_win": 0.0,
                "avg_loss": 0.0,
                "total_pnl": 0.0,
                "largest_win": 0.0,
                "largest_loss": 0.0
            }

        winners = [p for p in closed_positions if p.profit_loss > 0]
        losers = [p for p in closed_positions if p.profit_loss <= 0]

        return {
            "total_closed": len(closed_positions),
            "active_positions": len(active_positions),
            "winners": len(winners),
            "losers": len(losers),
            "win_rate": (len(winners) / len(closed_positions) * 100) if closed_positions else 0.0,
            "avg_win": (sum(p.profit_loss_percent for p in winners) / len(winners)) if winners else 0.0,
            "avg_loss": (sum(p.profit_loss_percent for p in losers) / len(losers)) if losers else 0.0,
            "total_pnl": sum(p.profit_loss for p in closed_positions),
            "total_pnl_percent": sum(p.profit_loss_percent for p in closed_positions) / len(closed_positions),
            "largest_win": max((p.profit_loss_percent for p in winners), default=0.0),
            "largest_loss": min((p.profit_loss_percent for p in losers), default=0.0),
            "avg_hold_time_minutes": sum(
                ((p.exit_time - p.entry_time).total_seconds() / 60)
                for p in closed_positions if p.exit_time
            ) / len(closed_positions) if closed_positions else 0.0
        }
