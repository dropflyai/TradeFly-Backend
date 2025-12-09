"""
Backtesting Engine - Test Strategies on Historical Data
Find out which setups actually work BEFORE using real money
"""
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import numpy as np
import yfinance as yf

from options_models import OptionContract, SignalAction
from paper_trading import PaperTrade, TradeOutcome

logger = logging.getLogger(__name__)


class BacktestResult:
    """Results from a backtest run"""
    def __init__(self):
        self.trades: List[PaperTrade] = []
        self.total_trades = 0
        self.winners = 0
        self.losers = 0
        self.win_rate = 0.0
        self.avg_win = 0.0
        self.avg_loss = 0.0
        self.profit_factor = 0.0
        self.total_pnl = 0.0
        self.best_trade = 0.0
        self.worst_trade = 0.0
        self.avg_holding_period = 0.0


class BacktestEngine:
    """
    Backtest trading strategies on historical data
    Learn which signals actually work
    """

    def __init__(self):
        self.results = {}

    def simulate_option_price_movement(
        self,
        stock_move_percent: float,
        delta: float,
        initial_option_price: float,
        days_elapsed: int = 0
    ) -> float:
        """
        Simulate how option price changes with stock movement

        Simple model:
        - Option moves delta * stock_move
        - Theta decay: ~10-15% per week for near-term options

        Args:
            stock_move_percent: How much stock moved (0.05 = 5%)
            delta: Option delta
            initial_option_price: Starting option price
            days_elapsed: Days since entry (for theta decay)

        Returns:
            Estimated new option price
        """
        # Delta effect
        option_move = stock_move_percent * abs(delta)

        # Theta decay (simplified)
        theta_decay_per_day = 0.02  # ~2% per day for short-term options
        total_theta_decay = theta_decay_per_day * days_elapsed

        # New price
        new_price = initial_option_price * (1 + option_move - total_theta_decay)

        return max(0.01, new_price)  # Can't go below 1 cent

    def backtest_strategy_on_stock(
        self,
        symbol: str,
        strategy_name: str,
        lookback_days: int = 30,
        option_dte: int = 7,
        delta_target: float = 0.50
    ) -> BacktestResult:
        """
        Backtest a strategy on historical stock data

        Args:
            symbol: Stock symbol
            strategy_name: Strategy to test (SCALPING, MOMENTUM, etc.)
            lookback_days: How many days of history to test
            option_dte: Days to expiration for simulated options
            delta_target: Target delta for options

        Returns:
            BacktestResult with performance metrics
        """
        logger.info(f"Backtesting {strategy_name} on {symbol} ({lookback_days} days)")

        result = BacktestResult()

        try:
            # Get historical data
            ticker = yf.Ticker(symbol)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=lookback_days)

            # Get daily and intraday data
            df_daily = ticker.history(start=start_date, end=end_date, interval='1d')
            df_1h = ticker.history(start=start_date, end=end_date, interval='1h')

            if df_daily.empty or df_1h.empty:
                logger.warning(f"No historical data for {symbol}")
                return result

            # Simulate trades
            trades = []

            for i in range(5, len(df_daily) - option_dte):
                current_date = df_daily.index[i]
                current_price = df_daily['Close'].iloc[i]

                # Get recent price history (last 5 days)
                recent_prices = df_daily['Close'].iloc[i-5:i].values

                # Calculate momentum
                momentum_3d = (current_price / df_daily['Close'].iloc[i-3] - 1)
                momentum_5d = (current_price / df_daily['Close'].iloc[i-5] - 1)

                # Simple strategy signals
                signal_generated = False

                # BULLISH SIGNAL: 3-day uptrend + pullback
                if momentum_3d > 0.02:  # 2%+ move in 3 days
                    # Simulate buying a CALL option
                    entry_price = current_price * 0.03  # Simulate option at ~3% of stock price
                    signal_generated = True
                    direction = "CALL"

                # BEARISH SIGNAL: 3-day downtrend + bounce
                elif momentum_3d < -0.02:
                    # Simulate buying a PUT option
                    entry_price = current_price * 0.03
                    signal_generated = True
                    direction = "PUT"

                if signal_generated:
                    # Simulate holding for DTE days or until hit target/stop
                    trade = self._simulate_trade_outcome(
                        symbol=symbol,
                        entry_date=current_date,
                        entry_price=entry_price,
                        direction=direction,
                        stock_prices=df_daily['Close'].iloc[i:i+option_dte+1],
                        delta=delta_target,
                        dte=option_dte
                    )

                    if trade:
                        trades.append(trade)

            # Calculate results
            result.trades = trades
            result.total_trades = len(trades)

            if trades:
                winners = [t for t in trades if t.profit_loss and t.profit_loss > 0]
                losers = [t for t in trades if t.profit_loss and t.profit_loss <= 0]

                result.winners = len(winners)
                result.losers = len(losers)
                result.win_rate = (len(winners) / len(trades)) * 100

                if winners:
                    result.avg_win = sum(t.profit_loss_percent for t in winners) / len(winners)
                    result.best_trade = max(t.profit_loss_percent for t in winners)

                if losers:
                    result.avg_loss = sum(t.profit_loss_percent for t in losers) / len(losers)
                    result.worst_trade = min(t.profit_loss_percent for t in losers)

                total_profit = sum(t.profit_loss for t in winners)
                total_loss = sum(abs(t.profit_loss) for t in losers)

                if total_loss > 0:
                    result.profit_factor = total_profit / total_loss

                result.total_pnl = sum(t.profit_loss for t in trades if t.profit_loss)

                # Average holding period
                holding_periods = [(t.exit_time - t.entry_time).days for t in trades if t.exit_time]
                if holding_periods:
                    result.avg_holding_period = sum(holding_periods) / len(holding_periods)

            logger.info(f"Backtest complete: {result.total_trades} trades, {result.win_rate:.1f}% win rate")

        except Exception as e:
            logger.error(f"Error backtesting {symbol}: {e}")

        return result

    def _simulate_trade_outcome(
        self,
        symbol: str,
        entry_date: datetime,
        entry_price: float,
        direction: str,
        stock_prices: np.ndarray,
        delta: float,
        dte: int
    ) -> Optional[PaperTrade]:
        """
        Simulate a single trade's outcome

        Args:
            symbol: Stock symbol
            entry_date: Entry date
            entry_price: Entry option price
            direction: "CALL" or "PUT"
            stock_prices: Future stock prices
            delta: Option delta
            dte: Days to expiration

        Returns:
            PaperTrade with simulated outcome
        """
        target_price = entry_price * 1.30  # 30% target
        stop_price = entry_price * 0.85    # 15% stop

        # Simulate each day
        for day_num in range(1, min(len(stock_prices), dte + 1)):
            stock_move = (stock_prices.iloc[day_num] / stock_prices.iloc[0]) - 1

            # Reverse move for PUTs
            if direction == "PUT":
                stock_move = -stock_move

            # Simulate option price
            current_option_price = self.simulate_option_price_movement(
                stock_move_percent=stock_move,
                delta=delta,
                initial_option_price=entry_price,
                days_elapsed=day_num
            )

            # Check if hit target
            if current_option_price >= target_price:
                return self._create_trade(
                    symbol, entry_date, entry_price, target_price,
                    day_num, TradeOutcome.HIT_TARGET, direction
                )

            # Check if hit stop
            if current_option_price <= stop_price:
                return self._create_trade(
                    symbol, entry_date, entry_price, stop_price,
                    day_num, TradeOutcome.HIT_STOP, direction
                )

        # Expired
        final_price = self.simulate_option_price_movement(
            stock_move_percent=(stock_prices.iloc[-1] / stock_prices.iloc[0]) - 1,
            delta=delta,
            initial_option_price=entry_price,
            days_elapsed=len(stock_prices) - 1
        )

        return self._create_trade(
            symbol, entry_date, entry_price, final_price,
            len(stock_prices) - 1, TradeOutcome.EXPIRED_WORTHLESS, direction
        )

    def _create_trade(
        self,
        symbol: str,
        entry_date: datetime,
        entry_price: float,
        exit_price: float,
        days_held: int,
        outcome: TradeOutcome,
        direction: str
    ) -> PaperTrade:
        """Create a PaperTrade from backtest results"""
        trade = PaperTrade(
            signal_id=f"backtest_{symbol}_{entry_date.strftime('%Y%m%d')}",
            symbol=symbol,
            strategy="BACKTEST",
            action=f"BUY_{direction}",
            entry_price=entry_price,
            entry_time=entry_date,
            target_price=entry_price * 1.30,
            stop_loss=entry_price * 0.85,
            strike=0.0,
            option_type=direction.lower(),
            expiration=(entry_date + timedelta(days=7)).strftime("%Y-%m-%d"),
            outcome=outcome,
            exit_price=exit_price,
            exit_time=entry_date + timedelta(days=days_held)
        )

        trade.profit_loss = exit_price - entry_price
        trade.profit_loss_percent = (trade.profit_loss / entry_price) * 100

        return trade

    def get_summary_report(self, result: BacktestResult) -> str:
        """Generate human-readable summary report"""
        if result.total_trades == 0:
            return "No trades generated in backtest"

        report = f"""
╔═══════════════════════════════════════════════════════════╗
║           BACKTEST RESULTS                                  ║
╠═══════════════════════════════════════════════════════════╣
║  Total Trades:        {result.total_trades:3d}                              ║
║  Winners:             {result.winners:3d}  ({result.win_rate:.1f}%)                   ║
║  Losers:              {result.losers:3d}                                    ║
║                                                             ║
║  Win Rate:            {result.win_rate:5.1f}%                              ║
║  Profit Factor:       {result.profit_factor:5.2f}x                            ║
║                                                             ║
║  Avg Win:             +{result.avg_win:5.1f}%                              ║
║  Avg Loss:            {result.avg_loss:6.1f}%                             ║
║  Best Trade:          +{result.best_trade:5.1f}%                              ║
║  Worst Trade:         {result.worst_trade:6.1f}%                             ║
║                                                             ║
║  Total P/L:           ${result.total_pnl:7.2f}                            ║
║  Avg Hold:            {result.avg_holding_period:4.1f} days                         ║
╚═══════════════════════════════════════════════════════════╝
"""
        return report
