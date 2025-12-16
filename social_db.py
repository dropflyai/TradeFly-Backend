"""
Social Platform Database Operations
Extends Supabase client with social features: users, posts, rooms, engagement
"""

import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
from uuid import UUID
from supabase import Client
from social_models import *
from supabase_client import get_db

logger = logging.getLogger(__name__)


class SocialDB:
    """Social platform database operations"""

    def __init__(self):
        """Initialize with shared Supabase client"""
        self.db = get_db()
        self.client: Optional[Client] = self.db.client if self.db else None

    def is_connected(self) -> bool:
        """Check if database is connected"""
        return self.client is not None

    # =====================================================
    # USER OPERATIONS
    # =====================================================

    def create_user(self, user_data: UserCreate) -> Optional[UUID]:
        """
        Create a new user
        Note: In production, use Supabase Auth for user creation
        This is a simplified version for backend-only creation
        """
        if not self.client:
            return None

        try:
            record = {
                "username": user_data.username,
                "email": user_data.email,
                "display_name": user_data.display_name,
                "bio": user_data.bio,
                "avatar_url": user_data.avatar_url,
                "experience_level": user_data.experience_level.value,
                "preferred_strategies": user_data.preferred_strategies,
                "specialization_tags": user_data.specialization_tags
            }

            result = self.client.table("users").insert(record).execute()

            if result.data:
                logger.info(f"✅ Created user: {user_data.username}")
                return UUID(result.data[0]["user_id"])

            return None

        except Exception as e:
            logger.error(f"❌ Error creating user: {e}")
            return None

    def get_user(self, user_id: UUID) -> Optional[UserProfile]:
        """Get user profile by ID"""
        if not self.client:
            return None

        try:
            result = self.client.table("users").select("*").eq("user_id", str(user_id)).single().execute()

            if result.data:
                return UserProfile(**result.data)

            return None

        except Exception as e:
            logger.error(f"❌ Error getting user: {e}")
            return None

    def get_user_by_username(self, username: str) -> Optional[UserProfile]:
        """Get user profile by username"""
        if not self.client:
            return None

        try:
            result = self.client.table("users").select("*").eq("username", username).single().execute()

            if result.data:
                return UserProfile(**result.data)

            return None

        except Exception as e:
            logger.error(f"❌ Error getting user by username: {e}")
            return None

    def update_user(self, user_id: UUID, updates: UserUpdate) -> bool:
        """Update user profile"""
        if not self.client:
            return False

        try:
            # Only include non-None values
            update_data = {k: v for k, v in updates.dict().items() if v is not None}
            update_data["updated_at"] = datetime.utcnow().isoformat()

            self.client.table("users").update(update_data).eq("user_id", str(user_id)).execute()

            logger.info(f"✅ Updated user: {user_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Error updating user: {e}")
            return False

    def update_user_reputation(self, user_id: UUID, delta: int) -> bool:
        """Adjust user reputation score"""
        if not self.client:
            return False

        try:
            # Get current score
            user = self.get_user(user_id)
            if not user:
                return False

            new_score = max(0, user.reputation_score + delta)  # Don't go below 0

            self.client.table("users").update({
                "reputation_score": new_score,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("user_id", str(user_id)).execute()

            logger.info(f"✅ Updated reputation for {user_id}: {user.reputation_score} → {new_score} ({delta:+d})")
            return True

        except Exception as e:
            logger.error(f"❌ Error updating reputation: {e}")
            return False

    # =====================================================
    # POST OPERATIONS
    # =====================================================

    def create_post(self, author_id: UUID, post_data: PostCreate) -> Optional[UUID]:
        """Create a new post"""
        if not self.client:
            return None

        try:
            record = {
                "author_id": str(author_id),
                "content": post_data.content,
                "media_urls": post_data.media_urls,
                "contract_symbol": post_data.contract_symbol,
                "underlying_symbol": post_data.underlying_symbol,
                "sentiment": post_data.sentiment.value if post_data.sentiment else None,
                "strategy": post_data.strategy,
                "post_type": post_data.post_type.value,
                "room_id": str(post_data.room_id) if post_data.room_id else None,
                "signal_id": str(post_data.signal_id) if post_data.signal_id else None,
                "signal_data": post_data.signal_data
            }

            result = self.client.table("posts").insert(record).execute()

            if result.data:
                post_id = UUID(result.data[0]["post_id"])
                logger.info(f"✅ Created post: {post_id} by {author_id}")

                # Award reputation for posting
                self.update_user_reputation(author_id, delta=1)

                return post_id

            return None

        except Exception as e:
            logger.error(f"❌ Error creating post: {e}")
            return None

    def get_post(self, post_id: UUID) -> Optional[Post]:
        """Get post by ID with author info"""
        if not self.client:
            return None

        try:
            # Use the user_feed view for optimized query
            result = self.client.from_("user_feed").select("*").eq("post_id", str(post_id)).single().execute()

            if result.data:
                return Post(**result.data)

            return None

        except Exception as e:
            logger.error(f"❌ Error getting post: {e}")
            return None

    def update_post(self, post_id: UUID, author_id: UUID, updates: PostUpdate) -> bool:
        """Update post (only within 5 minutes of creation)"""
        if not self.client:
            return False

        try:
            # Verify author and check time limit
            post = self.get_post(post_id)
            if not post or post.author_id != author_id:
                logger.warning(f"Post {post_id} not found or unauthorized")
                return False

            # Check 5-minute edit window
            if (datetime.utcnow() - post.created_at).total_seconds() > 300:
                logger.warning(f"Post {post_id} edit window expired")
                return False

            update_data = {k: v for k, v in updates.dict().items() if v is not None}
            update_data["updated_at"] = datetime.utcnow().isoformat()
            update_data["edited_at"] = datetime.utcnow().isoformat()

            self.client.table("posts").update(update_data).eq("post_id", str(post_id)).execute()

            logger.info(f"✅ Updated post: {post_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Error updating post: {e}")
            return False

    def delete_post(self, post_id: UUID, author_id: UUID) -> bool:
        """Delete post (soft delete by hiding)"""
        if not self.client:
            return False

        try:
            # Verify author
            post = self.get_post(post_id)
            if not post or post.author_id != author_id:
                return False

            self.client.table("posts").update({
                "is_hidden": True,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("post_id", str(post_id)).execute()

            logger.info(f"✅ Deleted (hidden) post: {post_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Error deleting post: {e}")
            return False

    def get_feed(self, filters: FeedFilter, user_id: Optional[UUID] = None) -> FeedResponse:
        """
        Get feed with filters
        """
        if not self.client:
            return FeedResponse(posts=[], total_count=0, has_more=False)

        try:
            # Start with user_feed view
            query = self.client.from_("user_feed").select("*", count="exact")

            # Apply filters
            if filters.strategy:
                query = query.eq("strategy", filters.strategy)

            if filters.sentiment:
                query = query.eq("sentiment", filters.sentiment.value)

            if filters.contract_symbol:
                query = query.eq("contract_symbol", filters.contract_symbol)

            if filters.underlying_symbol:
                query = query.eq("underlying_symbol", filters.underlying_symbol)

            if filters.author_id:
                query = query.eq("author_id", str(filters.author_id))

            if filters.room_id:
                query = query.eq("room_id", str(filters.room_id))

            if filters.min_confidence and filters.min_confidence > 0:
                # Filter by signal confidence in JSONB
                query = query.gte("signal_data->confidence", filters.min_confidence)

            # Following filter (requires join)
            if filters.following_only and user_id:
                # Get list of followed users
                follows_result = self.client.table("follows").select("following_id").eq("follower_id", str(user_id)).execute()
                following_ids = [f["following_id"] for f in follows_result.data]

                if following_ids:
                    query = query.in_("author_id", following_ids)
                else:
                    # No follows, return empty
                    return FeedResponse(posts=[], total_count=0, has_more=False)

            # Pagination
            query = query.order("created_at", desc=True).range(filters.offset, filters.offset + filters.limit - 1)

            result = query.execute()

            posts = [Post(**post) for post in result.data]
            total_count = result.count or 0
            has_more = (filters.offset + filters.limit) < total_count

            return FeedResponse(
                posts=posts,
                total_count=total_count,
                has_more=has_more
            )

        except Exception as e:
            logger.error(f"❌ Error getting feed: {e}")
            return FeedResponse(posts=[], total_count=0, has_more=False)

    # =====================================================
    # ENGAGEMENT OPERATIONS
    # =====================================================

    def like_post(self, user_id: UUID, post_id: UUID) -> bool:
        """Like a post"""
        if not self.client:
            return False

        try:
            self.client.table("post_likes").insert({
                "user_id": str(user_id),
                "post_id": str(post_id)
            }).execute()

            # Get post author to award reputation
            post = self.get_post(post_id)
            if post:
                self.update_user_reputation(post.author_id, delta=2)  # +2 for getting a like

            logger.info(f"✅ User {user_id} liked post {post_id}")
            return True

        except Exception as e:
            if "duplicate key" in str(e).lower():
                logger.debug(f"Post {post_id} already liked by {user_id}")
                return True  # Already liked, consider it success
            logger.error(f"❌ Error liking post: {e}")
            return False

    def unlike_post(self, user_id: UUID, post_id: UUID) -> bool:
        """Unlike a post"""
        if not self.client:
            return False

        try:
            self.client.table("post_likes").delete().eq("user_id", str(user_id)).eq("post_id", str(post_id)).execute()

            logger.info(f"✅ User {user_id} unliked post {post_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Error unliking post: {e}")
            return False

    def create_reply(self, author_id: UUID, reply_data: ReplyCreate) -> Optional[UUID]:
        """Create a reply to a post"""
        if not self.client:
            return None

        try:
            record = {
                "author_id": str(author_id),
                "post_id": str(reply_data.post_id),
                "content": reply_data.content,
                "parent_reply_id": str(reply_data.parent_reply_id) if reply_data.parent_reply_id else None
            }

            result = self.client.table("post_replies").insert(record).execute()

            if result.data:
                reply_id = UUID(result.data[0]["reply_id"])
                logger.info(f"✅ Created reply: {reply_id} by {author_id}")

                # Award reputation for replying
                self.update_user_reputation(author_id, delta=1)

                # Award reputation to original post author
                post = self.get_post(reply_data.post_id)
                if post:
                    self.update_user_reputation(post.author_id, delta=1)

                return reply_id

            return None

        except Exception as e:
            logger.error(f"❌ Error creating reply: {e}")
            return None

    def get_replies(self, post_id: UUID, limit: int = 50) -> List[Reply]:
        """Get replies for a post"""
        if not self.client:
            return []

        try:
            result = self.client.table("post_replies").select("""
                *,
                users!post_replies_author_id_fkey(username, display_name, avatar_url)
            """).eq("post_id", str(post_id)).order("created_at", desc=False).limit(limit).execute()

            replies = []
            for row in result.data:
                user_data = row.pop("users", {})
                reply = Reply(
                    **row,
                    author_username=user_data.get("username"),
                    author_display_name=user_data.get("display_name"),
                    author_avatar_url=user_data.get("avatar_url")
                )
                replies.append(reply)

            return replies

        except Exception as e:
            logger.error(f"❌ Error getting replies: {e}")
            return []

    def repost(self, user_id: UUID, repost_data: RepostCreate) -> Optional[UUID]:
        """Repost a post"""
        if not self.client:
            return None

        try:
            record = {
                "user_id": str(user_id),
                "original_post_id": str(repost_data.original_post_id),
                "comment": repost_data.comment
            }

            result = self.client.table("post_reposts").insert(record).execute()

            if result.data:
                repost_id = UUID(result.data[0]["repost_id"])
                logger.info(f"✅ Created repost: {repost_id} by {user_id}")

                # Award reputation to original post author
                post = self.get_post(repost_data.original_post_id)
                if post:
                    self.update_user_reputation(post.author_id, delta=3)  # +3 for getting a repost

                return repost_id

            return None

        except Exception as e:
            if "duplicate key" in str(e).lower():
                logger.debug(f"Post already reposted by {user_id}")
                return None
            logger.error(f"❌ Error reposting: {e}")
            return None

    # =====================================================
    # FOLLOW OPERATIONS
    # =====================================================

    def follow_user(self, follower_id: UUID, following_id: UUID) -> bool:
        """Follow a user"""
        if not self.client:
            return False

        try:
            if follower_id == following_id:
                logger.warning("Cannot follow yourself")
                return False

            self.client.table("follows").insert({
                "follower_id": str(follower_id),
                "following_id": str(following_id)
            }).execute()

            logger.info(f"✅ User {follower_id} followed {following_id}")
            return True

        except Exception as e:
            if "duplicate key" in str(e).lower():
                logger.debug(f"Already following")
                return True
            logger.error(f"❌ Error following user: {e}")
            return False

    def unfollow_user(self, follower_id: UUID, following_id: UUID) -> bool:
        """Unfollow a user"""
        if not self.client:
            return False

        try:
            self.client.table("follows").delete().eq("follower_id", str(follower_id)).eq("following_id", str(following_id)).execute()

            logger.info(f"✅ User {follower_id} unfollowed {following_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Error unfollowing user: {e}")
            return False

    def get_followers(self, user_id: UUID, limit: int = 50) -> List[UserProfile]:
        """Get user's followers"""
        if not self.client:
            return []

        try:
            result = self.client.table("follows").select("""
                follower:users!follows_follower_id_fkey(*)
            """).eq("following_id", str(user_id)).limit(limit).execute()

            return [UserProfile(**row["follower"]) for row in result.data]

        except Exception as e:
            logger.error(f"❌ Error getting followers: {e}")
            return []

    def get_following(self, user_id: UUID, limit: int = 50) -> List[UserProfile]:
        """Get users that this user follows"""
        if not self.client:
            return []

        try:
            result = self.client.table("follows").select("""
                following:users!follows_following_id_fkey(*)
            """).eq("follower_id", str(user_id)).limit(limit).execute()

            return [UserProfile(**row["following"]) for row in result.data]

        except Exception as e:
            logger.error(f"❌ Error getting following: {e}")
            return []

    # =====================================================
    # WATCHLIST OPERATIONS
    # =====================================================

    def add_to_watchlist(self, user_id: UUID, watchlist_item: WatchlistCreate) -> bool:
        """Add contract to watchlist"""
        if not self.client:
            return False

        try:
            record = {
                "user_id": str(user_id),
                "contract_symbol": watchlist_item.contract_symbol,
                "underlying_symbol": watchlist_item.underlying_symbol,
                "alert_enabled": watchlist_item.alert_enabled,
                "alert_confidence_threshold": watchlist_item.alert_confidence_threshold
            }

            self.client.table("user_watchlists").insert(record).execute()

            logger.info(f"✅ Added {watchlist_item.contract_symbol} to {user_id} watchlist")
            return True

        except Exception as e:
            if "duplicate key" in str(e).lower():
                logger.debug("Contract already in watchlist")
                return True
            logger.error(f"❌ Error adding to watchlist: {e}")
            return False

    def remove_from_watchlist(self, user_id: UUID, contract_symbol: str) -> bool:
        """Remove contract from watchlist"""
        if not self.client:
            return False

        try:
            self.client.table("user_watchlists").delete().eq("user_id", str(user_id)).eq("contract_symbol", contract_symbol).execute()

            logger.info(f"✅ Removed {contract_symbol} from {user_id} watchlist")
            return True

        except Exception as e:
            logger.error(f"❌ Error removing from watchlist: {e}")
            return False

    def get_watchlist(self, user_id: UUID) -> List[WatchlistItem]:
        """Get user's watchlist"""
        if not self.client:
            return []

        try:
            result = self.client.table("user_watchlists").select("*").eq("user_id", str(user_id)).order("added_at", desc=True).execute()

            return [WatchlistItem(**item) for item in result.data]

        except Exception as e:
            logger.error(f"❌ Error getting watchlist: {e}")
            return []

    # =====================================================
    # ROOM OPERATIONS
    # =====================================================

    def create_room(self, owner_id: UUID, room_data: RoomCreate) -> Optional[UUID]:
        """Create a new room"""
        if not self.client:
            return None

        try:
            record = {
                "owner_id": str(owner_id),
                "name": room_data.name,
                "description": room_data.description,
                "room_type": room_data.room_type.value,
                "price_monthly": room_data.price_monthly,
                "strategy_focus": room_data.strategy_focus,
                "is_public": room_data.is_public,
                "requires_approval": room_data.requires_approval
            }

            result = self.client.table("rooms").insert(record).execute()

            if result.data:
                room_id = UUID(result.data[0]["room_id"])

                # Auto-join owner as owner role
                self.join_room(owner_id, room_id, role=MemberRole.OWNER)

                logger.info(f"✅ Created room: {room_id} by {owner_id}")
                return room_id

            return None

        except Exception as e:
            logger.error(f"❌ Error creating room: {e}")
            return None

    def get_room(self, room_id: UUID) -> Optional[Room]:
        """Get room by ID"""
        if not self.client:
            return None

        try:
            result = self.client.table("rooms").select("""
                *,
                owner:users!rooms_owner_id_fkey(username, display_name)
            """).eq("room_id", str(room_id)).single().execute()

            if result.data:
                owner_data = result.data.pop("owner", {})
                return Room(
                    **result.data,
                    owner_username=owner_data.get("username"),
                    owner_display_name=owner_data.get("display_name")
                )

            return None

        except Exception as e:
            logger.error(f"❌ Error getting room: {e}")
            return None

    def list_rooms(self, strategy: Optional[str] = None, room_type: Optional[RoomType] = None, limit: int = 50) -> List[Room]:
        """List rooms with filters"""
        if not self.client:
            return []

        try:
            query = self.client.table("rooms").select("""
                *,
                owner:users!rooms_owner_id_fkey(username, display_name)
            """).eq("is_public", True)

            if strategy:
                query = query.eq("strategy_focus", strategy)

            if room_type:
                query = query.eq("room_type", room_type.value)

            result = query.order("members_count", desc=True).limit(limit).execute()

            rooms = []
            for row in result.data:
                owner_data = row.pop("owner", {})
                room = Room(
                    **row,
                    owner_username=owner_data.get("username"),
                    owner_display_name=owner_data.get("display_name")
                )
                rooms.append(room)

            return rooms

        except Exception as e:
            logger.error(f"❌ Error listing rooms: {e}")
            return []

    def join_room(self, user_id: UUID, room_id: UUID, role: MemberRole = MemberRole.MEMBER) -> bool:
        """Join a room"""
        if not self.client:
            return False

        try:
            record = {
                "user_id": str(user_id),
                "room_id": str(room_id),
                "role": role.value
            }

            self.client.table("room_members").insert(record).execute()

            logger.info(f"✅ User {user_id} joined room {room_id}")
            return True

        except Exception as e:
            if "duplicate key" in str(e).lower():
                logger.debug("Already a member")
                return True
            logger.error(f"❌ Error joining room: {e}")
            return False

    def leave_room(self, user_id: UUID, room_id: UUID) -> bool:
        """Leave a room"""
        if not self.client:
            return False

        try:
            self.client.table("room_members").delete().eq("user_id", str(user_id)).eq("room_id", str(room_id)).execute()

            logger.info(f"✅ User {user_id} left room {room_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Error leaving room: {e}")
            return False

    # =====================================================
    # TRENDING & DISCOVERY
    # =====================================================

    def get_trending_contracts(self, limit: int = 20) -> List[TrendingContract]:
        """Get trending contracts"""
        if not self.client:
            return []

        try:
            result = self.client.from_("trending_contracts").select("*").limit(limit).execute()

            return [TrendingContract(**row) for row in result.data]

        except Exception as e:
            logger.error(f"❌ Error getting trending contracts: {e}")
            return []

    def get_leaderboard(self, limit: int = 50) -> List[TrendingUser]:
        """Get user leaderboard"""
        if not self.client:
            return []

        try:
            result = self.client.from_("user_leaderboard").select("*").limit(limit).execute()

            return [TrendingUser(**row) for row in result.data]

        except Exception as e:
            logger.error(f"❌ Error getting leaderboard: {e}")
            return []


# Global instance
_social_db_instance = None


def get_social_db() -> SocialDB:
    """Get global social database instance"""
    global _social_db_instance
    if _social_db_instance is None:
        _social_db_instance = SocialDB()
    return _social_db_instance
