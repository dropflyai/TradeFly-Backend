-- =====================================================
-- TradeFly Database Migration: Add News Columns
-- =====================================================
-- Run this in your Supabase SQL Editor
-- Adds columns to store news context with trading signals

-- Add related_news column (stock-specific news)
ALTER TABLE trading_signals
ADD COLUMN IF NOT EXISTS related_news JSONB DEFAULT '[]'::jsonb;

-- Add market_news column (market-wide news)
ALTER TABLE trading_signals
ADD COLUMN IF NOT EXISTS market_news JSONB DEFAULT '[]'::jsonb;

-- Add comments for documentation
COMMENT ON COLUMN trading_signals.related_news IS 'Stock-specific news that influenced this signal (earnings, FDA, analyst upgrades, etc.)';
COMMENT ON COLUMN trading_signals.market_news IS 'Market-wide news at time of signal (Fed announcements, CPI, GDP, etc.)';

-- Create index for querying signals with news
CREATE INDEX IF NOT EXISTS idx_signals_with_news
ON trading_signals(ticker, created_at)
WHERE jsonb_array_length(related_news) > 0;

-- Verify migration
SELECT column_name, data_type, column_default
FROM information_schema.columns
WHERE table_name = 'trading_signals'
AND column_name IN ('related_news', 'market_news');

-- Sample query to test
-- SELECT ticker, signal_type, quality, related_news, market_news
-- FROM trading_signals
-- WHERE created_at > NOW() - INTERVAL '1 day'
-- ORDER BY created_at DESC
-- LIMIT 5;
