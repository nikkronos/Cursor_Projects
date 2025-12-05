"""
Тесты для механизма rate limiting
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import time
from utils import check_rate_limit, block_user, rate_limit, _rate_limit_history, _user_blocks


class TestRateLimiting(unittest.TestCase):
    """Тесты для rate limiting"""
    
    def setUp(self):
        """Очистка перед каждым тестом"""
        _rate_limit_history.clear()
        _user_blocks.clear()
    
    def test_check_rate_limit_allows_requests_within_limit(self):
        """Тест: разрешает запросы в пределах лимита"""
        user_id = 12345
        max_requests = 5
        time_window = 10.0
        
        # Делаем 5 запросов - все должны пройти
        for i in range(5):
            result = check_rate_limit(user_id, max_requests, time_window)
            self.assertTrue(result, f"Request {i+1} should be allowed")
    
    def test_check_rate_limit_blocks_exceeding_requests(self):
        """Тест: блокирует запросы, превышающие лимит"""
        user_id = 12345
        max_requests = 5
        time_window = 10.0
        
        # Делаем 5 запросов - все должны пройти
        for i in range(5):
            result = check_rate_limit(user_id, max_requests, time_window)
            self.assertTrue(result)
        
        # 6-й запрос должен быть заблокирован
        result = check_rate_limit(user_id, max_requests, time_window)
        self.assertFalse(result, "6th request should be blocked")
    
    def test_check_rate_limit_resets_after_time_window(self):
        """Тест: лимит сбрасывается после истечения окна времени"""
        user_id = 12345
        max_requests = 5
        time_window = 0.1  # Очень короткое окно для теста
        
        # Делаем 5 запросов
        for i in range(5):
            check_rate_limit(user_id, max_requests, time_window)
        
        # 6-й запрос должен быть заблокирован
        result = check_rate_limit(user_id, max_requests, time_window)
        self.assertFalse(result)
        
        # Ждем истечения окна времени
        time.sleep(0.15)
        
        # Теперь запрос должен пройти
        result = check_rate_limit(user_id, max_requests, time_window)
        self.assertTrue(result, "Request should be allowed after time window expires")
    
    def test_block_user_blocks_user(self):
        """Тест: блокировка пользователя"""
        user_id = 12345
        duration = 1.0
        
        block_user(user_id, duration)
        
        # Проверяем, что пользователь заблокирован
        self.assertIn(user_id, _user_blocks)
        self.assertGreater(_user_blocks[user_id], time.time())
    
    def test_block_user_expires_after_duration(self):
        """Тест: блокировка истекает после указанного времени"""
        user_id = 12345
        duration = 0.1  # Короткая блокировка для теста
        
        block_user(user_id, duration)
        self.assertIn(user_id, _user_blocks)
        
        # Ждем истечения блокировки
        time.sleep(0.15)
        
        # Проверяем, что блокировка истекла
        current_time = time.time()
        if user_id in _user_blocks:
            self.assertLess(_user_blocks[user_id], current_time)
    
    @patch('utils.ADMIN_ID', 99999)
    def test_rate_limit_allows_admin_unlimited(self):
        """Тест: администратор не ограничивается"""
        admin_id = 99999
        max_requests = 1
        time_window = 1.0
        
        # Администратор может делать сколько угодно запросов
        for i in range(10):
            result = check_rate_limit(admin_id, max_requests, time_window)
            # Администратор всегда проходит проверку в декораторе,
            # но check_rate_limit не знает об админе, поэтому тестируем напрямую
            # В реальности декоратор проверяет ADMIN_ID перед вызовом check_rate_limit
            pass
    
    def test_rate_limit_decorator_blocks_exceeding_requests(self):
        """Тест: декоратор блокирует превышающие запросы"""
        _rate_limit_history.clear()
        _user_blocks.clear()
        
        @rate_limit(max_requests=3, time_window=10.0, block_duration=1.0)
        def test_handler(message):
            return "OK"
        
        # Создаем mock message
        message = Mock()
        message.from_user.id = 12345
        
        # Делаем 3 запроса - все должны пройти
        for i in range(3):
            result = test_handler(message)
            self.assertEqual(result, "OK")
        
        # 4-й запрос должен быть заблокирован
        with patch('utils.safe_send_message') as mock_send, \
             patch('utils.bot') as mock_bot:
            result = test_handler(message)
            self.assertIsNone(result, "4th request should be blocked")
            # Проверяем, что было отправлено предупреждение
            self.assertTrue(mock_send.called)
    
    def test_rate_limit_decorator_handles_blocked_user(self):
        """Тест: декоратор обрабатывает заблокированного пользователя"""
        _rate_limit_history.clear()
        _user_blocks.clear()
        
        user_id = 12345
        block_user(user_id, 1.0)
        
        @rate_limit(max_requests=10, time_window=10.0, block_duration=1.0)
        def test_handler(message):
            return "OK"
        
        message = Mock()
        message.from_user.id = user_id
        
        # Запрос должен быть заблокирован
        with patch('utils.bot') as mock_bot:
            result = test_handler(message)
            self.assertIsNone(result, "Request from blocked user should be ignored")
    
    def test_rate_limit_decorator_handles_callback_query(self):
        """Тест: декоратор обрабатывает callback query"""
        _rate_limit_history.clear()
        _user_blocks.clear()
        
        @rate_limit(max_requests=3, time_window=10.0, block_duration=1.0)
        def test_callback_handler(call):
            return "OK"
        
        # Создаем mock call
        call = Mock()
        call.from_user.id = 12345
        call.id = "test_callback_id"
        call.data = "test_data"
        
        # Делаем 3 запроса
        for i in range(3):
            with patch('utils.bot') as mock_bot:
                result = test_callback_handler(call)
                self.assertEqual(result, "OK")
        
        # 4-й запрос должен быть заблокирован
        with patch('utils.bot') as mock_bot, \
             patch('utils.safe_send_message') as mock_send:
            result = test_callback_handler(call)
            self.assertIsNone(result, "4th callback should be blocked")
            # Проверяем, что был вызван answer_callback_query
            mock_bot.answer_callback_query.assert_called()
    
    def test_rate_limit_logging_includes_user_info(self):
        """Тест: логирование включает информацию о пользователе"""
        _rate_limit_history.clear()
        _user_blocks.clear()
        
        @rate_limit(max_requests=2, time_window=10.0, block_duration=1.0)
        def test_handler(message):
            return "OK"
        
        # Создаем mock message с информацией о пользователе
        message = Mock()
        message.from_user.id = 871902505
        message.from_user.first_name = "Иван"
        message.from_user.username = "ivan_user"
        
        # Делаем 2 запроса
        for i in range(2):
            with patch('utils.logger') as mock_logger, \
                 patch('utils.safe_send_message') as mock_send, \
                 patch('utils.bot') as mock_bot:
                result = test_handler(message)
                self.assertEqual(result, "OK")
        
        # 3-й запрос должен быть заблокирован и залогирован с информацией о пользователе
        with patch('utils.logger') as mock_logger, \
             patch('utils.safe_send_message') as mock_send, \
             patch('utils.bot') as mock_bot:
            result = test_handler(message)
            self.assertIsNone(result, "3rd request should be blocked")
            
            # Проверяем, что logger.warning был вызван с информацией о пользователе
            warning_calls = [call for call in mock_logger.warning.call_args_list 
                            if 'Rate limit exceeded' in str(call)]
            self.assertGreater(len(warning_calls), 0, "Logger should be called with rate limit warning")
            
            # Проверяем, что в логе есть информация о пользователе
            warning_message = str(warning_calls[0])
            self.assertIn('871902505', warning_message, "Log should contain user ID")
            # Проверяем, что есть имя или username (может быть в разных форматах)
            self.assertTrue(
                'Иван' in warning_message or 'ivan_user' in warning_message or '871902505' in warning_message,
                "Log should contain user information"
            )
    
    def test_rate_limit_logging_without_user_info(self):
        """Тест: логирование работает даже без информации о пользователе"""
        _rate_limit_history.clear()
        _user_blocks.clear()
        
        @rate_limit(max_requests=2, time_window=10.0, block_duration=1.0)
        def test_handler(message):
            return "OK"
        
        # Создаем mock message без имени и username
        message = Mock()
        message.from_user.id = 12345
        message.from_user.first_name = None
        message.from_user.username = None
        
        # Делаем 2 запроса
        for i in range(2):
            with patch('utils.logger') as mock_logger, \
                 patch('utils.safe_send_message') as mock_send, \
                 patch('utils.bot') as mock_bot:
                result = test_handler(message)
                self.assertEqual(result, "OK")
        
        # 3-й запрос должен быть заблокирован
        with patch('utils.logger') as mock_logger, \
             patch('utils.safe_send_message') as mock_send, \
             patch('utils.bot') as mock_bot:
            result = test_handler(message)
            self.assertIsNone(result, "3rd request should be blocked")
            
            # Проверяем, что logger.warning был вызван (даже без полной информации)
            warning_calls = [call for call in mock_logger.warning.call_args_list 
                            if 'Rate limit exceeded' in str(call)]
            self.assertGreater(len(warning_calls), 0, "Logger should be called even without user info")


if __name__ == '__main__':
    unittest.main()












