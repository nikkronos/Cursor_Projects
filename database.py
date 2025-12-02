import sqlite3
from datetime import datetime
from loader import logger

DB_FILE = "bot.db"

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row # Allows accessing columns by name
    return conn

# --- Helper functions for dates ---
def parse_db_date(date_str):
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S.%f')
    except ValueError:
        try:
            return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        except ValueError:
             return None

def format_db_date(date_obj):
    if not date_obj:
        return None
    return str(date_obj)

# Database initialization
def init_db():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    telegram_id INTEGER PRIMARY KEY,
                    first_name TEXT,
                    username TEXT,
                    subscription_status TEXT DEFAULT 'inactive',
                    subscription_start_date TEXT,
                    subscription_end_date TEXT,
                    payment_status TEXT DEFAULT 'pending',
                    last_notification_level TEXT DEFAULT NULL
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS receipts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    file_id TEXT,
                    file_type TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            
            try:
                cursor.execute("ALTER TABLE users ADD COLUMN last_notification_level TEXT DEFAULT NULL")
            except sqlite3.OperationalError:
                pass 
                
        logger.info("Database initialized (SQLite).")
    except Exception as e:
        logger.critical(f"Error initializing database: {e}")

# --- Data Access Functions ---

def get_user_status(telegram_id):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
            user = cursor.fetchone()
            return user
    except Exception as e:
        logger.error(f"Error fetching user status: {e}")
        return None

def get_all_users_for_check():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT telegram_id, first_name, subscription_status, subscription_end_date, payment_status, last_notification_level FROM users")
            return cursor.fetchall()
    except Exception as e:
        logger.error(f"Error fetching all users for check: {e}")
        return []

