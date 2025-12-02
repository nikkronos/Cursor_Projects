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

def get_users_by_status(message, status):
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

def save_tariff_answer(user_id, question_number, answer):
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

def get_user_tariff_answers(user_id):
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

def clear_user_tariff_answers(user_id):
    """Очистить ответы пользователя (после подтверждения/отклонения)"""
    try:
        with get_db_connection() as conn:
            conn.execute("DELETE FROM tariff_answers WHERE user_id = ?", (user_id,))
            conn.commit()
        return True
    except Exception as e:
        logger.error(f"Error clearing user tariff answers: {e}")
        return False

def update_tariff_answers_status(user_id, status):
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

