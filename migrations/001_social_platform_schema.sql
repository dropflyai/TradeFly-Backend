-- TradeFly Social Platform Database Schema
-- Phase 1: Core Social Features
-- Generated: 2025-12-15

-- =====================================================
-- USERS & PROFILES
-- =====================================================

CREATE TABLE IF NOT EXISTS users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    display_name VARCHAR(100),
    bio TEXT,
    avatar_url TEXT,

    -- Trading profile
    experience_level VARCHAR(20) DEFAULT 'beginner', -- beginner, intermediate, advanced, professional
    preferred_strategies TEXT[], -- Array of strategy names: ['scalping', 'momentum', 'volume_spike']
    specialization_tags TEXT[], -- ['Options Scalper', 'Momentum Trader', 'Flow Trader', 'Greeks Expert']

    -- Reputation & verification
    reputation_score INTEGER DEFAULT 0,
    verified BOOLEAN DEFAULT FALSE,
    verified_performance BOOLEAN DEFAULT FALSE, -- Broker-verified track record
    broker_connected BOOLEAN DEFAULT FALSE,

    -- Stats
    followers_count INTEGER DEFAULT 0,
    following_count INTEGER DEFAULT 0,
    posts_count INTEGER DEFAULT 0,

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_seen_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for user queries
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_reputation ON users(reputation_score DESC);
CREATE INDEX IF NOT EXISTS idx_users_verified ON users(verified) WHERE verified = TRUE;

-- =====================================================
-- SOCIAL GRAPH (FOLLOWS/FOLLOWERS)
-- =====================================================

CREATE TABLE IF NOT EXISTS follows (
    follower_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    following_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (follower_id, following_id),
    CHECK (follower_id != following_id) -- Can't follow yourself
);

-- Indexes for follow queries
CREATE INDEX IF NOT EXISTS idx_follows_follower ON follows(follower_id);
CREATE INDEX IF NOT EXISTS idx_follows_following ON follows(following_id);

-- =====================================================
-- POSTS/MESSAGES
-- =====================================================

CREATE TABLE IF NOT EXISTS posts (
    post_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    author_id UUID REFERENCES users(user_id) ON DELETE CASCADE NOT NULL,

    -- Content
    content TEXT NOT NULL CHECK (char_length(content) <= 5000), -- 5000 char limit
    media_urls TEXT[], -- Charts, images, videos

    -- Signal/Contract linking
    signal_id UUID, -- Link to options_signals table
    contract_symbol VARCHAR(50), -- e.g., 'AAPL_150C_12/15'
    underlying_symbol VARCHAR(10), -- e.g., 'AAPL'

    -- Trading metadata
    sentiment VARCHAR(20), -- 'bullish_call', 'bearish_put', 'neutral'
    strategy VARCHAR(50), -- 'scalping', 'momentum', 'volume_spike', etc.

    -- Signal data (embedded for performance)
    signal_data JSONB, -- Full signal details if linked

    -- Post type
    post_type VARCHAR(20) DEFAULT 'standard', -- 'standard', 'signal', 'trade_result', 'education'

    -- Engagement counters (denormalized for performance)
    likes_count INTEGER DEFAULT 0,
    replies_count INTEGER DEFAULT 0,
    reposts_count INTEGER DEFAULT 0,

    -- Room association
    room_id UUID, -- NULL for public feed, UUID for room-specific

    -- Moderation
    is_hidden BOOLEAN DEFAULT FALSE,
    moderation_status VARCHAR(20) DEFAULT 'approved', -- 'approved', 'flagged', 'removed'

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    edited_at TIMESTAMP
);

-- Indexes for post queries
CREATE INDEX IF NOT EXISTS idx_posts_author ON posts(author_id);
CREATE INDEX IF NOT EXISTS idx_posts_created ON posts(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_posts_contract ON posts(contract_symbol) WHERE contract_symbol IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_posts_underlying ON posts(underlying_symbol) WHERE underlying_symbol IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_posts_strategy ON posts(strategy) WHERE strategy IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_posts_room ON posts(room_id) WHERE room_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_posts_signal ON posts(signal_id) WHERE signal_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_posts_sentiment ON posts(sentiment) WHERE sentiment IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_posts_signal_data ON posts USING GIN (signal_data); -- JSONB index

-- =====================================================
-- POST ENGAGEMENT (LIKES, REPLIES, REPOSTS)
-- =====================================================

CREATE TABLE IF NOT EXISTS post_likes (
    post_id UUID REFERENCES posts(post_id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (post_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_post_likes_user ON post_likes(user_id);
CREATE INDEX IF NOT EXISTS idx_post_likes_post ON post_likes(post_id);

CREATE TABLE IF NOT EXISTS post_replies (
    reply_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    post_id UUID REFERENCES posts(post_id) ON DELETE CASCADE NOT NULL,
    author_id UUID REFERENCES users(user_id) ON DELETE CASCADE NOT NULL,
    content TEXT NOT NULL CHECK (char_length(content) <= 2000), -- Replies shorter than posts

    -- Nested replies
    parent_reply_id UUID REFERENCES post_replies(reply_id) ON DELETE CASCADE,

    -- Engagement
    likes_count INTEGER DEFAULT 0,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_post_replies_post ON post_replies(post_id);
CREATE INDEX IF NOT EXISTS idx_post_replies_author ON post_replies(author_id);
CREATE INDEX IF NOT EXISTS idx_post_replies_parent ON post_replies(parent_reply_id) WHERE parent_reply_id IS NOT NULL;

CREATE TABLE IF NOT EXISTS reply_likes (
    reply_id UUID REFERENCES post_replies(reply_id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (reply_id, user_id)
);

CREATE TABLE IF NOT EXISTS post_reposts (
    repost_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    original_post_id UUID REFERENCES posts(post_id) ON DELETE CASCADE NOT NULL,
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE NOT NULL,
    comment TEXT, -- Optional comment when reposting
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(original_post_id, user_id) -- Can't repost same post twice
);

CREATE INDEX IF NOT EXISTS idx_post_reposts_user ON post_reposts(user_id);
CREATE INDEX IF NOT EXISTS idx_post_reposts_original ON post_reposts(original_post_id);

-- =====================================================
-- WATCHLISTS
-- =====================================================

CREATE TABLE IF NOT EXISTS user_watchlists (
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    contract_symbol VARCHAR(50) NOT NULL, -- e.g., 'AAPL_150C_12/15'
    underlying_symbol VARCHAR(10) NOT NULL, -- e.g., 'AAPL'

    -- Alert settings
    alert_enabled BOOLEAN DEFAULT TRUE,
    alert_confidence_threshold DECIMAL(3, 2) DEFAULT 0.75, -- Alert when signal confidence >= 0.75

    added_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (user_id, contract_symbol)
);

CREATE INDEX IF NOT EXISTS idx_watchlists_user ON user_watchlists(user_id);
CREATE INDEX IF NOT EXISTS idx_watchlists_symbol ON user_watchlists(contract_symbol);
CREATE INDEX IF NOT EXISTS idx_watchlists_underlying ON user_watchlists(underlying_symbol);

-- =====================================================
-- ROOMS (STRATEGY-BASED COMMUNITIES)
-- =====================================================

CREATE TABLE IF NOT EXISTS rooms (
    room_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    description TEXT,

    -- Room type
    room_type VARCHAR(20) DEFAULT 'free', -- 'free', 'premium'
    price_monthly DECIMAL(10, 2) DEFAULT 0, -- For premium rooms

    -- Focus
    strategy_focus VARCHAR(50), -- 'scalping', 'momentum', 'volume_spike', 'advanced', 'all'

    -- Owner
    owner_id UUID REFERENCES users(user_id) ON DELETE CASCADE NOT NULL,

    -- Stats
    members_count INTEGER DEFAULT 0,
    posts_count INTEGER DEFAULT 0,

    -- Settings
    is_public BOOLEAN DEFAULT TRUE,
    requires_approval BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_rooms_owner ON rooms(owner_id);
CREATE INDEX IF NOT EXISTS idx_rooms_type ON rooms(room_type);
CREATE INDEX IF NOT EXISTS idx_rooms_strategy ON rooms(strategy_focus) WHERE strategy_focus IS NOT NULL;

CREATE TABLE IF NOT EXISTS room_members (
    room_id UUID REFERENCES rooms(room_id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,

    role VARCHAR(20) DEFAULT 'member', -- 'owner', 'moderator', 'member'

    -- Subscription for premium rooms
    subscription_status VARCHAR(20) DEFAULT 'active', -- 'active', 'expired', 'cancelled'
    subscription_expires_at TIMESTAMP,
    subscription_auto_renew BOOLEAN DEFAULT TRUE,

    joined_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (room_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_room_members_user ON room_members(user_id);
CREATE INDEX IF NOT EXISTS idx_room_members_room ON room_members(room_id);
CREATE INDEX IF NOT EXISTS idx_room_members_role ON room_members(role);

-- =====================================================
-- USER PERFORMANCE TRACKING
-- =====================================================

CREATE TABLE IF NOT EXISTS user_performance (
    performance_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE NOT NULL,
    date DATE NOT NULL,

    -- Daily stats
    trades_count INTEGER DEFAULT 0,
    wins INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,
    breakeven INTEGER DEFAULT 0,

    -- P&L
    total_pnl DECIMAL(15, 2) DEFAULT 0,
    total_return_pct DECIMAL(10, 4), -- Percentage return

    -- Calculated metrics
    win_rate DECIMAL(5, 2), -- Percentage
    avg_win DECIMAL(15, 2),
    avg_loss DECIMAL(15, 2),
    avg_risk_reward DECIMAL(5, 2),

    -- Strategy breakdown
    strategy_stats JSONB, -- {"scalping": {"trades": 5, "pnl": 250.00}, ...}

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, date)
);

CREATE INDEX IF NOT EXISTS idx_user_performance_user ON user_performance(user_id);
CREATE INDEX IF NOT EXISTS idx_user_performance_date ON user_performance(date DESC);

-- =====================================================
-- NOTIFICATIONS
-- =====================================================

CREATE TABLE IF NOT EXISTS notifications (
    notification_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE NOT NULL,

    -- Notification type
    type VARCHAR(50) NOT NULL, -- 'signal', 'follow', 'like', 'reply', 'repost', 'mention', 'room_invite'

    -- Content
    title VARCHAR(255) NOT NULL,
    message TEXT,

    -- Links
    link_url TEXT, -- URL to navigate to when clicked
    related_post_id UUID REFERENCES posts(post_id) ON DELETE CASCADE,
    related_user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,

    -- Metadata
    metadata JSONB,

    -- Status
    is_read BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_unread ON notifications(user_id, is_read) WHERE is_read = FALSE;
CREATE INDEX IF NOT EXISTS idx_notifications_created ON notifications(created_at DESC);

-- =====================================================
-- CONTENT MODERATION
-- =====================================================

CREATE TABLE IF NOT EXISTS moderation_reports (
    report_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- What's being reported
    post_id UUID REFERENCES posts(post_id) ON DELETE CASCADE,
    reply_id UUID REFERENCES post_replies(reply_id) ON DELETE CASCADE,
    reported_user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,

    -- Who reported
    reporter_id UUID REFERENCES users(user_id) ON DELETE CASCADE NOT NULL,

    -- Details
    reason VARCHAR(50) NOT NULL, -- 'spam', 'abuse', 'misinformation', 'pump_dump', 'other'
    description TEXT,

    -- Status
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'reviewed', 'action_taken', 'dismissed'
    moderator_notes TEXT,

    created_at TIMESTAMP DEFAULT NOW(),
    reviewed_at TIMESTAMP,

    CHECK (post_id IS NOT NULL OR reply_id IS NOT NULL OR reported_user_id IS NOT NULL) -- At least one must be set
);

CREATE INDEX IF NOT EXISTS idx_moderation_reports_status ON moderation_reports(status);
CREATE INDEX IF NOT EXISTS idx_moderation_reports_post ON moderation_reports(post_id) WHERE post_id IS NOT NULL;

-- =====================================================
-- TRIGGERS FOR COUNTER UPDATES
-- =====================================================

-- Update followers_count when follows added/removed
CREATE OR REPLACE FUNCTION update_followers_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE users SET followers_count = followers_count + 1 WHERE user_id = NEW.following_id;
        UPDATE users SET following_count = following_count + 1 WHERE user_id = NEW.follower_id;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE users SET followers_count = followers_count - 1 WHERE user_id = OLD.following_id;
        UPDATE users SET following_count = following_count - 1 WHERE user_id = OLD.follower_id;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_followers_count
AFTER INSERT OR DELETE ON follows
FOR EACH ROW EXECUTE FUNCTION update_followers_count();

-- Update likes_count on posts
CREATE OR REPLACE FUNCTION update_post_likes_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE posts SET likes_count = likes_count + 1 WHERE post_id = NEW.post_id;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE posts SET likes_count = likes_count - 1 WHERE post_id = OLD.post_id;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_post_likes_count
AFTER INSERT OR DELETE ON post_likes
FOR EACH ROW EXECUTE FUNCTION update_post_likes_count();

-- Update replies_count on posts
CREATE OR REPLACE FUNCTION update_post_replies_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE posts SET replies_count = replies_count + 1 WHERE post_id = NEW.post_id;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE posts SET replies_count = replies_count - 1 WHERE post_id = OLD.post_id;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_post_replies_count
AFTER INSERT OR DELETE ON post_replies
FOR EACH ROW EXECUTE FUNCTION update_post_replies_count();

-- Update reposts_count on posts
CREATE OR REPLACE FUNCTION update_post_reposts_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE posts SET reposts_count = reposts_count + 1 WHERE post_id = NEW.original_post_id;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE posts SET reposts_count = reposts_count - 1 WHERE post_id = OLD.original_post_id;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_post_reposts_count
AFTER INSERT OR DELETE ON post_reposts
FOR EACH ROW EXECUTE FUNCTION update_post_reposts_count();

-- Update posts_count on users
CREATE OR REPLACE FUNCTION update_user_posts_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE users SET posts_count = posts_count + 1 WHERE user_id = NEW.author_id;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE users SET posts_count = posts_count - 1 WHERE user_id = OLD.author_id;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_user_posts_count
AFTER INSERT OR DELETE ON posts
FOR EACH ROW EXECUTE FUNCTION update_user_posts_count();

-- Update room members_count
CREATE OR REPLACE FUNCTION update_room_members_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE rooms SET members_count = members_count + 1 WHERE room_id = NEW.room_id;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE rooms SET members_count = members_count - 1 WHERE room_id = OLD.room_id;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_room_members_count
AFTER INSERT OR DELETE ON room_members
FOR EACH ROW EXECUTE FUNCTION update_room_members_count();

-- =====================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- =====================================================

-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE post_likes ENABLE ROW LEVEL SECURITY;
ALTER TABLE post_replies ENABLE ROW LEVEL SECURITY;
ALTER TABLE follows ENABLE ROW LEVEL SECURITY;
ALTER TABLE rooms ENABLE ROW LEVEL SECURITY;
ALTER TABLE room_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;

-- Users can read all public profiles
CREATE POLICY "Users are viewable by everyone" ON users
    FOR SELECT USING (true);

-- Users can update their own profile
CREATE POLICY "Users can update own profile" ON users
    FOR UPDATE USING (auth.uid() = user_id);

-- Posts are viewable by everyone
CREATE POLICY "Posts are viewable by everyone" ON posts
    FOR SELECT USING (NOT is_hidden);

-- Users can create posts
CREATE POLICY "Users can create posts" ON posts
    FOR INSERT WITH CHECK (auth.uid() = author_id);

-- Users can update their own posts
CREATE POLICY "Users can update own posts" ON posts
    FOR UPDATE USING (auth.uid() = author_id);

-- Users can delete their own posts
CREATE POLICY "Users can delete own posts" ON posts
    FOR DELETE USING (auth.uid() = author_id);

-- Anyone can read follows
CREATE POLICY "Follows are viewable by everyone" ON follows
    FOR SELECT USING (true);

-- Users can follow/unfollow
CREATE POLICY "Users can manage own follows" ON follows
    FOR ALL USING (auth.uid() = follower_id);

-- =====================================================
-- SEED DATA: DEFAULT ROOMS
-- =====================================================

-- Create system user for default rooms
INSERT INTO users (user_id, username, email, display_name, bio, verified, reputation_score)
VALUES (
    '00000000-0000-0000-0000-000000000000',
    'tradefly_system',
    'system@tradeflyai.com',
    'TradeFly System',
    'Official TradeFly system account',
    TRUE,
    1000
) ON CONFLICT (user_id) DO NOTHING;

-- Create default free rooms
INSERT INTO rooms (room_id, name, description, room_type, strategy_focus, owner_id, is_public)
VALUES
    (
        '11111111-1111-1111-1111-111111111111',
        '⚡ Scalpers Lounge',
        'Fast 1-5 minute options plays. Quick in, quick out. Share your scalping setups and signals.',
        'free',
        'scalping',
        '00000000-0000-0000-0000-000000000000',
        TRUE
    ),
    (
        '22222222-2222-2222-2222-222222222222',
        '🚀 Momentum Traders',
        'Ride the wave. 15min-2hr directional plays on breakouts. Share momentum setups and technical analysis.',
        'free',
        'momentum',
        '00000000-0000-0000-0000-000000000000',
        TRUE
    ),
    (
        '33333333-3333-3333-3333-333333333333',
        '🐋 Flow Followers',
        'Track smart money. Unusual options activity & institutional flow. Share large block trades and dark pool activity.',
        'free',
        'volume_spike',
        '00000000-0000-0000-0000-000000000000',
        TRUE
    ),
    (
        '44444444-4444-4444-4444-444444444444',
        '📊 General Discussion',
        'General options trading discussion. Strategy questions, market analysis, learning resources.',
        'free',
        'all',
        '00000000-0000-0000-0000-000000000000',
        TRUE
    )
ON CONFLICT (room_id) DO NOTHING;

-- =====================================================
-- VIEWS FOR COMMON QUERIES
-- =====================================================

-- View: User feed (posts from followed users + own posts)
CREATE OR REPLACE VIEW user_feed AS
SELECT
    p.*,
    u.username AS author_username,
    u.display_name AS author_display_name,
    u.avatar_url AS author_avatar_url,
    u.verified AS author_verified,
    u.reputation_score AS author_reputation
FROM posts p
JOIN users u ON p.author_id = u.user_id
WHERE NOT p.is_hidden
ORDER BY p.created_at DESC;

-- View: Trending contracts (most discussed in last 24 hours)
CREATE OR REPLACE VIEW trending_contracts AS
SELECT
    contract_symbol,
    underlying_symbol,
    COUNT(*) AS mentions_count,
    COUNT(DISTINCT author_id) AS unique_authors,
    MAX(created_at) AS last_mentioned
FROM posts
WHERE
    contract_symbol IS NOT NULL
    AND created_at >= NOW() - INTERVAL '24 hours'
    AND NOT is_hidden
GROUP BY contract_symbol, underlying_symbol
ORDER BY mentions_count DESC, unique_authors DESC
LIMIT 50;

-- View: User leaderboard by reputation
CREATE OR REPLACE VIEW user_leaderboard AS
SELECT
    user_id,
    username,
    display_name,
    avatar_url,
    reputation_score,
    followers_count,
    posts_count,
    verified,
    verified_performance,
    preferred_strategies,
    specialization_tags
FROM users
WHERE reputation_score > 0
ORDER BY reputation_score DESC, followers_count DESC
LIMIT 100;

-- =====================================================
-- COMMENTS
-- =====================================================

COMMENT ON TABLE users IS 'User profiles and trading preferences';
COMMENT ON TABLE posts IS 'Social posts including signals, trade results, and discussions';
COMMENT ON TABLE follows IS 'Social graph: who follows whom';
COMMENT ON TABLE rooms IS 'Strategy-based community rooms';
COMMENT ON TABLE user_performance IS 'Verified trading performance metrics';
COMMENT ON TABLE notifications IS 'User notifications for signals, engagement, etc.';
COMMENT ON TABLE moderation_reports IS 'Content moderation and user reports';

-- Schema version
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    description TEXT,
    applied_at TIMESTAMP DEFAULT NOW()
);

INSERT INTO schema_version (version, description)
VALUES (1, 'Initial social platform schema - users, posts, rooms, engagement')
ON CONFLICT (version) DO NOTHING;
