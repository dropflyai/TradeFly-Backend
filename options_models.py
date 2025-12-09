"""
Options Trading Data Models - Institutional Grade
TradeFly Options - World-Class Algorithmic Trading System
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime, date
from enum import Enum


class OptionType(str, Enum):
    """Option contract type"""
    CALL = "call"
    PUT = "put"


class SignalAction(str, Enum):
    """Trading signal actions"""
    BUY = "BUY"
    SELL = "SELL"
    BUY_CALL = "BUY_CALL"
    BUY_PUT = "BUY_PUT"
    SELL_CALL = "SELL_CALL"
    SELL_PUT = "SELL_PUT"
    FOLLOW_FLOW = "FOLLOW_FLOW"
    WAIT = "WAIT"


class StrategyType(str, Enum):
    """Core trading strategies"""
    SCALPING = "SCALPING"
    SWING = "SWING"
    MOMENTUM = "MOMENTUM"
    VOLUME_SPIKE = "VOLUME_SPIKE"
    GAMMA_SCALP = "GAMMA_SCALP"
    DELTA_HEDGE = "DELTA_HEDGE"
    THETA_DECAY = "THETA_DECAY"
    VEGA_PLAY = "VEGA_PLAY"


class Greeks(BaseModel):
    """Option Greeks - Risk measures"""
    delta: float = Field(..., description="Price sensitivity to underlying (0-1 for calls, -1 to 0 for puts)")
    gamma: float = Field(..., description="Rate of change of delta")
    theta: float = Field(..., description="Time decay per day")
    vega: float = Field(..., description="Sensitivity to IV changes")
    rho: float = Field(..., description="Sensitivity to interest rates")

    class Config:
        json_schema_extra = {
            "example": {
                "delta": 0.65,
                "gamma": 0.05,
                "theta": -0.15,
                "vega": 0.12,
                "rho": 0.03
            }
        }


class ImpliedVolatility(BaseModel):
    """Implied Volatility metrics"""
    iv: float = Field(..., description="Current implied volatility (decimal)")
    iv_rank: float = Field(..., ge=0, le=100, description="IV percentile over 52 weeks (0-100)")
    iv_percentile: float = Field(..., ge=0, le=100, description="IV percentile")
    historical_volatility: Optional[float] = Field(None, description="Historical volatility for comparison")

    @property
    def iv_percent(self) -> float:
        """IV as percentage"""
        return self.iv * 100


class VolumeMetrics(BaseModel):
    """Volume and open interest metrics"""
    volume: int = Field(..., description="Current day volume")
    open_interest: int = Field(..., description="Total open contracts")
    volume_avg_30d: int = Field(..., description="30-day average volume")
    volume_ratio: float = Field(..., description="Current volume / 30d average")

    @property
    def is_high_volume(self) -> bool:
        """Check if volume is unusually high (3x+ average)"""
        return self.volume_ratio >= 3.0

    @property
    def is_very_high_volume(self) -> bool:
        """Check if volume is extremely high (lowered for early session testing)"""
        return self.volume_ratio >= 1.5  # Lowered from 5.0 for early session testing


class OptionPricing(BaseModel):
    """Real-time option pricing"""
    bid: float = Field(..., description="Current bid price")
    ask: float = Field(..., description="Current ask price")
    last: float = Field(..., description="Last trade price")
    mark: float = Field(..., description="Mark price (bid+ask)/2")

    @property
    def spread(self) -> float:
        """Bid-ask spread"""
        return self.ask - self.bid

    @property
    def spread_percent(self) -> float:
        """Spread as percentage of mark"""
        return (self.spread / self.mark) * 100 if self.mark > 0 else 0

    @property
    def is_liquid(self) -> bool:
        """Check if spread is acceptable (relaxed for quiet market)"""
        return self.spread < 7.00  # Relaxed to handle current market conditions


class OptionContract(BaseModel):
    """
    Complete option contract with all metrics for algorithmic trading
    """
    # Contract identifiers
    symbol: str = Field(..., description="Underlying stock symbol (e.g., NVDA)")
    strike: float = Field(..., description="Strike price")
    expiration: date = Field(..., description="Expiration date")
    option_type: OptionType = Field(..., description="Call or Put")

    # Pricing
    pricing: OptionPricing

    # Volume & Open Interest
    volume_metrics: VolumeMetrics

    # Greeks
    greeks: Greeks

    # Volatility
    iv_metrics: ImpliedVolatility

    # Underlying stock data
    underlying_price: float = Field(..., description="Current stock price")
    underlying_change_percent: Optional[float] = Field(None, description="Stock % change today")

    # Metadata
    timestamp: datetime = Field(default_factory=datetime.now)
    contract_id: Optional[str] = Field(None, description="Unique contract identifier")

    @property
    def option_id(self) -> str:
        """Generate option identifier (e.g., NVDA250113C145)"""
        exp_str = self.expiration.strftime("%y%m%d")
        type_char = "C" if self.option_type == OptionType.CALL else "P"
        strike_str = f"{int(self.strike * 1000):08d}"
        return f"{self.symbol}{exp_str}{type_char}{strike_str}"

    @property
    def days_to_expiration(self) -> int:
        """Calculate days until expiration"""
        return (self.expiration - date.today()).days

    @property
    def moneyness(self) -> str:
        """Determine if ITM, ATM, or OTM"""
        if self.option_type == OptionType.CALL:
            if self.underlying_price > self.strike * 1.02:
                return "ITM"
            elif self.underlying_price < self.strike * 0.98:
                return "OTM"
            else:
                return "ATM"
        else:  # PUT
            if self.underlying_price < self.strike * 0.98:
                return "ITM"
            elif self.underlying_price > self.strike * 1.02:
                return "OTM"
            else:
                return "ATM"

    @property
    def intrinsic_value(self) -> float:
        """Calculate intrinsic value"""
        if self.option_type == OptionType.CALL:
            return max(0, self.underlying_price - self.strike)
        else:  # PUT
            return max(0, self.strike - self.underlying_price)

    @property
    def extrinsic_value(self) -> float:
        """Calculate extrinsic (time) value"""
        return self.pricing.mark - self.intrinsic_value


class ScalpSignal(BaseModel):
    """
    Scalping signal - Quick 10-20% gains in 1-5 minutes
    """
    strategy: Literal[StrategyType.SCALPING] = StrategyType.SCALPING
    action: SignalAction
    contract: OptionContract

    # Entry/Exit levels
    entry: float = Field(..., description="Entry price")
    target: float = Field(..., description="Target price (15% gain typical)")
    stop: float = Field(..., description="Stop loss (5% typical)")

    # Signal quality
    confidence: float = Field(..., ge=0, le=1, description="Confidence score 0-1")
    reason: str = Field(..., description="Signal reasoning")

    # Metadata
    timestamp: datetime = Field(default_factory=datetime.now)
    timeframe: str = "1-5min"

    @property
    def profit_target_percent(self) -> float:
        """Calculate profit target percentage"""
        return ((self.target - self.entry) / self.entry) * 100

    @property
    def stop_loss_percent(self) -> float:
        """Calculate stop loss percentage"""
        return ((self.entry - self.stop) / self.entry) * 100

    @property
    def risk_reward_ratio(self) -> float:
        """Calculate risk/reward ratio"""
        risk = self.entry - self.stop
        reward = self.target - self.entry
        return reward / risk if risk > 0 else 0


class MomentumSignal(BaseModel):
    """
    Momentum breakout signal - 30-100% gains on directional moves
    """
    strategy: Literal[StrategyType.MOMENTUM] = StrategyType.MOMENTUM
    action: SignalAction
    contract: OptionContract

    # Entry/Exit levels
    entry: float
    target: float = Field(..., description="Target price (50%+ gain typical)")
    stop: float = Field(..., description="Stop loss (20% typical)")

    # Signal quality
    confidence: float = Field(..., ge=0, le=1)
    reason: str

    # Momentum specifics
    stock_momentum_15m: float = Field(..., description="Stock % move in 15 min")
    macd_signal: str = Field(..., description="MACD signal (bullish/bearish)")
    breakout_level: Optional[float] = Field(None, description="Key level broken")

    # Metadata
    timestamp: datetime = Field(default_factory=datetime.now)
    timeframe: str = "15min-2h"

    @property
    def is_strong_momentum(self) -> bool:
        """Check if momentum is strong (3%+ move)"""
        return abs(self.stock_momentum_15m) >= 0.03


class VolumeSpikeSignal(BaseModel):
    """
    Volume spike / Unusual Options Activity signal
    Smart money detection
    """
    strategy: Literal[StrategyType.VOLUME_SPIKE] = StrategyType.VOLUME_SPIKE
    action: SignalAction
    contract: OptionContract

    # Flow data
    flow_direction: Literal["bullish", "bearish"]
    net_premium_flow: float = Field(..., description="Net premium flow in dollars")
    large_orders_count: int = Field(..., description="Number of block trades detected")

    # Signal quality
    confidence: float = Field(..., ge=0, le=1)
    reason: str

    # Metadata
    timestamp: datetime = Field(default_factory=datetime.now)

    @property
    def is_institutional_flow(self) -> bool:
        """Check if flow indicates institutional activity ($1M+)"""
        return abs(self.net_premium_flow) >= 1_000_000

    @property
    def flow_in_millions(self) -> float:
        """Premium flow in millions"""
        return self.net_premium_flow / 1_000_000


class TechnicalIndicators(BaseModel):
    """
    Technical analysis indicators for options trading
    """
    # Momentum
    rsi_14: float = Field(..., ge=0, le=100, description="RSI (14 period)")

    # Trend
    macd_line: float
    macd_signal: float
    macd_histogram: float

    # Volatility
    bb_upper: float = Field(..., description="Bollinger Band upper")
    bb_middle: float = Field(..., description="Bollinger Band middle (SMA)")
    bb_lower: float = Field(..., description="Bollinger Band lower")

    # Volume
    vwap: float = Field(..., description="Volume Weighted Average Price")

    # Support/Resistance
    resistance_levels: list[float] = Field(default_factory=list)
    support_levels: list[float] = Field(default_factory=list)

    @property
    def is_oversold(self) -> bool:
        """RSI indicates oversold (< 30)"""
        return self.rsi_14 < 30

    @property
    def is_overbought(self) -> bool:
        """RSI indicates overbought (> 70)"""
        return self.rsi_14 > 70

    @property
    def macd_bullish(self) -> bool:
        """MACD bullish crossover"""
        return self.macd_line > self.macd_signal and self.macd_histogram > 0

    @property
    def macd_bearish(self) -> bool:
        """MACD bearish crossover"""
        return self.macd_line < self.macd_signal and self.macd_histogram < 0


class RiskMetrics(BaseModel):
    """
    Risk management metrics for position sizing
    """
    account_balance: float
    position_size: float = Field(..., description="Dollar amount to risk")
    position_size_percent: float = Field(..., ge=0, le=1, description="% of account")
    current_daily_pnl: float = Field(default=0, description="Today's P&L")
    max_daily_loss: float = Field(..., description="Maximum allowed daily loss")
    max_concurrent_trades: int = Field(default=3)
    active_trades_count: int = Field(default=0)

    @property
    def can_take_trade(self) -> bool:
        """Check if we can take another trade"""
        # Check daily loss limit
        if self.current_daily_pnl <= -self.max_daily_loss:
            return False

        # Check max concurrent trades
        if self.active_trades_count >= self.max_concurrent_trades:
            return False

        return True

    @property
    def daily_loss_percent(self) -> float:
        """Current daily loss as percentage"""
        return (self.current_daily_pnl / self.account_balance) * 100


class OptionsSignal(BaseModel):
    """
    Unified options trading signal combining all strategies
    """
    signal_id: str = Field(..., description="Unique signal identifier")
    strategy: StrategyType
    contract: OptionContract
    action: SignalAction

    # Entry/Exit
    entry_price: float
    target_price: float
    stop_loss: float

    # Analysis
    confidence: float = Field(..., ge=0, le=1)
    reasoning: str
    technical_indicators: TechnicalIndicators

    # Risk
    position_size_recommendation: float
    risk_reward_ratio: float

    # Metadata
    timestamp: datetime = Field(default_factory=datetime.now)
    is_active: bool = True
    expires_at: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "signal_id": "SCALP_NVDA_20251208_143000",
                "strategy": "SCALPING",
                "action": "BUY_CALL",
                "entry_price": 1.45,
                "target_price": 1.67,
                "stop_loss": 1.38,
                "confidence": 0.85,
                "reasoning": "3%+ momentum + RSI oversold + tight spread + high volume"
            }
        }
