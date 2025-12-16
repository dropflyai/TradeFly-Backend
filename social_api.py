"""
TradeFly Social API - FastAPI Routes
Premium social trading platform endpoints
"""

import logging
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from social_db import get_social_db, SocialDB
from social_models import (
    PostCreate, Post, PostUpdate,
    UserProfile, UserCreate, UserUpdate,
    FeedFilter, FeedResponse,
    LikeCreate, ReplyCreate, Reply, RepostCreate,
    FollowCreate,
    WatchlistCreate, WatchlistItem,
    RoomCreate, Room, RoomMemberCreate,
    TrendingContract, TrendingUser,
    SuccessResponse, ErrorResponse
)
from signal_to_social import convert_signal_to_post

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/social", tags=["social"])

# Dependency to get database
def get_db_dependency() -> SocialDB:
    return get_social_db()


# =====================================================
# FEED ENDPOINTS
# =====================================================

@router.get("/feed", response_model=FeedResponse)
async def get_feed(
    strategy: Optional[str] = Query(None, description="Filter by strategy"),
    sentiment: Optional[str] = Query(None, description="Filter by sentiment"),
    min_confidence: Optional[float] = Query(None, ge=0.0, le=1.0),
    contract_symbol: Optional[str] = Query(None, description="Filter by contract"),
    underlying_symbol: Optional[str] = Query(None, description="Filter by underlying"),
    following_only: bool = Query(False, description="Show only followed users"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: SocialDB = Depends(get_db_dependency)
):
    """
    Get personalized social feed

    Returns posts with filters applied, sorted by created_at DESC
    """
    try:
        # Build filter
        from social_models import Sentiment

        sentiment_enum = None
        if sentiment:
            sentiment_enum = Sentiment(sentiment)

        feed_filter = FeedFilter(
            strategy=strategy,
            sentiment=sentiment_enum,
            min_confidence=min_confidence,
            contract_symbol=contract_symbol,
            underlying_symbol=underlying_symbol,
            following_only=following_only,
            limit=limit,
            offset=offset
        )

        # Get feed
        feed = db.get_feed(feed_filter)

        logger.info(f"📰 Feed requested: {len(feed.posts)} posts returned (strategy={strategy})")

        return feed

    except Exception as e:
        logger.error(f"❌ Error getting feed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/feed/contract/{contract_symbol}", response_model=FeedResponse)
async def get_contract_feed(
    contract_symbol: str,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: SocialDB = Depends(get_db_dependency)
):
    """Get all posts about a specific contract"""
    try:
        feed_filter = FeedFilter(
            contract_symbol=contract_symbol,
            limit=limit,
            offset=offset
        )

        feed = db.get_feed(feed_filter)

        logger.info(f"📊 Contract feed for {contract_symbol}: {len(feed.posts)} posts")

        return feed

    except Exception as e:
        logger.error(f"❌ Error getting contract feed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# POST ENDPOINTS
# =====================================================

@router.post("/posts", response_model=SuccessResponse)
async def create_post(
    post_data: PostCreate,
    author_id: UUID = Query(..., description="Author user ID"),
    db: SocialDB = Depends(get_db_dependency)
):
    """Create a new post"""
    try:
        post_id = db.create_post(author_id, post_data)

        if not post_id:
            raise HTTPException(status_code=500, detail="Failed to create post")

        logger.info(f"✅ Post created: {post_id} by {author_id}")

        return SuccessResponse(
            message="Post created successfully",
            data={"post_id": str(post_id)}
        )

    except Exception as e:
        logger.error(f"❌ Error creating post: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/posts/{post_id}", response_model=Post)
async def get_post(
    post_id: UUID,
    db: SocialDB = Depends(get_db_dependency)
):
    """Get a single post by ID"""
    try:
        post = db.get_post(post_id)

        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        return post

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting post: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/posts/{post_id}/replies", response_model=List[Reply])
async def get_post_replies(
    post_id: UUID,
    limit: int = Query(50, ge=1, le=100),
    db: SocialDB = Depends(get_db_dependency)
):
    """Get replies for a post"""
    try:
        replies = db.get_replies(post_id, limit)

        logger.info(f"💬 Retrieved {len(replies)} replies for post {post_id}")

        return replies

    except Exception as e:
        logger.error(f"❌ Error getting replies: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# ENGAGEMENT ENDPOINTS
# =====================================================

@router.post("/posts/{post_id}/like", response_model=SuccessResponse)
async def like_post(
    post_id: UUID,
    user_id: UUID = Query(..., description="User ID"),
    db: SocialDB = Depends(get_db_dependency)
):
    """Like a post"""
    try:
        success = db.like_post(user_id, post_id)

        if not success:
            raise HTTPException(status_code=500, detail="Failed to like post")

        return SuccessResponse(message="Post liked")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error liking post: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/posts/{post_id}/like", response_model=SuccessResponse)
async def unlike_post(
    post_id: UUID,
    user_id: UUID = Query(..., description="User ID"),
    db: SocialDB = Depends(get_db_dependency)
):
    """Unlike a post"""
    try:
        success = db.unlike_post(user_id, post_id)

        if not success:
            raise HTTPException(status_code=500, detail="Failed to unlike post")

        return SuccessResponse(message="Post unliked")

    except Exception as e:
        logger.error(f"❌ Error unliking post: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/posts/{post_id}/reply", response_model=SuccessResponse)
async def create_reply(
    post_id: UUID,
    reply_data: ReplyCreate,
    author_id: UUID = Query(..., description="Author user ID"),
    db: SocialDB = Depends(get_db_dependency)
):
    """Create a reply to a post"""
    try:
        reply_id = db.create_reply(author_id, reply_data)

        if not reply_id:
            raise HTTPException(status_code=500, detail="Failed to create reply")

        return SuccessResponse(
            message="Reply created",
            data={"reply_id": str(reply_id)}
        )

    except Exception as e:
        logger.error(f"❌ Error creating reply: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/posts/{post_id}/repost", response_model=SuccessResponse)
async def repost_post(
    post_id: UUID,
    user_id: UUID = Query(..., description="User ID"),
    comment: Optional[str] = Query(None, max_length=500),
    db: SocialDB = Depends(get_db_dependency)
):
    """Repost a post"""
    try:
        from social_models import RepostCreate

        repost_data = RepostCreate(
            original_post_id=post_id,
            comment=comment
        )

        repost_id = db.repost(user_id, repost_data)

        if not repost_id:
            raise HTTPException(status_code=409, detail="Already reposted")

        return SuccessResponse(
            message="Post reposted",
            data={"repost_id": str(repost_id)}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error reposting: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# USER ENDPOINTS
# =====================================================

@router.get("/users/{user_id}", response_model=UserProfile)
async def get_user(
    user_id: UUID,
    db: SocialDB = Depends(get_db_dependency)
):
    """Get user profile"""
    try:
        user = db.get_user(user_id)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return user

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting user: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# ROOM ENDPOINTS
# =====================================================

@router.get("/rooms", response_model=List[Room])
async def list_rooms(
    strategy: Optional[str] = Query(None, description="Filter by strategy"),
    room_type: Optional[str] = Query(None, description="free or premium"),
    limit: int = Query(50, ge=1, le=100),
    db: SocialDB = Depends(get_db_dependency)
):
    """List all public rooms"""
    try:
        from social_models import RoomType

        room_type_enum = None
        if room_type:
            room_type_enum = RoomType(room_type)

        rooms = db.list_rooms(strategy, room_type_enum, limit)

        logger.info(f"🏠 Retrieved {len(rooms)} rooms")

        return rooms

    except Exception as e:
        logger.error(f"❌ Error listing rooms: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rooms/{room_id}", response_model=Room)
async def get_room(
    room_id: UUID,
    db: SocialDB = Depends(get_db_dependency)
):
    """Get room details"""
    try:
        room = db.get_room(room_id)

        if not room:
            raise HTTPException(status_code=404, detail="Room not found")

        return room

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting room: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rooms/{room_id}/feed", response_model=FeedResponse)
async def get_room_feed(
    room_id: UUID,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: SocialDB = Depends(get_db_dependency)
):
    """Get posts from a specific room"""
    try:
        feed_filter = FeedFilter(
            room_id=room_id,
            limit=limit,
            offset=offset
        )

        feed = db.get_feed(feed_filter)

        logger.info(f"🏠 Room {room_id} feed: {len(feed.posts)} posts")

        return feed

    except Exception as e:
        logger.error(f"❌ Error getting room feed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# TRENDING & DISCOVERY ENDPOINTS
# =====================================================

@router.get("/trending/contracts", response_model=List[TrendingContract])
async def get_trending_contracts(
    limit: int = Query(20, ge=1, le=50),
    db: SocialDB = Depends(get_db_dependency)
):
    """Get trending options contracts (most discussed in 24hr)"""
    try:
        trending = db.get_trending_contracts(limit)

        logger.info(f"🔥 Retrieved {len(trending)} trending contracts")

        return trending

    except Exception as e:
        logger.error(f"❌ Error getting trending contracts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trending/users", response_model=List[TrendingUser])
async def get_leaderboard(
    limit: int = Query(50, ge=1, le=100),
    db: SocialDB = Depends(get_db_dependency)
):
    """Get user leaderboard (top by reputation)"""
    try:
        leaderboard = db.get_leaderboard(limit)

        logger.info(f"🏆 Retrieved top {len(leaderboard)} users")

        return leaderboard

    except Exception as e:
        logger.error(f"❌ Error getting leaderboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# UTILITY ENDPOINTS
# =====================================================

@router.post("/signals/auto-post", response_model=SuccessResponse)
async def auto_post_signal(
    signal: dict,
    db: SocialDB = Depends(get_db_dependency)
):
    """
    Auto-convert and post a signal to social feed
    Used by signal generation system
    """
    try:
        # Convert signal to post
        post_data = convert_signal_to_post(signal)

        # Post as system user
        system_user_id = UUID("00000000-0000-0000-0000-000000000000")
        post_id = db.create_post(system_user_id, post_data)

        if not post_id:
            raise HTTPException(status_code=500, detail="Failed to create signal post")

        logger.info(f"🎯 Auto-posted signal: {signal.get('contract', {}).get('symbol')} → {post_id}")

        return SuccessResponse(
            message="Signal posted to social feed",
            data={"post_id": str(post_id)}
        )

    except Exception as e:
        logger.error(f"❌ Error auto-posting signal: {e}")
        raise HTTPException(status_code=500, detail=str(e))
