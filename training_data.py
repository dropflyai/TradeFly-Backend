"""
Training Data Manager - AI Self-Improvement System
Stores signal outcomes for pattern analysis and strategy optimization
"""
import logging
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path
import json
from pydantic import BaseModel, Field
from options_models import StrategyType, SignalAction, OptionType

logger = logging.getLogger(__name__)


class SignalOutcome(BaseModel):
    """Complete signal outcome record for AI training"""

    # Identifiers
    signal_id: str
    timestamp: datetime

    # Signal characteristics (INPUTS for AI learning)
    symbol: str
    strategy: StrategyType
    confidence: float  # What AI originally predicted (0-1)
    action: SignalAction

    # Entry conditions
    entry_price: float
    strike: float
    dte: int  # Days to expiration at entry
    option_type: OptionType

    # Technical state at entry (features for ML)
    rsi_14: float
    macd_histogram: float
    price_momentum_15m: float  # % change in 15min
    volume_ratio: float  # Current volume / 30d avg
    iv_rank: float  # IV percentile
    delta: float
    gamma: float
    theta: float
    bid_ask_spread_percent: float

    # Market context
    time_of_day: str  # "HH:MM"
    day_of_week: int  # 0=Monday, 4=Friday
    overall_market_direction: str  # "up", "down", "sideways"

    # OUTCOME (TARGET for AI - what we're trying to predict)
    exit_price: Optional[float] = None
    profit_loss_percent: Optional[float] = None
    hold_duration_minutes: Optional[int] = None
    exit_reason: Optional[str] = None  # "target", "stop", "trailing_stop", "time", "manual", "expiration"
    outcome: Optional[str] = None  # "win", "loss", "breakeven"
    hit_target: Optional[bool] = None  # Did it reach target?
    hit_stop: Optional[bool] = None  # Did it hit stop loss?

    # Learning metadata
    ai_learned: bool = False
    learning_iteration: int = 0
    notes: Optional[str] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TrainingDataManager:
    """
    Manages training data for AI self-improvement

    Features:
    - Append-only JSONL storage
    - Query by criteria
    - Performance analysis
    - Export for external ML models
    """

    def __init__(self, data_file: str = "training_data.jsonl"):
        self.data_file = Path(data_file)
        self.ensure_file_exists()

    def ensure_file_exists(self):
        """Create data file if it doesn't exist"""
        if not self.data_file.exists():
            self.data_file.touch()
            logger.info(f"Created training data file: {self.data_file}")

    def record_outcome(self, outcome: SignalOutcome) -> bool:
        """
        Record a signal outcome for AI training

        Args:
            outcome: SignalOutcome object with all data

        Returns:
            True if successful
        """
        try:
            # Append to JSONL (one JSON object per line)
            with open(self.data_file, 'a') as f:
                f.write(outcome.json() + '\n')

            logger.info(f"✅ Recorded outcome for AI training: {outcome.signal_id} ({outcome.outcome})")
            return True

        except Exception as e:
            logger.error(f"Error recording outcome: {e}")
            return False

    def get_all_outcomes(self, limit: Optional[int] = None) -> List[SignalOutcome]:
        """
        Load all training data

        Args:
            limit: Max number of outcomes to return (most recent first)

        Returns:
            List of SignalOutcome objects
        """
        outcomes = []

        try:
            with open(self.data_file, 'r') as f:
                for line in f:
                    if line.strip():
                        outcome = SignalOutcome.parse_raw(line)
                        outcomes.append(outcome)

            # Reverse to get most recent first
            outcomes.reverse()

            if limit:
                outcomes = outcomes[:limit]

            logger.debug(f"Loaded {len(outcomes)} outcomes from training data")
            return outcomes

        except Exception as e:
            logger.error(f"Error loading outcomes: {e}")
            return []

    def get_performance_by_criteria(self, **criteria) -> Dict:
        """
        Analyze win rate for specific criteria

        Examples:
            get_performance_by_criteria(strategy='SCALPING')
            get_performance_by_criteria(rsi_14_gt=70, strategy='SCALPING')
            get_performance_by_criteria(confidence_gt=0.85)

        Returns:
            {
                'win_rate': 0.75,
                'sample_size': 20,
                'avg_profit': 15.3,
                'avg_loss': -8.2,
                'avg_hold_time_min': 125
            }
        """
        outcomes = self.get_all_outcomes()

        # Filter by criteria
        filtered = []
        for outcome in outcomes:
            if outcome.outcome is None:  # Skip incomplete
                continue

            matches = True

            # Check each criterion
            for key, value in criteria.items():
                # Handle comparison operators in key (e.g., 'rsi_14_gt')
                if '_gt' in key:
                    field = key.replace('_gt', '')
                    if not (hasattr(outcome, field) and getattr(outcome, field) > value):
                        matches = False
                        break

                elif '_lt' in key:
                    field = key.replace('_lt', '')
                    if not (hasattr(outcome, field) and getattr(outcome, field) < value):
                        matches = False
                        break

                elif '_gte' in key:
                    field = key.replace('_gte', '')
                    if not (hasattr(outcome, field) and getattr(outcome, field) >= value):
                        matches = False
                        break

                elif '_lte' in key:
                    field = key.replace('_lte', '')
                    if not (hasattr(outcome, field) and getattr(outcome, field) <= value):
                        matches = False
                        break

                else:
                    # Exact match
                    if not (hasattr(outcome, key) and str(getattr(outcome, key)) == str(value)):
                        matches = False
                        break

            if matches:
                filtered.append(outcome)

        # Calculate statistics
        if not filtered:
            return {
                'win_rate': 0.0,
                'sample_size': 0,
                'avg_profit': 0.0,
                'avg_loss': 0.0,
                'avg_hold_time_min': 0.0
            }

        wins = [o for o in filtered if o.outcome == 'win']
        losses = [o for o in filtered if o.outcome == 'loss']

        return {
            'win_rate': len(wins) / len(filtered) if filtered else 0.0,
            'sample_size': len(filtered),
            'wins': len(wins),
            'losses': len(losses),
            'avg_profit': sum(o.profit_loss_percent for o in wins) / len(wins) if wins else 0.0,
            'avg_loss': sum(o.profit_loss_percent for o in losses) / len(losses) if losses else 0.0,
            'avg_hold_time_min': sum(o.hold_duration_minutes for o in filtered if o.hold_duration_minutes) / len(filtered) if filtered else 0.0,
            'total_trades': len(filtered)
        }

    def get_best_performing_patterns(self, min_sample_size: int = 10) -> List[Dict]:
        """
        Identify winning patterns in the data

        Returns:
            List of patterns with high win rates
        """
        patterns = []

        # Analyze by strategy
        for strategy in [StrategyType.SCALPING, StrategyType.SWING, StrategyType.MOMENTUM]:
            stats = self.get_performance_by_criteria(strategy=strategy.value)
            if stats['sample_size'] >= min_sample_size:
                patterns.append({
                    'pattern': f'Strategy: {strategy.value}',
                    'win_rate': stats['win_rate'],
                    'sample_size': stats['sample_size'],
                    'avg_profit': stats['avg_profit']
                })

        # Analyze high confidence signals
        stats = self.get_performance_by_criteria(confidence_gte=0.85)
        if stats['sample_size'] >= min_sample_size:
            patterns.append({
                'pattern': 'High confidence (≥85%)',
                'win_rate': stats['win_rate'],
                'sample_size': stats['sample_size'],
                'avg_profit': stats['avg_profit']
            })

        # Analyze by time of day (market open hour)
        morning_stats = self.get_performance_by_criteria_custom(
            lambda o: o.time_of_day and o.time_of_day.startswith('09:')
        )
        if morning_stats['sample_size'] >= min_sample_size:
            patterns.append({
                'pattern': 'Morning trades (9am hour)',
                'win_rate': morning_stats['win_rate'],
                'sample_size': morning_stats['sample_size'],
                'avg_profit': morning_stats['avg_profit']
            })

        # Sort by win rate
        patterns.sort(key=lambda x: x['win_rate'], reverse=True)

        return patterns

    def get_performance_by_criteria_custom(self, filter_func) -> Dict:
        """Custom filter function for complex queries"""
        outcomes = self.get_all_outcomes()
        filtered = [o for o in outcomes if o.outcome and filter_func(o)]

        if not filtered:
            return {'win_rate': 0.0, 'sample_size': 0, 'avg_profit': 0.0}

        wins = [o for o in filtered if o.outcome == 'win']

        return {
            'win_rate': len(wins) / len(filtered),
            'sample_size': len(filtered),
            'avg_profit': sum(o.profit_loss_percent for o in wins) / len(wins) if wins else 0.0
        }

    def export_for_ml(self, output_file: str = "training_export.json") -> bool:
        """
        Export training data in format suitable for ML models

        Returns:
            True if successful
        """
        try:
            outcomes = self.get_all_outcomes()

            # Convert to ML-friendly format
            ml_data = []
            for outcome in outcomes:
                if outcome.outcome:  # Only export completed trades
                    ml_data.append({
                        # Features (inputs)
                        'features': {
                            'rsi_14': outcome.rsi_14,
                            'macd_histogram': outcome.macd_histogram,
                            'price_momentum_15m': outcome.price_momentum_15m,
                            'volume_ratio': outcome.volume_ratio,
                            'iv_rank': outcome.iv_rank,
                            'delta': outcome.delta,
                            'gamma': outcome.gamma,
                            'theta': outcome.theta,
                            'spread_percent': outcome.bid_ask_spread_percent,
                            'dte': outcome.dte,
                            'strategy': outcome.strategy.value,
                            'confidence': outcome.confidence
                        },
                        # Target (what we're predicting)
                        'target': {
                            'outcome': outcome.outcome,
                            'profit_loss_percent': outcome.profit_loss_percent,
                            'hit_target': outcome.hit_target,
                            'hit_stop': outcome.hit_stop
                        }
                    })

            with open(output_file, 'w') as f:
                json.dump(ml_data, f, indent=2)

            logger.info(f"✅ Exported {len(ml_data)} records for ML training: {output_file}")
            return True

        except Exception as e:
            logger.error(f"Error exporting ML data: {e}")
            return False

    def get_stats_summary(self) -> Dict:
        """Get overall training data statistics"""
        outcomes = self.get_all_outcomes()
        completed = [o for o in outcomes if o.outcome]

        if not completed:
            return {
                'total_outcomes': len(outcomes),
                'completed': 0,
                'win_rate': 0.0,
                'strategies': {}
            }

        wins = [o for o in completed if o.outcome == 'win']

        # Stats by strategy
        strategy_stats = {}
        for strategy in [StrategyType.SCALPING, StrategyType.SWING, StrategyType.MOMENTUM, StrategyType.VOLUME_SPIKE]:
            stats = self.get_performance_by_criteria(strategy=strategy.value)
            if stats['sample_size'] > 0:
                strategy_stats[strategy.value] = stats

        return {
            'total_outcomes': len(outcomes),
            'completed': len(completed),
            'pending': len(outcomes) - len(completed),
            'win_rate': len(wins) / len(completed) if completed else 0.0,
            'total_wins': len(wins),
            'total_losses': len([o for o in completed if o.outcome == 'loss']),
            'strategies': strategy_stats
        }


# Global instance
training_data_manager = TrainingDataManager()
