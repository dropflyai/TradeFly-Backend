"""
Pydantic Models for TradeFly Social Platform
Defines data structures for users, posts, rooms, engagement, and social features
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, EmailStr, validator
from enum import Enum


# =====================================================
# ENUMS
# =====================================================

class ExperienceLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    PROFESSIONAL = "professional"


class Sentiment(str, Enum):
    BULLISH_CALL = "bullish_call"
    BEARISH_PUT = "bearish_put"
    NEUTRAL = "neutral"


class PostType(str, Enum):
    STANDARD = "standard"
    SIGNAL = "signal"
    TRADE_RESULT = "trade_result"
    EDUCATION = "education"


class RoomType(str, Enum):
    FREE = "free"
    PREMIUM = "premium"


class MemberRole(str, Enum):
    OWNER = "owner"
    MODERATOR = "moderator"
    MEMBER = "member"


class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class ModerationStatus(str, Enum):
    APPROVED = "approved"
    FLAGGED = "flagged"
    REMOVED = "removed"


class ReportReason(str, Enum):
    SPAM = "spam"
    ABUSE = "abuse"
    MISINFORMATION = "misinformation"
    PUMP_DUMP = "pump_dump"
    OTHER = "other"


class NotificationType(str, Enum):
    SIGNAL = "signal"
    FOLLOW = "follow"
    LIKE = "like"
    REPLY = "reply"
    REPOST = "repost"
    MENTION = "mention"
    ROOM_INVITE = "room_invite"
    TRADE_ALERT = "trade_alert"


# =====================================================
# USER MODELS
# =====================================================

class UserBase(BaseModel):
    """Base user model"""
    username: str = Field(..., min_length=3, max_length=50, pattern=r'^[a-zA-Z0-9_]+$')
    email: EmailStr
    display_name: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = None
    experience_level: ExperienceLevel = ExperienceLevel.BEGINNER
    preferred_strategies: List[str] = Field(default_factory=list)
    specialization_tags: List[str] = Field(default_factory=list)


class UserCreate(UserBase):
    """User creation model"""
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """User update model"""
    display_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    experience_level: Optional[ExperienceLevel] = None
    preferred_strategies: Optional[List[str]] = None
    specialization_tags: Optional[str] = None


class UserProfile(UserBase):
    """Public user profile"""
    user_id: UUID
    reputation_score: int = 0
    verified: bool = False
    verified_performance: bool = False
    followers_count: int = 0
    following_count: int = 0
    posts_count: int = 0
    created_at: datetime
    last_seen_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserStats(BaseModel):
    """User trading statistics"""
    user_id: UUID
    total_trades: int = 0
    win_rate: Optional[float] = None
    total_pnl: Optional[float] = None
    avg_risk_reward: Optional[float] = None
    best_strategy: Optional[str] = None


# =====================================================
# POST MODELS
# =====================================================

class PostBase(BaseModel):
    """Base post model"""
    content: str = Field(..., min_length=1, max_length=5000)
    media_urls: List[str] = Field(default_factory=list)
    contract_symbol: Optional[str] = None
    underlying_symbol: Optional[str] = None
    sentiment: Optional[Sentiment] = None
    strategy: Optional[str] = None
    post_type: PostType = PostType.STANDARD
    room_id: Optional[UUID] = None


class PostCreate(PostBase):
    """Post creation model"""
    signal_id: Optional[UUID] = None
    signal_data: Optional[Dict[str, Any]] = None


class PostUpdate(BaseModel):
    """Post update model (within 5 minutes of creation)"""
    content: Optional[str] = Field(None, min_length=1, max_length=5000)
    media_urls: Optional[List[str]] = None


class Post(PostBase):
    """Full post model"""
    post_id: UUID
    author_id: UUID
    signal_id: Optional[UUID] = None
    signal_data: Optional[Dict[str, Any]] = None
    likes_count: int = 0
    replies_count: int = 0
    reposts_count: int = 0
    is_hidden: bool = False
    moderation_status: ModerationStatus = ModerationStatus.APPROVED
    created_at: datetime
    updated_at: datetime
    edited_at: Optional[datetime] = None

    # Populated from join
    author_username: Optional[str] = None
    author_display_name: Optional[str] = None
    author_avatar_url: Optional[str] = None
    author_verified: Optional[bool] = None
    author_reputation: Optional[int] = None

    class Config:
        from_attributes = True


class PostWithEngagement(Post):
    """Post with engagement info for current user"""
    liked_by_user: bool = False
    reposted_by_user: bool = False


# =====================================================
# ENGAGEMENT MODELS
# =====================================================

class LikeCreate(BaseModel):
    """Like a post"""
    post_id: UUID


class ReplyCreate(BaseModel):
    """Create a reply"""
    post_id: UUID
    content: str = Field(..., min_length=1, max_length=2000)
    parent_reply_id: Optional[UUID] = None


class Reply(BaseModel):
    """Reply model"""
    reply_id: UUID
    post_id: UUID
    author_id: UUID
    content: str
    parent_reply_id: Optional[UUID] = None
    likes_count: int = 0
    created_at: datetime
    updated_at: datetime

    # Populated from join
    author_username: Optional[str] = None
    author_display_name: Optional[str] = None
    author_avatar_url: Optional[str] = None

    class Config:
        from_attributes = True


class RepostCreate(BaseModel):
    """Repost a post"""
    original_post_id: UUID
    comment: Optional[str] = Field(None, max_length=500)


class Repost(BaseModel):
    """Repost model"""
    repost_id: UUID
    original_post_id: UUID
    user_id: UUID
    comment: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# =====================================================
# FOLLOW MODELS
# =====================================================

class FollowCreate(BaseModel):
    """Follow a user"""
    following_id: UUID


class Follow(BaseModel):
    """Follow relationship"""
    follower_id: UUID
    following_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# =====================================================
# WATCHLIST MODELS
# =====================================================

class WatchlistCreate(BaseModel):
    """Add contract to watchlist"""
    contract_symbol: str = Field(..., min_length=1)
    underlying_symbol: str = Field(..., min_length=1)
    alert_enabled: bool = True
    alert_confidence_threshold: float = Field(default=0.75, ge=0.0, le=1.0)


class WatchlistItem(WatchlistCreate):
    """Watchlist item"""
    user_id: UUID
    added_at: datetime

    class Config:
        from_attributes = True


# =====================================================
# ROOM MODELS
# =====================================================

class RoomBase(BaseModel):
    """Base room model"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    room_type: RoomType = RoomType.FREE
    price_monthly: float = Field(default=0, ge=0)
    strategy_focus: Optional[str] = None
    is_public: bool = True
    requires_approval: bool = False


class RoomCreate(RoomBase):
    """Room creation model"""
    pass


class RoomUpdate(BaseModel):
    """Room update model"""
    name: Optional[str] = None
    description: Optional[str] = None
    price_monthly: Optional[float] = None
    is_public: Optional[bool] = None
    requires_approval: Optional[bool] = None


class Room(RoomBase):
    """Full room model"""
    room_id: UUID
    owner_id: UUID
    members_count: int = 0
    posts_count: int = 0
    created_at: datetime
    updated_at: datetime

    # Populated from join
    owner_username: Optional[str] = None
    owner_display_name: Optional[str] = None
    is_member: Optional[bool] = None
    member_role: Optional[MemberRole] = None

    class Config:
        from_attributes = True


class RoomMemberCreate(BaseModel):
    """Join a room"""
    room_id: UUID


class RoomMember(BaseModel):
    """Room member model"""
    room_id: UUID
    user_id: UUID
    role: MemberRole = MemberRole.MEMBER
    subscription_status: SubscriptionStatus = SubscriptionStatus.ACTIVE
    subscription_expires_at: Optional[datetime] = None
    subscription_auto_renew: bool = True
    joined_at: datetime

    class Config:
        from_attributes = True


# =====================================================
# PERFORMANCE MODELS
# =====================================================

class PerformanceCreate(BaseModel):
    """Create daily performance record"""
    date: datetime
    trades_count: int = 0
    wins: int = 0
    losses: int = 0
    breakeven: int = 0
    total_pnl: float = 0
    total_return_pct: Optional[float] = None
    win_rate: Optional[float] = None
    avg_win: Optional[float] = None
    avg_loss: Optional[float] = None
    avg_risk_reward: Optional[float] = None
    strategy_stats: Optional[Dict[str, Any]] = None


class Performance(PerformanceCreate):
    """Performance record"""
    performance_id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =====================================================
# NOTIFICATION MODELS
# =====================================================

class NotificationCreate(BaseModel):
    """Create notification"""
    user_id: UUID
    type: NotificationType
    title: str = Field(..., max_length=255)
    message: Optional[str] = None
    link_url: Optional[str] = None
    related_post_id: Optional[UUID] = None
    related_user_id: Optional[UUID] = None
    metadata: Optional[Dict[str, Any]] = None


class Notification(NotificationCreate):
    """Notification model"""
    notification_id: UUID
    is_read: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


# =====================================================
# MODERATION MODELS
# =====================================================

class ModerationReportCreate(BaseModel):
    """Create moderation report"""
    post_id: Optional[UUID] = None
    reply_id: Optional[UUID] = None
    reported_user_id: Optional[UUID] = None
    reason: ReportReason
    description: Optional[str] = None

    @validator('post_id', 'reply_id', 'reported_user_id')
    def at_least_one_required(cls, v, values):
        """At least one of post_id, reply_id, or reported_user_id must be set"""
        if not any([values.get('post_id'), values.get('reply_id'), v]):
            raise ValueError("At least one of post_id, reply_id, or reported_user_id must be provided")
        return v


class ModerationReport(ModerationReportCreate):
    """Moderation report model"""
    report_id: UUID
    reporter_id: UUID
    status: str = "pending"
    moderator_notes: Optional[str] = None
    created_at: datetime
    reviewed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# =====================================================
# FEED MODELS
# =====================================================

class FeedFilter(BaseModel):
    """Feed filtering options"""
    strategy: Optional[str] = None
    sentiment: Optional[Sentiment] = None
    min_confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    contract_symbol: Optional[str] = None
    underlying_symbol: Optional[str] = None
    author_id: Optional[UUID] = None
    room_id: Optional[UUID] = None
    following_only: bool = False
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class FeedResponse(BaseModel):
    """Feed response with posts"""
    posts: List[Post]
    total_count: int
    has_more: bool


# =====================================================
# TRENDING MODELS
# =====================================================

class TrendingContract(BaseModel):
    """Trending contract info"""
    contract_symbol: str
    underlying_symbol: str
    mentions_count: int
    unique_authors: int
    last_mentioned: datetime
    sentiment_bullish_pct: Optional[float] = None


class TrendingUser(BaseModel):
    """Trending user (leaderboard)"""
    user_id: UUID
    username: str
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    reputation_score: int
    followers_count: int
    posts_count: int
    verified: bool
    verified_performance: bool
    preferred_strategies: List[str] = Field(default_factory=list)
    specialization_tags: List[str] = Field(default_factory=list)


# =====================================================
# SIGNAL INTEGRATION MODELS
# =====================================================

class SignalPost(BaseModel):
    """Signal converted to social post"""
    signal_id: UUID
    content: str
    contract_symbol: str
    underlying_symbol: str
    sentiment: Sentiment
    strategy: str
    signal_data: Dict[str, Any]
    media_urls: List[str] = Field(default_factory=list)


# =====================================================
# API RESPONSE MODELS
# =====================================================

class SuccessResponse(BaseModel):
    """Generic success response"""
    success: bool = True
    message: str
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    """Generic error response"""
    success: bool = False
    error: str
    detail: Optional[str] = None


class PaginatedResponse(BaseModel):
    """Paginated response"""
    items: List[Any]
    total: int
    page: int
    page_size: int
    has_next: bool
    has_prev: bool
