"""
Тесты для проверки структуры handlers после рефакторинга.
Проверяет, что все модули импортируются и обработчики регистрируются.
"""
import pytest


class TestHandlersImports:
    """Тесты для импорта handlers модулей"""
    
    def test_import_handlers_package(self):
        """Тест: импорт пакета handlers работает"""
        import handlers
        assert handlers is not None
        assert hasattr(handlers, '__path__')  # Это пакет
    
    def test_import_handlers_modules(self):
        """Тест: все модули handlers импортируются"""
        from handlers import helpers
        from handlers import admin
        from handlers import user
        from handlers import callbacks
        from handlers import join_requests
        
        assert helpers is not None
        assert admin is not None
        assert user is not None
        assert callbacks is not None
        assert join_requests is not None
    
    def test_handlers_all_exported(self):
        """Тест: все модули экспортируются через __all__"""
        import handlers
        assert hasattr(handlers, '__all__')
        expected_modules = ['helpers', 'admin', 'user', 'callbacks', 'join_requests']
        for module_name in expected_modules:
            assert module_name in handlers.__all__
            assert hasattr(handlers, module_name)


class TestHandlersHelpers:
    """Тесты для helpers модуля"""
    
    def test_helpers_functions_exist(self):
        """Тест: основные helper функции существуют"""
        from handlers.helpers import (
            send_main_menu,
            send_admin_menu,
            send_users_filter_menu,
            send_payment_info,
            send_answers_to_admin,
            TARIFF_QUESTIONS
        )
        
        assert callable(send_main_menu)
        assert callable(send_admin_menu)
        assert callable(send_users_filter_menu)
        assert callable(send_payment_info)
        assert callable(send_answers_to_admin)
        assert isinstance(TARIFF_QUESTIONS, list)
        assert len(TARIFF_QUESTIONS) > 0


class TestHandlersRegistration:
    """Тесты для регистрации обработчиков"""
    
    def test_handlers_registered_after_import(self):
        """Тест: обработчики регистрируются после импорта"""
        # Импортируем handlers для регистрации декораторов
        import handlers
        
        # Проверяем, что bot доступен и обработчики зарегистрированы
        try:
            from loader import bot
            # Проверяем, что есть зарегистрированные обработчики
            # (точное количество может варьироваться, но должно быть > 0)
            total_handlers = (
                len(bot.message_handlers) +
                len(bot.callback_query_handlers) +
                len(bot.chat_join_request_handlers) +
                len(bot.chat_member_handlers)
            )
            assert total_handlers > 0, "Должен быть хотя бы один зарегистрированный обработчик"
        except (ImportError, AttributeError):
            # Если bot не инициализирован (нет токена), это нормально для тестов
            pytest.skip("Bot не инициализирован (нет токена), пропускаем тест регистрации")


class TestHandlersStructure:
    """Тесты для структуры handlers модулей"""
    
    def test_admin_handlers_exist(self):
        """Тест: админские обработчики существуют"""
        import handlers.admin as admin_module
        
        # Проверяем наличие основных админских функций
        assert hasattr(admin_module, 'handle_backup_command')
        assert hasattr(admin_module, 'handle_admin_command')
        assert hasattr(admin_module, 'handle_manage_days_menu')
    
    def test_user_handlers_exist(self):
        """Тест: пользовательские обработчики существуют"""
        import handlers.user as user_module
        
        # Проверяем наличие основных пользовательских функций
        assert hasattr(user_module, 'handle_start')
        assert hasattr(user_module, 'send_tariffs')
        assert hasattr(user_module, 'send_rules')
        assert hasattr(user_module, 'handle_status_command')
    
    def test_callbacks_exist(self):
        """Тест: callback обработчики существуют"""
        import handlers.callbacks as callbacks_module
        
        # Проверяем наличие основных callback функций
        assert hasattr(callbacks_module, 'callback_confirm_payment')
        assert hasattr(callbacks_module, 'callback_reject_payment')
        assert hasattr(callbacks_module, 'callback_confirm_tariff')
    
    def test_join_requests_exist(self):
        """Тест: обработчики заявок существуют"""
        import handlers.join_requests as join_module
        
        # Проверяем наличие функций для обработки заявок
        assert hasattr(join_module, 'handle_join_request')
        assert hasattr(join_module, 'handle_chat_member_update')












