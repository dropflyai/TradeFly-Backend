"""
GPT-5 AI Analysis for trading signals
Uses Expert Trading System with Live Context
"""
import logging
import json
from openai import OpenAI
from config import settings
from models import GPT5AnalysisResponse, SignalQuality
from expert_system import get_expert_system_prompt, get_pattern_specific_rules
from live_context_builder import LiveContextBuilder
from market_data import MarketDataService

logger = logging.getLogger(__name__)


class AIAnalyzer:
    """Use GPT-5 to analyze and rate trading signals"""

    def __init__(self, market_service: MarketDataService, news_service=None):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.context_builder = LiveContextBuilder(market_service, news_service)
        self.market_service = market_service
        self.news_service = news_service
        logger.info("AIAnalyzer initialized with GPT-5 Expert System")

    async def analyze_signal(self, signal_data: dict) -> GPT5AnalysisResponse:
        """
        Analyze a detected signal using GPT-5 Expert System

        Args:
            signal_data: Dict with ticker, signal_type, market_data, pattern_detected

        Returns:
            GPT5AnalysisResponse with quality rating and reasoning
        """
        try:
            ticker = signal_data['ticker']

            # Get multi-timeframe data for comprehensive analysis
            # Note: In production, fetch actual 5m and daily bars
            # For now, using 1m data as placeholder
            data_5m = signal_data['market_data']  # TODO: Fetch actual 5-minute data
            data_daily = signal_data['market_data']  # TODO: Fetch actual daily data

            # Build live context with real-time market data (async now supports news)
            live_context = await self.context_builder.build_analysis_context(
                signal_data,
                data_5m=data_5m,
                data_daily=data_daily
            )

            # Get pattern-specific rules if available
            pattern_rules = get_pattern_specific_rules(signal_data['signal_type'])
            if pattern_rules:
                live_context += f"\n\n{pattern_rules}"

            # Get expert trading system prompt
            expert_system = get_expert_system_prompt()

            # Call GPT-5 - OpenAI's latest model
            response = self.client.chat.completions.create(
                model="gpt-5",  # GPT-5 model
                messages=[
                    {
                        "role": "system",
                        "content": expert_system  # Our comprehensive trading rules
                    },
                    {
                        "role": "user",
                        "content": live_context  # Real-time market data and context
                    }
                ],
                temperature=0.2,  # Very low for consistent, conservative analysis
                max_tokens=2000,  # More tokens for detailed analysis
                response_format={"type": "json_object"}
            )

            # Parse response
            analysis = json.loads(response.choices[0].message.content)

            # Log the analysis for monitoring
            logger.info(f"GPT-5 Analysis for {ticker}: {analysis['quality']} "
                       f"(confidence: {analysis.get('confidence_score', 0)}%)")

            return GPT5AnalysisResponse(
                quality=SignalQuality(analysis['quality']),
                confidence_score=analysis.get('confidence_score', 0),
                reasoning=analysis.get('reasoning', 'No reasoning provided'),
                risk_factors=analysis.get('risk_factors', []),
                entry_recommendation=analysis.get('entry_recommendation', signal_data['market_data'].price),
                stop_loss_recommendation=analysis.get('stop_loss_recommendation', signal_data['market_data'].price * 0.98),
                take_profit_recommendation=analysis.get('take_profit_recommendation', signal_data['market_data'].price * 1.02)
            )

        except Exception as e:
            logger.error(f"Error in GPT-5 analysis: {e}", exc_info=True)
            # Return conservative default on error
            return GPT5AnalysisResponse(
                quality=SignalQuality.LOW,
                confidence_score=0,
                reasoning=f"Analysis failed: {str(e)}. System defaulted to LOW quality for safety.",
                risk_factors=["Analysis error - GPT-5 API call failed"],
                entry_recommendation=signal_data['market_data'].price,
                stop_loss_recommendation=signal_data['market_data'].price * 0.98,
                take_profit_recommendation=signal_data['market_data'].price * 1.02
            )
