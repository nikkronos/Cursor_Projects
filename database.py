import sqlite3
from datetime import datetime
from typing import Optional, List, Any
from loader import logger

DB_FILE = "bot.db"

def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row # Allows accessing columns by name
    return conn

# --- Helper functions for dates ---
def parse_db_date(date_str: Optional[str]) -> Optional[datetime]:
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
    if not date_obj:
        return None
    return str(date_obj)

# Database initialization
def init_db() -> None:
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
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tariff_answers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    question_number INTEGER,
                    answer TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'pending',
                    FOREIGN KEY (user_id) REFERENCES users(telegram_id)
                )
            """)
            
            conn.commit()
            
            # Создание индексов для оптимизации запросов
            try:
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_subscription_status ON users(subscription_status)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_subscription_end_date ON users(subscription_end_date)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_subscription_status_end_date ON users(subscription_status, subscription_end_date)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_receipts_user_id ON receipts(user_id)")
                conn.commit()
                logger.info("Database indexes created successfully.")
            except sqlite3.Error as e:
                logger.error(f"Error creating indexes: {e}")
            
            try:
                cursor.execute("ALTER TABLE users ADD COLUMN last_notification_level TEXT DEFAULT NULL")
            except sqlite3.OperationalError:
                pass 
                
        logger.info("Database initialized (SQLite).")
    except Exception as e:
        logger.critical(f"Error initializing database: {e}")

# --- Database Migration Functions ---

def migrate_add_indexes() -> None:
    """Добавить индексы в существующую базу данных (миграция)"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Проверяем, существуют ли уже индексы
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='index' AND name='idx_subscription_status'
            """)
            if cursor.fetchone():
                logger.info("Indexes already exist, skipping migration.")
                return
            
            logger.info("Starting database migration: adding indexes...")
            
            # Создаем индексы
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_subscription_status ON users(subscription_status)")
            logger.info("Created index: idx_subscription_status")
            
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_subscription_end_date ON users(subscription_end_date)")
            logger.info("Created index: idx_subscription_end_date")
            
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_subscription_status_end_date ON users(subscription_status, subscription_end_date)")
            logger.info("Created index: idx_subscription_status_end_date")
            
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_receipts_user_id ON receipts(user_id)")
            logger.info("Created index: idx_receipts_user_id")
            
            conn.commit()
            logger.info("Database migration completed successfully.")
            
    except Exception as e:
        logger.error(f"Error during database migration: {e}")

# --- Data Access Functions ---

def get_user_status(telegram_id: int) -> Optional[sqlite3.Row]:
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
            user = cursor.fetchone()
            return user
    except Exception as e:
        logger.error(f"Error fetching user status: {e}")
        return None

def get_all_users_for_check() -> List[sqlite3.Row]:
    """Получить всех пользователей для проверки (оптимизировано для планировщика)"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # Оптимизация: получаем только пользователей, которые могут иметь активную подписку
            # или нуждаются в проверке (активные + неактивные с датой окончания)
            cursor.execute("""
                SELECT telegram_id, first_name, subscription_status, subscription_end_date, 
                       payment_status, last_notification_level 
                FROM users 
                WHERE subscription_status = 'active' 
                   OR (subscription_status = 'inactive' AND subscription_end_date IS NOT NULL)
            """)
            return cursor.fetchall()
    except Exception as e:
        logger.error(f"Error fetching users for check: {e}")
        return []

def get_active_users_for_check() -> List[sqlite3.Row]:
    """Получить только активных пользователей для проверки (более быстрый запрос)"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT telegram_id, first_name, subscription_status, subscription_end_date, 
                       payment_status, last_notification_level 
                FROM users 
                WHERE subscription_status = 'active' AND subscription_end_date IS NOT NULL
            """)
            return cursor.fetchall()
    except Exception as e:
        logger.error(f"Error fetching active users for check: {e}")
        return []

def get_users_by_status(message: Any, status: str) -> None:
    """Получить список пользователей по статусу подписки и отправить админу"""
    from loader import bot
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT telegram_id, first_name, username, subscription_status, 
                       subscription_start_date, subscription_end_date, payment_status 
                FROM users 
                WHERE subscription_status = ?
                ORDER BY subscription_end_date DESC
            """, (status,))
            users = cursor.fetchall()
        
        if users:
            response = f"Пользователи со статусом '{status}':\n\n"
            for user in users:
                start_date = parse_db_date(user['subscription_start_date'])
                end_date = parse_db_date(user['subscription_end_date'])
                
                start_date_str = start_date.strftime('%d.%m.%Y %H:%M') if start_date else 'N/A'
                end_date_str = end_date.strftime('%d.%m.%Y %H:%M') if end_date else 'N/A'
                
                username = f"@{user['username']}" if user['username'] else "нет username"
                response += f"ID: {user['telegram_id']}\n"
                response += f"Имя: {user['first_name']}\n"
                response += f"Username: {username}\n"
                response += f"Начало: {start_date_str}\n"
                response += f"Конец: {end_date_str}\n"
                response += f"Оплата: {user['payment_status']}\n"
                response += "─" * 20 + "\n"
            
            # Разбиваем на части, если сообщение слишком длинное (Telegram лимит ~4096 символов)
            if len(response) > 4000:
                parts = response.split("─" * 20 + "\n")
                current_part = ""
                for part in parts:
                    if len(current_part + part) > 4000:
                        bot.send_message(message.chat.id, current_part, parse_mode='Markdown')
                        current_part = part
                    else:
                        current_part += part + "─" * 20 + "\n"
                if current_part:
                    bot.send_message(message.chat.id, current_part, parse_mode='Markdown')
            else:
                bot.send_message(message.chat.id, response, parse_mode='Markdown')
        else:
            bot.send_message(message.chat.id, f"Пользователи со статусом '{status}' не найдены.")
    except Exception as e:
        logger.error(f"Error getting users by status: {e}")
        bot.send_message(message.chat.id, f"Ошибка при получении списка пользователей: {e}")

def save_tariff_answer(user_id: int, question_number: int, answer: str) -> bool:
    """Сохранить ответ на вопрос опроса"""
    try:
        with get_db_connection() as conn:
            conn.execute("""
                INSERT INTO tariff_answers (user_id, question_number, answer, status)
                VALUES (?, ?, ?, 'pending')
            """, (user_id, question_number, answer))
            conn.commit()
        return True
    except Exception as e:
        logger.error(f"Error saving tariff answer: {e}")
        return False

def get_user_tariff_answers(user_id: int) -> List[sqlite3.Row]:
    """Получить все ответы пользователя на вопросы опроса"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT question_number, answer 
                FROM tariff_answers 
                WHERE user_id = ? AND status = 'pending'
                ORDER BY question_number
            """, (user_id,))
            return cursor.fetchall()
    except Exception as e:
        logger.error(f"Error getting user tariff answers: {e}")
        return []

def clear_user_tariff_answers(user_id: int) -> bool:
    """Очистить ответы пользователя (после подтверждения/отклонения)"""
    try:
        with get_db_connection() as conn:
            conn.execute("DELETE FROM tariff_answers WHERE user_id = ?", (user_id,))
            conn.commit()
        return True
    except Exception as e:
        logger.error(f"Error clearing user tariff answers: {e}")
        return False

def update_tariff_answers_status(user_id: int, status: str) -> bool:
    """Обновить статус ответов пользователя (approved/rejected)"""
    try:
        with get_db_connection() as conn:
            conn.execute("""
                UPDATE tariff_answers 
                SET status = ? 
                WHERE user_id = ? AND status = 'pending'
            """, (status, user_id))
            conn.commit()
        return True
    except Exception as e:
        logger.error(f"Error updating tariff answers status: {e}")
        return False

