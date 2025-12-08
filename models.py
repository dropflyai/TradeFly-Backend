"""
Data models for TradeFly Backend
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
from enum import Enum


class SignalType(str, Enum):
    """Trading signal types"""
    ORB_BREAKOUT_LONG = "ORB_BREAKOUT_LONG"
    VWAP_RECLAIM_LONG = "VWAP_RECLAIM_LONG"
    EMA_TREND_LONG = "EMA_TREND_CONTINUATION_LONG"
    HOD_BREAKOUT_LONG = "HOD_BREAKOUT_LONG"
    ORB_BREAKDOWN_PUT = "ORB_BREAKDOWN_PUT"
    VWAP_REJECT_PUT = "VWAP_REJECT_PUT"
    LOD_BREAK_PUT = "LOD_BREAK_PUT"


class SignalQuality(str, Enum):
    """Signal quality ratings"""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class AssetType(str, Enum):
    """Asset type classification"""
    STOCK = "stock"
    CRYPTO = "crypto"


def detect_asset_type(ticker: str) -> AssetType:
    """
    Detect if a ticker is a stock or crypto based on naming convention.
    Crypto tickers typically end with -USD, -USDT, -BTC, etc.
    """
    ticker_upper = ticker.upper()
    crypto_suffixes = ('-USD', '-USDT', '-BTC', '-ETH', '-BUSD')

    if any(ticker_upper.endswith(suffix) for suffix in crypto_suffixes):
        return AssetType.CRYPTO
    return AssetType.STOCK


class MarketData(BaseModel):
    """Real-time market data for a ticker"""
    ticker: str
    timestamp: datetime
    price: float
    open: float
    high: float
    low: float
    volume: int
    vwap: float
    ema9: float
    ema20: float
    ema50: float


class TradingSignal(BaseModel):
    """Complete trading signal with AI analysis"""
    ticker: str
    asset_type: AssetType  # NEW: Classify as stock or crypto
    signal_type: SignalType
    quality: SignalQuality
    timestamp: datetime

    # Price data
    current_price: float
    entry_price: float
    stop_loss: float
    take_profit_1: float
    take_profit_2: Optional[float] = None

    # Technical indicators
    vwap: float
    ema9: float
    ema20: float
    ema50: float
    volume: int
    avg_volume: int

    # AI Analysis
    ai_reasoning: str
    confidence_score: int = Field(ge=0, le=100)
    risk_factors: list[str] = []

    # News context (NEW)
    related_news: list[dict] = []  # Stock-specific news
    market_news: list[dict] = []   # Broad market news

    # Metadata
    timeframe: str = "1min"
    is_active: bool = True


class GPT5AnalysisRequest(BaseModel):
    """Request format for GPT-5 analysis"""
    ticker: str
    signal_type: str
    market_data: MarketData
    pattern_detected: str


class GPT5AnalysisResponse(BaseModel):
    """Response from GPT-5 analysis"""
    quality: SignalQuality
    confidence_score: int
    reasoning: str
    risk_factors: list[str]
    entry_recommendation: float
    stop_loss_recommendation: float
    take_profit_recommendation: float
