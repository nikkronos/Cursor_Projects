"""
Database module for Копия иксуюемся.
Handles SQLite database operations.
"""
import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any
from loader import logger

DB_FILE = "bot.db"

def get_db_connection() -> sqlite3.Connection:
    """
    Get database connection with Row factory.
    
    Returns:
        SQLite connection object
    """
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # Allows accessing columns by name
    return conn

# --- Helper functions for dates ---
def parse_db_date(date_str: Optional[str]) -> Optional[datetime]:
    """Parse date string from database to datetime object."""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S.%f')
    except ValueError:
        try:
            return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return None

def format_db_date(date_obj: Optional[datetime]) -> Optional[str]:
    """Format datetime object to string for database storage."""
    if not date_obj:
        return None
    return str(date_obj)

# Database initialization
def init_db() -> None:
    """Initialize database with required tables."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Table: users - информация о пользователях
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    telegram_id INTEGER PRIMARY KEY,
                    first_name TEXT,
                    username TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Table: subscriptions - подписки пользователей на каналы
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS subscriptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    channel_id TEXT NOT NULL,
                    status TEXT DEFAULT 'active',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(telegram_id),
                    UNIQUE(user_id, channel_id)
                )
            """)
            
            # Table: messages - история скопированных сообщений (опционально, для логирования)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_id INTEGER,
                    target_message_id INTEGER,
                    source_channel_id TEXT,
                    target_channel_id TEXT,
                    message_type TEXT,
                    copied_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Migration: add target_message_id if table already exists without it
            try:
                cursor.execute("ALTER TABLE messages ADD COLUMN target_message_id INTEGER")
                conn.commit()
            except sqlite3.OperationalError:
                pass  # column already exists
            
            conn.commit()
            
            # Create indexes for optimization
            try:
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON subscriptions(user_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_subscriptions_channel_id ON subscriptions(channel_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_subscriptions_status ON subscriptions(status)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_source_channel ON messages(source_channel_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_target_channel ON messages(target_channel_id)")
                conn.commit()
                logger.info("Database indexes created successfully.")
            except sqlite3.Error as e:
                logger.error(f"Error creating indexes: {e}")
                
        logger.info("Database initialized (SQLite).")
    except Exception as e:
        logger.critical(f"Error initializing database: {e}")

# --- User Management Functions ---

def register_user(telegram_id: int, first_name: Optional[str] = None, username: Optional[str] = None) -> bool:
    """
    Register a new user in the database.
    
    Args:
        telegram_id: User's Telegram ID
        first_name: User's first name
        username: User's username
    
    Returns:
        True if user was registered, False if user already exists
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO users (telegram_id, first_name, username)
                VALUES (?, ?, ?)
            """, (telegram_id, first_name, username))
            conn.commit()
            
            if cursor.rowcount > 0:
                logger.info(f"User {telegram_id} registered successfully.")
                return True
            else:
                logger.debug(f"User {telegram_id} already exists.")
                return False
    except Exception as e:
        logger.error(f"Error registering user {telegram_id}: {e}")
        return False

def get_user(telegram_id: int) -> Optional[sqlite3.Row]:
    """
    Get user information from database.
    
    Args:
        telegram_id: User's Telegram ID
    
    Returns:
        User row if found, None otherwise
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
            return cursor.fetchone()
    except Exception as e:
        logger.error(f"Error fetching user {telegram_id}: {e}")
        return None

# --- Subscription Management Functions ---

def add_subscription(user_id: int, channel_id: str) -> bool:
    """
    Add subscription for user to channel.
    
    Args:
        user_id: User's Telegram ID
        channel_id: Channel ID to subscribe to
    
    Returns:
        True if subscription was added, False otherwise
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO subscriptions (user_id, channel_id, status, created_at)
                VALUES (?, ?, 'active', CURRENT_TIMESTAMP)
            """, (user_id, channel_id))
            conn.commit()
            
            if cursor.rowcount > 0:
                logger.info(f"Subscription added: user {user_id} -> channel {channel_id}")
                return True
            return False
    except Exception as e:
        logger.error(f"Error adding subscription for user {user_id} to channel {channel_id}: {e}")
        return False

def remove_subscription(user_id: int, channel_id: str) -> bool:
    """
    Remove subscription for user from channel.
    
    Args:
        user_id: User's Telegram ID
        channel_id: Channel ID to unsubscribe from
    
    Returns:
        True if subscription was removed, False otherwise
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM subscriptions
                WHERE user_id = ? AND channel_id = ?
            """, (user_id, channel_id))
            conn.commit()
            
            if cursor.rowcount > 0:
                logger.info(f"Subscription removed: user {user_id} -> channel {channel_id}")
                return True
            return False
    except Exception as e:
        logger.error(f"Error removing subscription for user {user_id} from channel {channel_id}: {e}")
        return False

def check_subscription(user_id: int, channel_id: str) -> bool:
    """
    Check if user is subscribed to channel.
    
    Args:
        user_id: User's Telegram ID
        channel_id: Channel ID to check
    
    Returns:
        True if user is subscribed, False otherwise
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT status FROM subscriptions
                WHERE user_id = ? AND channel_id = ? AND status = 'active'
            """, (user_id, channel_id))
            result = cursor.fetchone()
            return result is not None
    except Exception as e:
        logger.error(f"Error checking subscription for user {user_id} to channel {channel_id}: {e}")
        return False

def get_subscribed_users(channel_id: str) -> List[int]:
    """
    Get list of user IDs subscribed to channel.
    
    Args:
        channel_id: Channel ID
    
    Returns:
        List of user Telegram IDs
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT user_id FROM subscriptions
                WHERE channel_id = ? AND status = 'active'
            """, (channel_id,))
            return [row[0] for row in cursor.fetchall()]
    except Exception as e:
        logger.error(f"Error getting subscribed users for channel {channel_id}: {e}")
        return []

# --- Message Logging Functions ---

def log_copied_message(
    message_id: int,
    source_channel_id: str,
    target_channel_id: str,
    message_type: str,
    target_message_id: Optional[int] = None,
) -> bool:
    """
    Log copied message to database (optional, for tracking).
    target_message_id is used to resolve reply_to_message_id for native clickable replies.
    
    Args:
        message_id: Original (source) message ID
        source_channel_id: Source channel ID
        target_channel_id: Target channel ID
        message_type: Type of message (text, photo, video, etc.)
        target_message_id: ID of the message in the target channel (for reply linking)
    
    Returns:
        True if logged successfully, False otherwise
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO messages (message_id, target_message_id, source_channel_id, target_channel_id, message_type)
                VALUES (?, ?, ?, ?, ?)
            """, (message_id, target_message_id, source_channel_id, target_channel_id, message_type))
            conn.commit()
            return True
    except Exception as e:
        logger.error(f"Error logging copied message {message_id}: {e}")
        return False


def is_message_copied(source_channel_id: str, target_channel_id: str, source_message_id: int) -> bool:
    """
    Check if a message has already been copied to prevent duplicates.
    
    Args:
        source_channel_id: Source channel ID
        target_channel_id: Target channel ID
        source_message_id: Message ID in the source channel
    
    Returns:
        True if message was already copied, False otherwise
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM messages
                WHERE source_channel_id = ? AND target_channel_id = ? AND message_id = ?
            """, (source_channel_id, target_channel_id, source_message_id))
            count = cursor.fetchone()[0]
            return count > 0
    except Exception as e:
        logger.error(f"Error checking if message {source_message_id} was copied: {e}")
        return False  # If check fails, allow copy (better to duplicate than miss)


def get_target_message_id(source_channel_id: str, target_channel_id: str, source_message_id: int) -> Optional[int]:
    """
    Get target channel message ID for a given source message ID (for reply_to_message_id).
    
    Args:
        source_channel_id: Source channel ID
        target_channel_id: Target channel ID
        source_message_id: Message ID in the source channel
    
    Returns:
        Message ID in the target channel, or None if not found
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT target_message_id FROM messages
                WHERE source_channel_id = ? AND target_channel_id = ? AND message_id = ?
                ORDER BY id DESC LIMIT 1
            """, (source_channel_id, target_channel_id, source_message_id))
            row = cursor.fetchone()
            return int(row["target_message_id"]) if row and row["target_message_id"] is not None else None
    except Exception as e:
        logger.error(f"Error getting target message id for source {source_message_id}: {e}")
        return None
