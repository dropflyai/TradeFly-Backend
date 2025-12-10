-- TradeFly AI Database Schema
-- Run this in Supabase SQL Editor: https://supabase.com/dashboard/project/YOUR_PROJECT/sql

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Market Movers Table (stores top gainers/losers/actives)
CREATE TABLE IF NOT EXISTS market_movers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol VARCHAR(10) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    change_percent DECIMAL(8, 4) NOT NULL,
    volume BIGINT NOT NULL,
    category VARCHAR(20) NOT NULL, -- 'gainer', 'loser', 'active'
    scanned_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create indexes for fast queries
CREATE INDEX IF NOT EXISTS idx_market_movers_symbol ON market_movers(symbol);
CREATE INDEX IF NOT EXISTS idx_market_movers_scanned_at ON market_movers(scanned_at DESC);
CREATE INDEX IF NOT EXISTS idx_market_movers_category ON market_movers(category);

-- Options Signals Table (stores all detected signals)
CREATE TABLE IF NOT EXISTS options_signals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    signal_id VARCHAR(100) UNIQUE NOT NULL,
    symbol VARCHAR(10) NOT NULL,
    strategy VARCHAR(50) NOT NULL, -- 'SCALPING', 'SWING', etc.
    action VARCHAR(20) NOT NULL, -- 'BUY_CALL', 'BUY_PUT'

    -- Contract details
    strike DECIMAL(10, 2) NOT NULL,
    expiration DATE NOT NULL,
    option_type VARCHAR(10) NOT NULL, -- 'call', 'put'
    days_to_expiry INTEGER NOT NULL,

    -- Pricing
    entry_price DECIMAL(10, 2) NOT NULL,
    target_price DECIMAL(10, 2) NOT NULL,
    stop_loss DECIMAL(10, 2) NOT NULL,

    -- Signal quality
    confidence DECIMAL(5, 4) NOT NULL,

    -- Greeks
    delta DECIMAL(8, 6),
    gamma DECIMAL(8, 6),
    theta DECIMAL(8, 6),
    vega DECIMAL(8, 6),

    -- Underlying
    underlying_price DECIMAL(10, 2),

    -- Volume metrics
    volume INTEGER,
    open_interest INTEGER,

    -- Full contract data (JSONB for flexibility)
    contract_data JSONB NOT NULL,

    -- Metadata
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ, -- When signal is no longer valid
    is_active BOOLEAN DEFAULT TRUE
);

-- Create indexes for fast queries
CREATE INDEX IF NOT EXISTS idx_signals_symbol ON options_signals(symbol);
CREATE INDEX IF NOT EXISTS idx_signals_strategy ON options_signals(strategy);
CREATE INDEX IF NOT EXISTS idx_signals_created_at ON options_signals(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_signals_confidence ON options_signals(confidence DESC);
CREATE INDEX IF NOT EXISTS idx_signals_is_active ON options_signals(is_active);
CREATE INDEX IF NOT EXISTS idx_signals_expiration ON options_signals(expiration);

-- Paper Trading Positions Table
CREATE TABLE IF NOT EXISTS paper_positions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    signal_id VARCHAR(100) REFERENCES options_signals(signal_id),
    symbol VARCHAR(10) NOT NULL,

    -- Position details
    entry_price DECIMAL(10, 2) NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    position_type VARCHAR(10) NOT NULL, -- 'call', 'put'

    -- Current status
    current_price DECIMAL(10, 2),
    profit_loss DECIMAL(10, 2),
    profit_loss_percent DECIMAL(8, 4),

    -- Timestamps
    opened_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    closed_at TIMESTAMPTZ,

    -- Status
    status VARCHAR(20) DEFAULT 'open', -- 'open', 'closed', 'expired'

    -- Full position data
    position_data JSONB NOT NULL
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_paper_positions_symbol ON paper_positions(symbol);
CREATE INDEX IF NOT EXISTS idx_paper_positions_status ON paper_positions(status);
CREATE INDEX IF NOT EXISTS idx_paper_positions_opened_at ON paper_positions(opened_at DESC);

-- Scanner Cache Table (stores scanner results to avoid re-scanning)
CREATE TABLE IF NOT EXISTS scanner_cache (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cache_key VARCHAR(255) UNIQUE NOT NULL,
    cache_data JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL
);

-- Create index for cache lookups
CREATE INDEX IF NOT EXISTS idx_scanner_cache_key ON scanner_cache(cache_key);
CREATE INDEX IF NOT EXISTS idx_scanner_cache_expires_at ON scanner_cache(expires_at);

-- View: Active Signals (signals that haven't expired)
CREATE OR REPLACE VIEW active_signals AS
SELECT *
FROM options_signals
WHERE is_active = TRUE
  AND (expires_at IS NULL OR expires_at > NOW())
ORDER BY created_at DESC;

-- View: Latest Market Movers (last scan)
CREATE OR REPLACE VIEW latest_market_movers AS
SELECT DISTINCT ON (symbol) *
FROM market_movers
ORDER BY symbol, scanned_at DESC;

-- View: Paper Trading Stats
CREATE OR REPLACE VIEW paper_trading_stats AS
SELECT
    COUNT(*) FILTER (WHERE status = 'open') as open_positions,
    COUNT(*) FILTER (WHERE status = 'closed') as closed_positions,
    AVG(profit_loss_percent) FILTER (WHERE status = 'closed') as avg_return,
    SUM(profit_loss) FILTER (WHERE status = 'closed') as total_profit_loss,
    COUNT(*) FILTER (WHERE status = 'closed' AND profit_loss > 0) * 100.0 / NULLIF(COUNT(*) FILTER (WHERE status = 'closed'), 0) as win_rate
FROM paper_positions;

-- Function to clean up old data (run daily)
CREATE OR REPLACE FUNCTION cleanup_old_data()
RETURNS void AS $$
BEGIN
    -- Delete signals older than 7 days
    DELETE FROM options_signals
    WHERE created_at < NOW() - INTERVAL '7 days';

    -- Delete market movers older than 1 day
    DELETE FROM market_movers
    WHERE scanned_at < NOW() - INTERVAL '1 day';

    -- Delete expired cache entries
    DELETE FROM scanner_cache
    WHERE expires_at < NOW();

    -- Delete closed paper positions older than 30 days
    DELETE FROM paper_positions
    WHERE status = 'closed' AND closed_at < NOW() - INTERVAL '30 days';
END;
$$ LANGUAGE plpgsql;

-- Enable Row Level Security (RLS)
ALTER TABLE market_movers ENABLE ROW LEVEL SECURITY;
ALTER TABLE options_signals ENABLE ROW LEVEL SECURITY;
ALTER TABLE paper_positions ENABLE ROW LEVEL SECURITY;
ALTER TABLE scanner_cache ENABLE ROW LEVEL SECURITY;

-- Create policies (allow public read access for now)
CREATE POLICY "Allow public read access" ON market_movers FOR SELECT USING (true);
CREATE POLICY "Allow public read access" ON options_signals FOR SELECT USING (true);
CREATE POLICY "Allow public read access" ON paper_positions FOR SELECT USING (true);
CREATE POLICY "Allow public read access" ON scanner_cache FOR SELECT USING (true);

-- Grant permissions (for service role to write)
GRANT ALL ON market_movers TO service_role;
GRANT ALL ON options_signals TO service_role;
GRANT ALL ON paper_positions TO service_role;
GRANT ALL ON scanner_cache TO service_role;

-- Success message
SELECT 'TradeFly database schema created successfully!' AS status;
