#!/usr/bin/env python3
"""
Test script to verify backend is serving live, current data
"""
import requests
from datetime import datetime, timedelta
import json

BASE_URL = "http://localhost:8000"

def test_price_endpoint():
    """Test /price/{ticker} endpoint and verify data is from today"""
    print("=" * 60)
    print("TESTING LIVE PRICE DATA")
    print("=" * 60)

    ticker = "AAPL"
    response = requests.get(f"{BASE_URL}/price/{ticker}")

    if response.status_code != 200:
        print(f"❌ FAILED: Got status code {response.status_code}")
        return False

    data = response.json()
    print(f"\n✅ Successfully fetched data for {ticker}")
    print(f"Current Price: ${data['price']:.2f}")
    print(f"Timestamp: {data['timestamp']}")

    # Parse timestamp
    timestamp = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
    now = datetime.now(timestamp.tzinfo)
    age_minutes = (now - timestamp).total_seconds() / 60

    print(f"Data age: {age_minutes:.1f} minutes")

    # Verify timestamp is from today
    today = now.date()
    data_date = timestamp.date()

    if data_date == today:
        print(f"✅ VERIFIED: Data is from today ({today})")
    else:
        print(f"❌ FAILED: Data is from {data_date}, not today ({today})")
        return False

    # Verify data is relatively fresh (less than 10 minutes old during market hours)
    if age_minutes < 10:
        print(f"✅ VERIFIED: Data is fresh (under 10 minutes old)")
    else:
        print(f"⚠️  WARNING: Data is {age_minutes:.1f} minutes old (may be market closed)")

    return True

def test_candles_endpoint():
    """Test /candles/{ticker} endpoint and verify data is from today"""
    print("\n" + "=" * 60)
    print("TESTING LIVE CANDLE DATA")
    print("=" * 60)

    ticker = "AAPL"
    response = requests.get(f"{BASE_URL}/candles/{ticker}?interval=1m&limit=5")

    if response.status_code != 200:
        print(f"❌ FAILED: Got status code {response.status_code}")
        return False

    data = response.json()
    print(f"\n✅ Successfully fetched {data['candle_count']} candles for {ticker}")

    # Check most recent candle
    latest_candle = data['candles'][-1]
    print(f"\nLatest candle:")
    print(f"  Timestamp: {latest_candle['timestamp']}")
    print(f"  Open: ${latest_candle['open']:.2f}")
    print(f"  High: ${latest_candle['high']:.2f}")
    print(f"  Low: ${latest_candle['low']:.2f}")
    print(f"  Close: ${latest_candle['close']:.2f}")
    print(f"  Volume: {latest_candle['volume']:,}")

    # Parse timestamp
    timestamp_str = latest_candle['timestamp']
    # Handle different timezone formats
    if '+' in timestamp_str or '-' in timestamp_str[-6:]:
        timestamp = datetime.fromisoformat(timestamp_str)
    else:
        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))

    now = datetime.now(timestamp.tzinfo)
    age_minutes = (now - timestamp).total_seconds() / 60

    print(f"  Age: {age_minutes:.1f} minutes")

    # Verify timestamp is from today
    today = now.date()
    data_date = timestamp.date()

    if data_date == today:
        print(f"✅ VERIFIED: Candle data is from today ({today})")
    else:
        print(f"❌ FAILED: Candle data is from {data_date}, not today ({today})")
        return False

    # Show all 5 candles to verify they're sequential
    print(f"\nAll {data['candle_count']} candles:")
    for i, candle in enumerate(data['candles']):
        ts = candle['timestamp']
        print(f"  {i+1}. {ts} - Close: ${candle['close']:.2f}")

    return True

def main():
    print("\n" + "🔍 " * 20)
    print("LIVE DATA VERIFICATION TEST")
    print("Testing TradeFly Backend APIs")
    print("Current time:", datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z"))
    print("🔍 " * 20 + "\n")

    try:
        # Test health endpoint first
        response = requests.get(f"{BASE_URL}/")
        if response.status_code != 200:
            print("❌ Backend is not running!")
            return

        print("✅ Backend is online\n")

        # Run tests
        price_test = test_price_endpoint()
        candles_test = test_candles_endpoint()

        # Summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"Price endpoint: {'✅ PASS' if price_test else '❌ FAIL'}")
        print(f"Candles endpoint: {'✅ PASS' if candles_test else '❌ FAIL'}")

        if price_test and candles_test:
            print("\n🎉 ALL TESTS PASSED - DATA IS LIVE AND CURRENT! 🎉\n")
        else:
            print("\n❌ SOME TESTS FAILED - DATA MAY NOT BE LIVE\n")

    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to backend. Is it running on port 8000?")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
