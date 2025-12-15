"""
Enhanced Paper Trading System with Learning and Analysis
Comprehensive tracking, detailed analysis, and AI learning from every trade

Features:
- One-click add signals to paper tracker
- Detailed trade analysis (what went right/wrong)
- Pattern learning (which setups work best)
- Performance insights (win rate by strategy, time, conditions)
- Educational explanations for every trade outcome
"""
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict, field
from enum import Enum
import numpy as np

from options_models import OptionsSignal, SignalAction, StrategyType
from paper_trading import PaperTrade, TradeOutcome, PaperTradingEngine

logger = logging.getLogger(__name__)


@dataclass
class TradeAnalysis:
    """Comprehensive analysis of a completed trade"""
    # Performance
    win: bool
    profit_loss_percent: float
    profit_loss_dollars: float
    hold_time_hours: float

    # What worked
    strengths: List[str] = field(default_factory=list)

    # What didn't work
    weaknesses: List[str] = field(default_factory=list)

    # Key learnings
    lessons: List[str] = field(default_factory=list)

    # Market conditions during trade
    market_conditions: Dict[str, any] = field(default_factory=dict)

    # Pattern analysis
    entry_pattern: Optional[str] = None
    exit_pattern: Optional[str] = None

    # Greeks behavior
    greeks_performance: Dict[str, str] = field(default_factory=dict)

    # Execution quality
    entry_quality: str = "unknown"  # "excellent", "good", "poor"
    exit_quality: str = "unknown"

    # What could have been done better
    improvements: List[str] = field(default_factory=list)

    # Educational summary
    education_summary: str = ""

    def to_dict(self) -> Dict:
        """Convert to dictionary for storage"""
        return asdict(self)


@dataclass
class PerformanceInsights:
    """Performance insights across all trades"""
    # Overall stats
    total_trades: int
    win_rate: float
    avg_profit_percent: float
    avg_loss_percent: float
    profit_factor: float  # Gross profit / gross loss

    # By strategy
    best_strategy: str
    worst_strategy: str
    strategy_performance: Dict[str, Dict] = field(default_factory=dict)

    # By time
    best_hour: int  # Hour of day (0-23)
    worst_hour: int
    hour_performance: Dict[int, Dict] = field(default_factory=dict)

    # By market condition
    best_in_uptrend: bool
    best_in_downtrend: bool
    best_in_sideways: bool

    # Pattern insights
    most_reliable_entry_patterns: List[str] = field(default_factory=list)
    most_reliable_exit_patterns: List[str] = field(default_factory=list)

    # Greeks insights
    optimal_delta_range: Tuple[float, float] = (0.0, 0.0)
    optimal_iv_rank: float = 0.0

    # Key learnings
    top_lessons: List[str] = field(default_factory=list)

    # What to do more of
    winning_characteristics: List[str] = field(default_factory=list)

    # What to avoid
    losing_characteristics: List[str] = field(default_factory=list)


class EnhancedPaperTradingEngine(PaperTradingEngine):
    """
    Enhanced paper trading with comprehensive learning and analysis

    Features:
    - Detailed trade analysis
    - Pattern recognition and learning
    - Performance insights
    - Educational explanations
    - AI training data generation
    """

    def __init__(self, data_file: str = "paper_trades.json", analysis_file: str = "trade_analyses.json"):
        super().__init__(data_file)
        self.analysis_file = Path(analysis_file)
        self.trade_analyses: Dict[str, TradeAnalysis] = {}
        self.load_analyses()

    def load_analyses(self):
        """Load trade analyses from disk"""
        if self.analysis_file.exists():
            try:
                with open(self.analysis_file, 'r') as f:
                    data = json.load(f)
                    self.trade_analyses = {
                        k: TradeAnalysis(**v) for k, v in data.items()
                    }
                logger.info(f"Loaded {len(self.trade_analyses)} trade analyses")
            except Exception as e:
                logger.error(f"Error loading trade analyses: {e}")
                self.trade_analyses = {}

    def save_analyses(self):
        """Save trade analyses to disk"""
        try:
            data = {k: v.to_dict() for k, v in self.trade_analyses.items()}
            with open(self.analysis_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Saved {len(self.trade_analyses)} trade analyses")
        except Exception as e:
            logger.error(f"Error saving trade analyses: {e}")

    def add_signal_with_analysis(self, signal: OptionsSignal, market_context: Optional[Dict] = None) -> Dict:
        """
        One-click add signal to paper tracker with full context

        Args:
            signal: OptionsSignal to track
            market_context: Optional dict with market conditions at entry

        Returns:
            Dict with trade info and confirmation
        """
        # Add to paper trading
        trade = self.add_signal(signal)

        # Enrich with market context
        if market_context:
            trade.overall_market_direction = market_context.get('trend', 'neutral')

        # Store entry analysis
        entry_analysis = self._analyze_entry_setup(signal, market_context)

        # Create response with full context
        response = {
            "success": True,
            "trade_id": trade.signal_id,
            "message": f"✅ Added to paper tracker: {signal.contract.symbol} ${signal.contract.strike} {signal.contract.option_type}",
            "entry_details": {
                "symbol": trade.symbol,
                "strategy": trade.strategy,
                "entry_price": trade.entry_price,
                "target_price": trade.target_price,
                "stop_loss": trade.stop_loss,
                "risk_reward_ratio": (trade.target_price - trade.entry_price) / (trade.entry_price - trade.stop_loss) if trade.entry_price > trade.stop_loss else 0,
                "confidence": trade.original_confidence
            },
            "entry_analysis": entry_analysis,
            "tracking": {
                "monitor_url": f"/api/paper-trades/{trade.signal_id}",
                "real_time_updates": True
            }
        }

        return response

    def _analyze_entry_setup(self, signal: OptionsSignal, market_context: Optional[Dict]) -> Dict:
        """Analyze the entry setup quality"""
        strengths = []
        weaknesses = []
        quality_score = 0.0

        # Check confidence
        if signal.confidence >= 0.8:
            strengths.append("High confidence signal (≥80%)")
            quality_score += 0.2
        elif signal.confidence < 0.6:
            weaknesses.append("Low confidence signal (<60%)")
            quality_score -= 0.1

        # Check risk/reward
        rr_ratio = (signal.target_price - signal.entry_price) / (signal.entry_price - signal.stop_loss) if signal.entry_price > signal.stop_loss else 0
        if rr_ratio >= 2.0:
            strengths.append(f"Excellent R:R ratio ({rr_ratio:.1f}:1)")
            quality_score += 0.2
        elif rr_ratio < 1.5:
            weaknesses.append(f"Poor R:R ratio ({rr_ratio:.1f}:1)")
            quality_score -= 0.1

        # Check market alignment
        if market_context:
            trend = market_context.get('trend', 'neutral')
            if signal.action == SignalAction.BUY_CALL and trend == 'uptrend':
                strengths.append("Aligned with uptrend (calls in uptrend)")
                quality_score += 0.1
            elif signal.action == SignalAction.BUY_PUT and trend == 'downtrend':
                strengths.append("Aligned with downtrend (puts in downtrend)")
                quality_score += 0.1
            elif signal.action == SignalAction.BUY_CALL and trend == 'downtrend':
                weaknesses.append("Against trend (calls in downtrend)")
                quality_score -= 0.2

        # Determine entry quality
        if quality_score >= 0.4:
            entry_quality = "excellent"
        elif quality_score >= 0.2:
            entry_quality = "good"
        elif quality_score >= 0:
            entry_quality = "fair"
        else:
            entry_quality = "poor"

        return {
            "quality": entry_quality,
            "quality_score": quality_score,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "recommendation": self._get_entry_recommendation(entry_quality, strengths, weaknesses)
        }

    def _get_entry_recommendation(self, quality: str, strengths: List[str], weaknesses: List[str]) -> str:
        """Generate entry recommendation"""
        if quality == "excellent":
            return "🟢 EXCELLENT SETUP - All factors aligned. High probability trade."
        elif quality == "good":
            return "🟡 GOOD SETUP - Most factors positive. Acceptable risk."
        elif quality == "fair":
            return "🟠 FAIR SETUP - Mixed signals. Consider waiting for better setup."
        else:
            return "🔴 POOR SETUP - Multiple red flags. Skip or reduce position size."

    def close_trade_with_analysis(
        self,
        signal_id: str,
        exit_price: float,
        exit_reason: str,
        market_context: Optional[Dict] = None
    ) -> Dict:
        """
        Close a paper trade and generate comprehensive analysis

        Args:
            signal_id: Trade ID
            exit_price: Exit price
            exit_reason: Why trade was closed
            market_context: Market conditions at exit

        Returns:
            Dict with trade results and learning insights
        """
        trade = next((t for t in self.trades if t.signal_id == signal_id), None)
        if not trade:
            return {"success": False, "error": "Trade not found"}

        # Update trade
        trade.exit_price = exit_price
        trade.exit_time = datetime.now()
        trade.profit_loss = exit_price - trade.entry_price
        trade.profit_loss_percent = (trade.profit_loss / trade.entry_price) * 100

        # Determine outcome
        if abs(trade.profit_loss_percent) < 2:
            trade.outcome = TradeOutcome.BREAKEVEN
        elif trade.profit_loss > 0:
            trade.outcome = TradeOutcome.HIT_TARGET if exit_reason == "target" else TradeOutcome.CLOSED_MANUAL
        else:
            trade.outcome = TradeOutcome.HIT_STOP if exit_reason == "stop" else TradeOutcome.CLOSED_MANUAL

        # Generate comprehensive analysis
        analysis = self._generate_trade_analysis(trade, exit_reason, market_context)
        self.trade_analyses[signal_id] = analysis

        # Save updates
        self.save_trades()
        self.save_analyses()

        # Create detailed response
        response = {
            "success": True,
            "trade_id": signal_id,
            "outcome": trade.outcome.value,
            "performance": {
                "profit_loss_percent": trade.profit_loss_percent,
                "profit_loss_dollars": trade.profit_loss,
                "hold_time_hours": analysis.hold_time_hours,
                "win": analysis.win
            },
            "analysis": {
                "strengths": analysis.strengths,
                "weaknesses": analysis.weaknesses,
                "lessons": analysis.lessons,
                "improvements": analysis.improvements,
                "entry_quality": analysis.entry_quality,
                "exit_quality": analysis.exit_quality
            },
            "education": {
                "summary": analysis.education_summary,
                "what_worked": analysis.strengths[:3],  # Top 3
                "what_didnt": analysis.weaknesses[:3],
                "key_learning": analysis.lessons[0] if analysis.lessons else "Review trade details"
            },
            "market_context": analysis.market_conditions
        }

        logger.info(f"📊 Trade closed: {trade.symbol} | P/L: {trade.profit_loss_percent:.2f}% | Outcome: {trade.outcome.value}")

        return response

    def _generate_trade_analysis(
        self,
        trade: PaperTrade,
        exit_reason: str,
        market_context: Optional[Dict]
    ) -> TradeAnalysis:
        """Generate comprehensive trade analysis"""
        # Calculate basics
        win = trade.profit_loss_percent > 0
        hold_time = (trade.exit_time - trade.entry_time).total_seconds() / 3600  # hours

        analysis = TradeAnalysis(
            win=win,
            profit_loss_percent=trade.profit_loss_percent,
            profit_loss_dollars=trade.profit_loss,
            hold_time_hours=hold_time
        )

        # Analyze what worked
        if win:
            analysis.strengths.append(f"Profitable trade (+{trade.profit_loss_percent:.1f}%)")

            if exit_reason == "target":
                analysis.strengths.append("Hit profit target as planned")
                analysis.exit_quality = "excellent"
            elif hold_time < 4:
                analysis.strengths.append("Quick profit (momentum trade)")
            elif trade.profit_loss_percent > 50:
                analysis.strengths.append("Large gain (>50%) - excellent entry timing")

            if trade.original_confidence >= 0.8:
                analysis.strengths.append("High confidence signal validated")

        else:
            # Analyze what went wrong
            analysis.weaknesses.append(f"Losing trade ({trade.profit_loss_percent:.1f}%)")

            if exit_reason == "stop":
                analysis.weaknesses.append("Hit stop loss - trade invalidated")
                analysis.exit_quality = "good"  # Followed rules
            else:
                analysis.weaknesses.append("Manual exit - may have exited too early/late")
                analysis.exit_quality = "fair"

            if hold_time < 0.5:
                analysis.weaknesses.append("Stopped out quickly - entry timing was poor")
            elif hold_time > 24:
                analysis.weaknesses.append("Held too long - should have exited sooner")

            if trade.original_confidence < 0.6:
                analysis.weaknesses.append("Low confidence signal - should have skipped")

        # Market conditions analysis
        if market_context:
            analysis.market_conditions = market_context

            trend = market_context.get('trend', 'neutral')
            if trade.action == "buy_call" and trend == "uptrend" and win:
                analysis.lessons.append("📈 Calls work best in confirmed uptrends")
            elif trade.action == "buy_put" and trend == "downtrend" and win:
                analysis.lessons.append("📉 Puts work best in confirmed downtrends")
            elif trade.action == "buy_call" and trend == "downtrend" and not win:
                analysis.lessons.append("⚠️ Avoid buying calls against the trend")

        # Strategy-specific lessons
        if trade.strategy == "scalping":
            if hold_time > 2 and win:
                analysis.lessons.append("🎯 Scalp held longer than planned but still profitable - consider taking profits at target")
            elif hold_time > 2 and not win:
                analysis.lessons.append("⏰ Scalp held too long - stick to quick exits in scalping")

        elif trade.strategy == "momentum":
            if win and trade.profit_loss_percent > 30:
                analysis.lessons.append("🚀 Momentum trade hit big - these work when volume confirms")
            elif not win and hold_time < 1:
                analysis.lessons.append("⚡ Momentum faded quickly - need stronger initial volume confirmation")

        elif trade.strategy == "swing":
            if win and hold_time > 24:
                analysis.lessons.append("📊 Swing trade given time to develop - patience pays off")
            elif not win and hold_time < 12:
                analysis.lessons.append("⏳ Swing trade not given enough time - avoid early exits")

        # Generate improvements
        if not win:
            if trade.original_confidence < 0.7:
                analysis.improvements.append("Only take trades with ≥70% confidence")
            if exit_reason != "stop":
                analysis.improvements.append("Honor stop losses - cut losses quickly")
            analysis.improvements.append("Review entry checklist before next trade")

        if win but trade.profit_loss_percent < 15:
            analysis.improvements.append("Consider scaling position size on high-confidence setups")

        # Entry quality (based on original setup)
        if trade.original_confidence >= 0.8:
            analysis.entry_quality = "excellent"
        elif trade.original_confidence >= 0.7:
            analysis.entry_quality = "good"
        else:
            analysis.entry_quality = "fair"

        # Educational summary
        analysis.education_summary = self._generate_education_summary(trade, analysis, win)

        return analysis

    def _generate_education_summary(self, trade: PaperTrade, analysis: TradeAnalysis, win: bool) -> str:
        """Generate educational summary of the trade"""
        if win:
            summary = f"✅ **Winning Trade** ({trade.profit_loss_percent:+.1f}%)\n\n"
            summary += f"**What Worked:**\n"
            for strength in analysis.strengths[:3]:
                summary += f"• {strength}\n"

            summary += f"\n**Key Takeaway:** "
            if analysis.lessons:
                summary += analysis.lessons[0]
            else:
                summary += f"This {trade.strategy} setup was successful. Repeat similar setups."

            summary += f"\n\n**Strategy:** {trade.strategy.upper()} strategy executed well"
            summary += f"\n**Hold Time:** {analysis.hold_time_hours:.1f} hours"

        else:
            summary = f"❌ **Losing Trade** ({trade.profit_loss_percent:+.1f}%)\n\n"
            summary += f"**What Went Wrong:**\n"
            for weakness in analysis.weaknesses[:3]:
                summary += f"• {weakness}\n"

            summary += f"\n**Lesson Learned:** "
            if analysis.lessons:
                summary += analysis.lessons[0]
            else:
                summary += "Not every trade wins. Follow your system and rules."

            summary += f"\n\n**Improvements for Next Time:**\n"
            for improvement in analysis.improvements[:2]:
                summary += f"• {improvement}\n"

        return summary

    def get_performance_insights(self) -> PerformanceInsights:
        """
        Generate comprehensive performance insights across all trades

        Returns:
            PerformanceInsights with detailed analysis
        """
        if not self.trades:
            return self._empty_insights()

        closed_trades = [t for t in self.trades if t.outcome != TradeOutcome.PENDING]
        if not closed_trades:
            return self._empty_insights()

        # Calculate overall stats
        winning_trades = [t for t in closed_trades if t.profit_loss_percent > 0]
        losing_trades = [t for t in closed_trades if t.profit_loss_percent < 0]

        win_rate = len(winning_trades) / len(closed_trades) if closed_trades else 0

        avg_profit = np.mean([t.profit_loss_percent for t in winning_trades]) if winning_trades else 0
        avg_loss = abs(np.mean([t.profit_loss_percent for t in losing_trades])) if losing_trades else 0

        gross_profit = sum(t.profit_loss_percent for t in winning_trades) if winning_trades else 0
        gross_loss = abs(sum(t.profit_loss_percent for t in losing_trades)) if losing_trades else 0
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')

        # By strategy
        strategy_performance = self._analyze_by_strategy(closed_trades)
        best_strategy = max(strategy_performance.items(), key=lambda x: x[1]['win_rate'])[0] if strategy_performance else "none"
        worst_strategy = min(strategy_performance.items(), key=lambda x: x[1]['win_rate'])[0] if strategy_performance else "none"

        # By hour
        hour_performance = self._analyze_by_hour(closed_trades)
        best_hour = max(hour_performance.items(), key=lambda x: x[1]['win_rate'])[0] if hour_performance else 9
        worst_hour = min(hour_performance.items(), key=lambda x: x[1]['win_rate'])[0] if hour_performance else 15

        # Generate insights
        insights = PerformanceInsights(
            total_trades=len(closed_trades),
            win_rate=win_rate,
            avg_profit_percent=avg_profit,
            avg_loss_percent=avg_loss,
            profit_factor=profit_factor,
            best_strategy=best_strategy,
            worst_strategy=worst_strategy,
            strategy_performance=strategy_performance,
            best_hour=best_hour,
            worst_hour=worst_hour,
            hour_performance=hour_performance,
            best_in_uptrend=True,  # TODO: Implement
            best_in_downtrend=False,
            best_in_sideways=False
        )

        # Extract top lessons from analyses
        all_lessons = []
        for analysis in self.trade_analyses.values():
            all_lessons.extend(analysis.lessons)
        # Count lesson frequency
        lesson_counts = {}
        for lesson in all_lessons:
            lesson_counts[lesson] = lesson_counts.get(lesson, 0) + 1
        # Top 5 lessons
        insights.top_lessons = sorted(lesson_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        insights.top_lessons = [lesson for lesson, _ in insights.top_lessons]

        # Winning characteristics
        winning_analyses = [self.trade_analyses[t.signal_id] for t in winning_trades if t.signal_id in self.trade_analyses]
        if winning_analyses:
            all_strengths = []
            for a in winning_analyses:
                all_strengths.extend(a.strengths)
            strength_counts = {}
            for strength in all_strengths:
                strength_counts[strength] = strength_counts.get(strength, 0) + 1
            insights.winning_characteristics = sorted(strength_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            insights.winning_characteristics = [char for char, _ in insights.winning_characteristics]

        # Losing characteristics
        losing_analyses = [self.trade_analyses[t.signal_id] for t in losing_trades if t.signal_id in self.trade_analyses]
        if losing_analyses:
            all_weaknesses = []
            for a in losing_analyses:
                all_weaknesses.extend(a.weaknesses)
            weakness_counts = {}
            for weakness in all_weaknesses:
                weakness_counts[weakness] = weakness_counts.get(weakness, 0) + 1
            insights.losing_characteristics = sorted(weakness_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            insights.losing_characteristics = [char for char, _ in insights.losing_characteristics]

        return insights

    def _analyze_by_strategy(self, trades: List[PaperTrade]) -> Dict[str, Dict]:
        """Analyze performance by strategy"""
        strategy_stats = {}

        for trade in trades:
            if trade.strategy not in strategy_stats:
                strategy_stats[trade.strategy] = {
                    "total": 0,
                    "wins": 0,
                    "losses": 0,
                    "total_pnl": 0.0
                }

            stats = strategy_stats[trade.strategy]
            stats["total"] += 1
            stats["total_pnl"] += trade.profit_loss_percent

            if trade.profit_loss_percent > 0:
                stats["wins"] += 1
            else:
                stats["losses"] += 1

        # Calculate win rates
        for strategy, stats in strategy_stats.items():
            stats["win_rate"] = stats["wins"] / stats["total"] if stats["total"] > 0 else 0
            stats["avg_pnl"] = stats["total_pnl"] / stats["total"] if stats["total"] > 0 else 0

        return strategy_stats

    def _analyze_by_hour(self, trades: List[PaperTrade]) -> Dict[int, Dict]:
        """Analyze performance by hour of day"""
        hour_stats = {}

        for trade in trades:
            hour = trade.entry_time.hour

            if hour not in hour_stats:
                hour_stats[hour] = {
                    "total": 0,
                    "wins": 0,
                    "losses": 0,
                    "total_pnl": 0.0
                }

            stats = hour_stats[hour]
            stats["total"] += 1
            stats["total_pnl"] += trade.profit_loss_percent

            if trade.profit_loss_percent > 0:
                stats["wins"] += 1
            else:
                stats["losses"] += 1

        # Calculate win rates
        for hour, stats in hour_stats.items():
            stats["win_rate"] = stats["wins"] / stats["total"] if stats["total"] > 0 else 0
            stats["avg_pnl"] = stats["total_pnl"] / stats["total"] if stats["total"] > 0 else 0

        return hour_stats

    def _empty_insights(self) -> PerformanceInsights:
        """Return empty insights when no trades"""
        return PerformanceInsights(
            total_trades=0,
            win_rate=0.0,
            avg_profit_percent=0.0,
            avg_loss_percent=0.0,
            profit_factor=0.0,
            best_strategy="none",
            worst_strategy="none",
            best_hour=9,
            worst_hour=15,
            best_in_uptrend=False,
            best_in_downtrend=False,
            best_in_sideways=False
        )

    def get_learning_report(self) -> Dict:
        """
        Generate a comprehensive learning report

        Returns:
            Dict with insights, lessons, and recommendations
        """
        insights = self.get_performance_insights()

        report = {
            "overall_performance": {
                "total_trades": insights.total_trades,
                "win_rate": f"{insights.win_rate * 100:.1f}%",
                "profit_factor": f"{insights.profit_factor:.2f}",
                "avg_win": f"+{insights.avg_profit_percent:.1f}%",
                "avg_loss": f"-{insights.avg_loss_percent:.1f}%"
            },
            "strategy_insights": {
                "best_performing": insights.best_strategy,
                "worst_performing": insights.worst_strategy,
                "details": insights.strategy_performance
            },
            "timing_insights": {
                "best_hour": f"{insights.best_hour}:00",
                "worst_hour": f"{insights.worst_hour}:00",
                "recommendation": f"Focus trading between {insights.best_hour-1}:00-{insights.best_hour+2}:00"
            },
            "key_learnings": {
                "top_lessons": insights.top_lessons,
                "do_more_of": insights.winning_characteristics[:3],
                "avoid": insights.losing_characteristics[:3]
            },
            "recommendations": self._generate_recommendations(insights)
        }

        return report

    def _generate_recommendations(self, insights: PerformanceInsights) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        # Win rate recommendations
        if insights.win_rate < 0.5:
            recommendations.append("🚨 Win rate below 50% - Focus on higher confidence setups only (≥70%)")
        elif insights.win_rate >= 0.7:
            recommendations.append("✅ Strong win rate - Current strategy is working, stay consistent")

        # Profit factor recommendations
        if insights.profit_factor < 1.5:
            recommendations.append("📊 Profit factor needs improvement - Let winners run longer, cut losses faster")
        elif insights.profit_factor >= 2.0:
            recommendations.append("🎯 Excellent profit factor - Your risk/reward management is working")

        # Strategy recommendations
        if insights.strategy_performance:
            best_strategy = insights.best_strategy
            best_wr = insights.strategy_performance[best_strategy]["win_rate"]
            if best_wr >= 0.7:
                recommendations.append(f"💡 {best_strategy} strategy has {best_wr*100:.0f}% win rate - Increase allocation")

            worst_strategy = insights.worst_strategy
            worst_wr = insights.strategy_performance[worst_strategy]["win_rate"]
            if worst_wr < 0.4:
                recommendations.append(f"⚠️ {worst_strategy} strategy has {worst_wr*100:.0f}% win rate - Review or pause")

        # Add general recommendations
        if insights.total_trades < 20:
            recommendations.append("📚 Limited sample size - Continue paper trading to gather more data")

        return recommendations
