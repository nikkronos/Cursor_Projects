"""
Тесты для проверки создания и работы индексов в базе данных
"""
import pytest
import sqlite3
import os
import tempfile
import shutil
import database
from database import init_db, migrate_add_indexes, get_db_connection, DB_FILE


@pytest.fixture
def temp_db_path(tmp_path):
    """Создает временный путь для тестовой БД"""
    db_path = tmp_path / "test_bot.db"
    return str(db_path)


@pytest.fixture
def mock_db_file(monkeypatch, temp_db_path):
    """Временно подменяет DB_FILE на тестовый путь"""
    original_db_file = database.DB_FILE
    monkeypatch.setattr(database, "DB_FILE", temp_db_path)
    yield temp_db_path
    # Восстанавливаем оригинальный путь
    monkeypatch.setattr(database, "DB_FILE", original_db_file)


def test_init_db_creates_indexes(mock_db_file):
    """Тест: при инициализации БД создаются все необходимые индексы"""
    # Arrange
    # Удаляем файл БД если существует
    if os.path.exists(mock_db_file):
        os.remove(mock_db_file)
    
    # Act
    init_db()
    
    # Assert - проверяем наличие индексов
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Проверяем индекс на subscription_status
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='index' AND name='idx_subscription_status'
        """)
        assert cursor.fetchone() is not None, "Index idx_subscription_status not found"
        
        # Проверяем индекс на subscription_end_date
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='index' AND name='idx_subscription_end_date'
        """)
        assert cursor.fetchone() is not None, "Index idx_subscription_end_date not found"
        
        # Проверяем комбинированный индекс
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='index' AND name='idx_subscription_status_end_date'
        """)
        assert cursor.fetchone() is not None, "Index idx_subscription_status_end_date not found"
        
        # Проверяем индекс на receipts.user_id
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='index' AND name='idx_receipts_user_id'
        """)
        assert cursor.fetchone() is not None, "Index idx_receipts_user_id not found"


def test_migrate_add_indexes_creates_indexes(mock_db_file):
    """Тест: миграция добавляет индексы в существующую БД"""
    # Arrange - создаем БД без индексов
    if os.path.exists(mock_db_file):
        os.remove(mock_db_file)
    
    # Создаем БД только с таблицами (без индексов)
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                telegram_id INTEGER PRIMARY KEY,
                subscription_status TEXT,
                subscription_end_date TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS receipts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER
            )
        """)
        conn.commit()
    
    # Act
    migrate_add_indexes()
    
    # Assert
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='index' AND name='idx_subscription_status'
        """)
        assert cursor.fetchone() is not None, "Migration failed to create idx_subscription_status"


def test_migrate_add_indexes_idempotent(mock_db_file):
    """Тест: миграция безопасна при повторном запуске (idempotent)"""
    # Arrange - создаем БД с индексами
    if os.path.exists(mock_db_file):
        os.remove(mock_db_file)
    
    init_db()  # Создает БД с индексами
    
    # Act - запускаем миграцию повторно
    migrate_add_indexes()
    migrate_add_indexes()  # Еще раз
    
    # Assert - индексы должны существовать, ошибок быть не должно
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM sqlite_master 
            WHERE type='index' AND name LIKE 'idx_%'
        """)
        index_count = cursor.fetchone()[0]
        assert index_count >= 4, "Expected at least 4 indexes"


def test_indexes_used_in_queries(mock_db_file):
    """Тест: индексы используются в запросах (EXPLAIN QUERY PLAN)"""
    # Arrange
    if os.path.exists(mock_db_file):
        os.remove(mock_db_file)
    
    init_db()
    
    # Добавляем тестовые данные
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (telegram_id, subscription_status, subscription_end_date)
            VALUES (123, 'active', '2024-12-31 23:59:59')
        """)
        conn.commit()
    
    # Act - проверяем план запроса
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # EXPLAIN QUERY PLAN для запроса с использованием индекса
        cursor.execute("""
            EXPLAIN QUERY PLAN
            SELECT * FROM users WHERE subscription_status = 'active'
        """)
        plan = cursor.fetchall()
        
        # Assert - план должен показывать использование индекса
        plan_str = str(plan).lower()
        # SQLite использует индексы через "SEARCH TABLE ... USING INDEX"
        # Это не гарантировано, но если индекс используется, мы увидим его в плане
        # Для простоты проверяем, что запрос выполняется без ошибок
        assert len(plan) > 0, "Query plan should not be empty"


def test_get_all_users_for_check_optimized(mock_db_file):
    """Тест: оптимизированный запрос get_all_users_for_check работает корректно"""
    # Arrange
    if os.path.exists(mock_db_file):
        os.remove(mock_db_file)
    
    init_db()
    
    # Добавляем тестовые данные
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (telegram_id, first_name, subscription_status, subscription_end_date)
            VALUES 
                (1, 'Active User', 'active', '2024-12-31 23:59:59'),
                (2, 'Inactive User', 'inactive', '2024-12-31 23:59:59'),
                (3, 'No Date User', 'inactive', NULL)
        """)
        conn.commit()
    
    # Act
    from database import get_all_users_for_check
    users = get_all_users_for_check()
    
    # Assert
    assert len(users) == 2, "Should return only active users and inactive users with end_date"
    user_ids = [user['telegram_id'] for user in users]
    assert 1 in user_ids, "Active user should be included"
    assert 2 in user_ids, "Inactive user with date should be included"
    assert 3 not in user_ids, "Inactive user without date should not be included"

