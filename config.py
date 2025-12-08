"""
Configuration settings for TradeFly Backend
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # OpenAI
    openai_api_key: str

    # Supabase
    supabase_url: str
    supabase_service_key: str

    # Market Data Provider (Choose ONE)
    # Alpaca
    alpaca_api_key: str = ""
    alpaca_secret_key: str = ""

    # Polygon.io (you're using this!)
    polygon_api_key: str = ""

    # Yahoo Finance
    use_yahoo_finance: bool = False

    # Optional: News APIs
    benzinga_api_key: str = ""  # $99/month - Best for trading news
    news_api_key: str = ""      # $49/month - General news

    # App settings
    environment: str = "development"
    log_level: str = "INFO"
    signal_check_interval: int = 60
    tickers_to_watch: str = "NVDA,TSLA,AAPL,AMD,MSFT,GOOGL,AMZN,META"

    @property
    def tickers_list(self) -> List[str]:
        """Convert comma-separated tickers to list"""
        return [t.strip() for t in self.tickers_to_watch.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Allow extra fields in .env file


# Global settings instance
settings = Settings()
