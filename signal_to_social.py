"""
Signal-to-Social Conversion System
Converts algorithmic trading signals into shareable social posts
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional
from uuid import UUID
from social_models import (
    PostCreate, SignalPost, Sentiment, PostType
)

logger = logging.getLogger(__name__)


class SignalConverter:
    """Convert trading signals to social posts"""

    # System user ID for posting TradeFly signals
    TRADEFLY_BOT_ID = UUID("00000000-0000-0000-0000-000000000000")

    @staticmethod
    def format_contract_symbol(contract: Dict[str, Any]) -> str:
        """
        Format contract into social tag format
        Example: AAPL $150C 12/15 → AAPL_150C_12/15
        """
        symbol = contract.get("symbol", "")
        strike = contract.get("strike", 0)
        option_type = contract.get("option_type", "call")
        expiration = contract.get("expiration", "")

        # Option type abbreviation
        opt_type = "C" if option_type.lower() == "call" else "P"

        # Format expiration from YYYY-MM-DD to MM/DD
        if expiration:
            try:
                exp_date = datetime.fromisoformat(expiration.replace('Z', '+00:00'))
                exp_str = exp_date.strftime("%m/%d")
            except:
                exp_str = expiration
        else:
            exp_str = ""

        return f"{symbol}_{int(strike)}{opt_type}_{exp_str}"

    @staticmethod
    def determine_sentiment(signal: Dict[str, Any]) -> Sentiment:
        """Determine sentiment from signal action"""
        action = signal.get("action", "").upper()

        if "CALL" in action or "BULLISH" in action:
            return Sentiment.BULLISH_CALL
        elif "PUT" in action or "BEARISH" in action:
            return Sentiment.BEARISH_PUT
        else:
            return Sentiment.NEUTRAL

    @staticmethod
    def generate_scalping_narrative(signal: Dict[str, Any]) -> str:
        """Generate narrative for scalping signals"""
        contract = signal.get("contract", {})
        greeks = contract.get("greeks", {})

        symbol = contract.get("symbol", "")
        strike = contract.get("strike", 0)
        option_type = contract.get("option_type", "call").upper()[0]

        entry = signal.get("entry", 0)
        target = signal.get("target", 0)
        stop_loss = signal.get("stop_loss", 0)
        confidence = signal.get("confidence", 0)

        # Calculate percentages
        target_pct = ((target / entry) - 1) * 100 if entry > 0 else 0
        stop_pct = ((1 - stop_loss / entry)) * 100 if entry > 0 else 0

        delta = greeks.get("delta", 0)
        iv = greeks.get("implied_volatility", 0)

        reasoning = signal.get("reasoning", "Strong momentum setup")

        narrative = f"""🎯 SCALP SIGNAL: {symbol} ${int(strike)}{option_type}

📊 Entry: ${entry:.2f}
🎯 Target: ${target:.2f} (+{target_pct:.1f}%)
🛑 Stop: ${stop_loss:.2f} (-{stop_pct:.1f}%)

⚡ Confidence: {confidence*100:.0f}%
⏱️ Timeframe: 2-5 minutes

📈 Greeks:
• Delta: {delta:.2f}
• IV: {iv*100:.1f}%

💡 {reasoning}

#Scalping #OptionsTrading #{symbol}
"""
        return narrative.strip()

    @staticmethod
    def generate_momentum_narrative(signal: Dict[str, Any]) -> str:
        """Generate narrative for momentum signals"""
        contract = signal.get("contract", {})
        greeks = contract.get("greeks", {})
        candlestick = signal.get("candlestick_pattern", {})

        symbol = contract.get("symbol", "")
        strike = contract.get("strike", 0)
        option_type = contract.get("option_type", "call").upper()[0]

        entry = signal.get("entry", 0)
        target = signal.get("target", 0)
        stop_loss = signal.get("stop_loss", 0)
        confidence = signal.get("confidence", 0)

        target_pct = ((target / entry) - 1) * 100 if entry > 0 else 0
        stop_pct = ((1 - stop_loss / entry)) * 100 if entry > 0 else 0

        delta = greeks.get("delta", 0)
        gamma = greeks.get("gamma", 0)

        pattern_name = candlestick.get("pattern_name", "")
        reasoning = signal.get("reasoning", "Momentum breakout confirmed")

        narrative = f"""🚀 MOMENTUM SIGNAL: {symbol} ${int(strike)}{option_type}

📊 Entry: ${entry:.2f}
🎯 Target: ${target:.2f} (+{target_pct:.1f}%)
🛑 Stop: ${stop_loss:.2f} (-{stop_pct:.1f}%)

⚡ Confidence: {confidence*100:.0f}%
⏱️ Timeframe: 15min - 2hr

📈 Setup:
• Pattern: {pattern_name if pattern_name else 'Breakout'}
• Delta: {delta:.2f}
• Gamma: {gamma:.4f}

💡 {reasoning}

#Momentum #Breakout #{symbol}
"""
        return narrative.strip()

    @staticmethod
    def generate_volume_spike_narrative(signal: Dict[str, Any]) -> str:
        """Generate narrative for volume spike (flow) signals"""
        contract = signal.get("contract", {})
        greeks = contract.get("greeks", {})
        volume_metrics = contract.get("volume_metrics", {})

        symbol = contract.get("symbol", "")
        strike = contract.get("strike", 0)
        option_type = contract.get("option_type", "call").upper()[0]

        entry = signal.get("entry", 0)
        target = signal.get("target", 0)
        stop_loss = signal.get("stop_loss", 0)
        confidence = signal.get("confidence", 0)

        target_pct = ((target / entry) - 1) * 100 if entry > 0 else 0
        stop_pct = ((1 - stop_loss / entry)) * 100 if entry > 0 else 0

        volume = volume_metrics.get("volume", 0)
        oi = volume_metrics.get("open_interest", 0)
        vol_oi_ratio = volume_metrics.get("volume_oi_ratio", 0)

        delta = greeks.get("delta", 0)

        reasoning = signal.get("reasoning", "Unusual institutional activity detected")

        narrative = f"""🐋 FLOW SIGNAL: {symbol} ${int(strike)}{option_type}

📊 Entry: ${entry:.2f}
🎯 Target: ${target:.2f} (+{target_pct:.1f}%)
🛑 Stop: ${stop_loss:.2f} (-{stop_pct:.1f}%)

⚡ Confidence: {confidence*100:.0f}%
⏱️ Smart Money Flow

📈 Unusual Activity:
• Volume: {volume:,}
• OI: {oi:,}
• Vol/OI: {vol_oi_ratio:.2f}x
• Delta: {delta:.2f}

💡 {reasoning}

#Flow #SmartMoney #UnusualActivity #{symbol}
"""
        return narrative.strip()

    @classmethod
    def signal_to_post(cls, signal: Dict[str, Any]) -> PostCreate:
        """
        Convert a signal to a PostCreate object

        Args:
            signal: Signal dictionary from options_signal_detector

        Returns:
            PostCreate object ready to be posted
        """
        try:
            contract = signal.get("contract", {})
            strategy = signal.get("strategy", "").lower()

            # Generate narrative based on strategy
            if strategy == "scalping":
                content = cls.generate_scalping_narrative(signal)
            elif strategy == "momentum":
                content = cls.generate_momentum_narrative(signal)
            elif strategy == "volume_spike":
                content = cls.generate_volume_spike_narrative(signal)
            else:
                content = f"New signal detected for {contract.get('symbol', '')}"

            # Format contract symbol for tagging
            contract_symbol = cls.format_contract_symbol(contract)
            underlying_symbol = contract.get("symbol", "")

            # Determine sentiment
            sentiment = cls.determine_sentiment(signal)

            # Create post
            post = PostCreate(
                content=content,
                media_urls=[],  # TODO: Generate chart images
                contract_symbol=contract_symbol,
                underlying_symbol=underlying_symbol,
                sentiment=sentiment,
                strategy=strategy,
                post_type=PostType.SIGNAL,
                signal_id=None,  # Will be set when signal is saved to DB
                signal_data=signal,  # Embed full signal
                room_id=None  # Public feed
            )

            logger.info(f"✅ Converted signal to post: {underlying_symbol} {strategy}")
            return post

        except Exception as e:
            logger.error(f"❌ Error converting signal to post: {e}")
            raise

    @classmethod
    def trade_result_to_post(cls, trade: Dict[str, Any]) -> PostCreate:
        """
        Convert a completed trade to a shareable result post

        Args:
            trade: Trade result dictionary with entry, exit, P&L

        Returns:
            PostCreate object for trade result
        """
        try:
            contract = trade.get("contract", {})
            signal = trade.get("signal", {})

            symbol = contract.get("symbol", "")
            strike = contract.get("strike", 0)
            option_type = contract.get("option_type", "call").upper()[0]

            entry_price = trade.get("entry_price", 0)
            exit_price = trade.get("exit_price", 0)
            pnl = trade.get("pnl", 0)
            pnl_pct = ((exit_price - entry_price) / entry_price) * 100 if entry_price > 0 else 0

            entry_time = trade.get("entry_time", datetime.utcnow())
            exit_time = trade.get("exit_time", datetime.utcnow())

            if isinstance(entry_time, str):
                entry_time = datetime.fromisoformat(entry_time.replace('Z', '+00:00'))
            if isinstance(exit_time, str):
                exit_time = datetime.fromisoformat(exit_time.replace('Z', '+00:00'))

            hold_minutes = (exit_time - entry_time).total_seconds() / 60

            strategy = trade.get("strategy", "")
            confidence = signal.get("confidence", 0)
            notes = trade.get("notes", "")
            verified = trade.get("verified", False)

            emoji = "✅" if pnl > 0 else "❌" if pnl < 0 else "⚖️"

            content = f"""{emoji} TRADE CLOSED: {symbol} ${int(strike)}{option_type}

💰 P&L: ${pnl:,.2f} ({pnl_pct:+.1f}%)

📊 Entry: ${entry_price:.2f} @ {entry_time.strftime('%H:%M')}
📊 Exit: ${exit_price:.2f} @ {exit_time.strftime('%H:%M')}
⏱️ Hold Time: {int(hold_minutes)} minutes

📈 Strategy: {strategy.title()}
⚡ Confidence: {confidence*100:.0f}%

{f'💡 Notes: {notes}' if notes else ''}

{' VERIFIED' if verified else '⚠️ UNVERIFIED'}
"""

            contract_symbol = cls.format_contract_symbol(contract)

            post = PostCreate(
                content=content.strip(),
                media_urls=[],  # TODO: Generate P&L chart
                contract_symbol=contract_symbol,
                underlying_symbol=symbol,
                sentiment=Sentiment.BULLISH_CALL if pnl > 0 else Sentiment.BEARISH_PUT,
                strategy=strategy,
                post_type=PostType.TRADE_RESULT,
                signal_data=trade,
                room_id=None
            )

            logger.info(f"✅ Converted trade result to post: {symbol} P&L=${pnl:.2f}")
            return post

        except Exception as e:
            logger.error(f"❌ Error converting trade result to post: {e}")
            raise

    @staticmethod
    def extract_hashtags(content: str) -> list:
        """Extract hashtags from post content"""
        import re
        return re.findall(r'#(\w+)', content)

    @staticmethod
    def extract_mentions(content: str) -> list:
        """Extract @mentions from post content"""
        import re
        return re.findall(r'@(\w+)', content)

    @staticmethod
    def parse_contract_tag(tag: str) -> Optional[Dict[str, str]]:
        """
        Parse contract tag back to components
        Example: AAPL_150C_12/15 → {symbol: AAPL, strike: 150, type: C, exp: 12/15}
        """
        try:
            import re
            match = re.match(r'([A-Z]+)_(\d+)([CP])_(\d{2}/\d{2})', tag)
            if match:
                return {
                    "symbol": match.group(1),
                    "strike": match.group(2),
                    "option_type": "call" if match.group(3) == "C" else "put",
                    "expiration": match.group(4)
                }
            return None
        except Exception:
            return None


# Convenience functions
def convert_signal_to_post(signal: Dict[str, Any]) -> PostCreate:
    """Convert signal to post (convenience function)"""
    return SignalConverter.signal_to_post(signal)


def convert_trade_to_post(trade: Dict[str, Any]) -> PostCreate:
    """Convert trade result to post (convenience function)"""
    return SignalConverter.trade_result_to_post(trade)
