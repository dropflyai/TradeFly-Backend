-- Add asset_type column to trading_signals table
-- This allows us to separate stock signals from crypto signals

-- Add the column with default value
ALTER TABLE trading_signals 
ADD COLUMN IF NOT EXISTS asset_type TEXT DEFAULT 'stock';

-- Update existing rows: if ticker contains '-USD', it's crypto, otherwise stock
UPDATE trading_signals
SET asset_type = CASE 
  WHEN ticker LIKE '%-USD' THEN 'crypto'
  ELSE 'stock'
END
WHERE asset_type IS NULL OR asset_type = 'stock';

-- Make the column NOT NULL after backfilling
ALTER TABLE trading_signals 
ALTER COLUMN asset_type SET NOT NULL;

-- Add check constraint to ensure only valid values
ALTER TABLE trading_signals
ADD CONSTRAINT asset_type_check CHECK (asset_type IN ('stock', 'crypto'));

-- Create index for faster filtering by asset_type
CREATE INDEX IF NOT EXISTS idx_trading_signals_asset_type ON trading_signals(asset_type);

-- Create composite index for common query: active signals filtered by asset type
CREATE INDEX IF NOT EXISTS idx_trading_signals_active_asset_type 
ON trading_signals(is_active, asset_type, created_at DESC);

