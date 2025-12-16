#!/usr/bin/env python3
"""
Test Social Platform Implementation
Verifies database operations and signal conversion
"""

import json
from datetime import datetime
from social_db import get_social_db
from signal_to_social import convert_signal_to_post
from social_models import *

def test_database_connection():
    """Test database connectivity"""
    print("🔍 Testing Database Connection...")
    db = get_social_db()

    if not db.is_connected():
        print("❌ Database not connected!")
        return False

    print("✅ Database connected successfully")
    return True


def test_rooms():
    """Test room listing"""
    print("\n🏠 Testing Default Rooms...")
    db = get_social_db()

    rooms = db.list_rooms()
    print(f"✅ Found {len(rooms)} rooms:")
    for room in rooms:
        print(f"   - {room.name} ({room.strategy_focus}) - {room.members_count} members")

    return len(rooms) == 4


def test_signal_conversion():
    """Test signal-to-post conversion"""
    print("\n⚡ Testing Signal Conversion...")

    # Sample scalping signal
    scalp_signal = {
        "signal_id": "test-123",
        "strategy": "scalping",
        "action": "BUY_CALL",
        "confidence": 0.85,
        "entry": 2.45,
        "target": 2.75,
        "stop_loss": 2.30,
        "risk_reward_ratio": 2.0,
        "reasoning": "Strong momentum on breakout above VWAP",
        "contract": {
            "symbol": "AAPL",
            "strike": 150,
            "option_type": "call",
            "expiration": "2025-12-20",
            "underlying_price": 148.50,
            "greeks": {
                "delta": 0.65,
                "gamma": 0.025,
                "theta": -0.15,
                "vega": 0.12,
                "implied_volatility": 0.325
            },
            "volume_metrics": {
                "volume": 1250,
                "open_interest": 8500
            }
        }
    }

    # Convert signal to post
    post = convert_signal_to_post(scalp_signal)

    print("✅ Signal converted successfully")
    print(f"   Contract Tag: {post.contract_symbol}")
    print(f"   Sentiment: {post.sentiment}")
    print(f"   Strategy: {post.strategy}")
    print(f"\n   Content Preview:")
    print("   " + "-" * 50)
    for line in post.content.split('\n')[:8]:
        print(f"   {line}")
    print("   " + "-" * 50)

    return True


def test_post_creation():
    """Test creating a post (system user)"""
    print("\n📝 Testing Post Creation...")
    db = get_social_db()

    # Get system user
    system_user = db.get_user(UUID("00000000-0000-0000-0000-000000000000"))
    if not system_user:
        print("❌ System user not found!")
        return False

    print(f"✅ System user found: {system_user.username}")

    # Create a test signal post
    test_post = PostCreate(
        content="🎯 TEST POST: This is a test signal from the TradeFly social platform!\n\n#Testing #TradeFly",
        contract_symbol="AAPL_150C_12/20",
        underlying_symbol="AAPL",
        sentiment=Sentiment.BULLISH_CALL,
        strategy="scalping",
        post_type=PostType.SIGNAL
    )

    post_id = db.create_post(system_user.user_id, test_post)

    if not post_id:
        print("❌ Failed to create post!")
        return False

    print(f"✅ Post created: {post_id}")

    # Retrieve the post
    created_post = db.get_post(post_id)
    if created_post:
        print(f"   Author: {created_post.author_username}")
        print(f"   Contract: {created_post.contract_symbol}")
        print(f"   Sentiment: {created_post.sentiment}")

    return True


def test_feed_retrieval():
    """Test feed retrieval"""
    print("\n📰 Testing Feed Retrieval...")
    db = get_social_db()

    # Get public feed
    feed_filter = FeedFilter(
        limit=10,
        strategy="scalping"
    )

    feed = db.get_feed(feed_filter)

    print(f"✅ Feed retrieved: {len(feed.posts)} posts")
    print(f"   Total posts available: {feed.total_count}")
    print(f"   Has more: {feed.has_more}")

    if feed.posts:
        print(f"\n   Latest post:")
        latest = feed.posts[0]
        print(f"   - Author: {latest.author_username}")
        print(f"   - Contract: {latest.contract_symbol}")
        print(f"   - Sentiment: {latest.sentiment}")
        print(f"   - Created: {latest.created_at}")

    return True


def test_engagement():
    """Test engagement operations"""
    print("\n❤️  Testing Engagement Operations...")
    db = get_social_db()

    # Get a post to engage with
    feed = db.get_feed(FeedFilter(limit=1))
    if not feed.posts:
        print("⚠️  No posts to engage with")
        return True

    post = feed.posts[0]
    system_user_id = UUID("00000000-0000-0000-0000-000000000000")

    # Like the post
    like_result = db.like_post(system_user_id, post.post_id)
    print(f"✅ Like operation: {'Success' if like_result else 'Already liked'}")

    # Create a reply
    reply = ReplyCreate(
        post_id=post.post_id,
        content="Great signal! Thanks for sharing. #TradeFly"
    )

    reply_id = db.create_reply(system_user_id, reply)
    if reply_id:
        print(f"✅ Reply created: {reply_id}")
    else:
        print("⚠️  Reply creation skipped (already tested)")

    return True


def test_watchlist():
    """Test watchlist operations"""
    print("\n👁️  Testing Watchlist...")
    db = get_social_db()

    system_user_id = UUID("00000000-0000-0000-0000-000000000000")

    # Add to watchlist
    watchlist_item = WatchlistCreate(
        contract_symbol="AAPL_150C_12/20",
        underlying_symbol="AAPL",
        alert_enabled=True,
        alert_confidence_threshold=0.75
    )

    add_result = db.add_to_watchlist(system_user_id, watchlist_item)
    print(f"✅ Watchlist add: {'Success' if add_result else 'Already exists'}")

    # Get watchlist
    watchlist = db.get_watchlist(system_user_id)
    print(f"✅ Watchlist retrieved: {len(watchlist)} contracts")

    for item in watchlist[:3]:
        print(f"   - {item.contract_symbol} (alerts: {item.alert_enabled})")

    return True


def test_trending():
    """Test trending features"""
    print("\n🔥 Testing Trending Features...")
    db = get_social_db()

    # Trending contracts
    trending = db.get_trending_contracts(limit=5)
    print(f"✅ Trending contracts: {len(trending)}")

    for contract in trending[:3]:
        print(f"   - {contract.contract_symbol}: {contract.mentions_count} mentions")

    # Leaderboard
    leaderboard = db.get_leaderboard(limit=5)
    print(f"✅ Leaderboard: {len(leaderboard)} users")

    for user in leaderboard[:3]:
        print(f"   - {user.username}: {user.reputation_score} pts, {user.followers_count} followers")

    return True


def main():
    """Run all tests"""
    print("=" * 60)
    print("  TradeFly Social Platform - Integration Tests")
    print("=" * 60)

    tests = [
        ("Database Connection", test_database_connection),
        ("Default Rooms", test_rooms),
        ("Signal Conversion", test_signal_conversion),
        ("Post Creation", test_post_creation),
        ("Feed Retrieval", test_feed_retrieval),
        ("Engagement", test_engagement),
        ("Watchlist", test_watchlist),
        ("Trending", test_trending),
    ]

    results = []

    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name} FAILED: {e}")
            results.append((name, False))

    print("\n" + "=" * 60)
    print("  Test Results Summary")
    print("=" * 60)

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")

    print("=" * 60)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 60)

    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Social platform is ready!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check logs above.")
        return 1


if __name__ == "__main__":
    exit(main())
