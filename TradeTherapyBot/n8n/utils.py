"""
Утилиты для интеграции с N8N

Этот модуль содержит функции для отправки данных в N8N webhooks
и работы с N8N API.
"""

import os
import requests
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv(dotenv_path='env_vars.txt')

logger = logging.getLogger(__name__)


def get_n8n_webhook_url(workflow_name: Optional[str] = None) -> Optional[str]:
    """
    Получить URL webhook для конкретного workflow
    
    Args:
        workflow_name: Имя workflow в N8N (опционально, если указан полный URL в N8N_WEBHOOK_URL)
        
    Returns:
        URL webhook или None, если не настроен
    """
    base_url = os.getenv('N8N_WEBHOOK_URL')
    if not base_url:
        logger.warning("N8N_WEBHOOK_URL не настроен в env_vars.txt")
        return None
    
    # Если workflow_name не указан, возвращаем полный URL как есть
    if not workflow_name:
        return base_url
    
    # Если указан workflow_name, добавляем его к базовому URL
    # Формат: https://your-instance.n8n.cloud/webhook/workflow-name
    if base_url.endswith('/'):
        return f"{base_url}{workflow_name}"
    return f"{base_url}/{workflow_name}"


def send_to_n8n_webhook(workflow_name: str, data: Dict[str, Any], timeout: int = 10) -> bool:
    """
    Отправить данные в N8N webhook
    
    Args:
        workflow_name: Имя workflow в N8N
        data: Данные для отправки
        timeout: Таймаут запроса в секундах
        
    Returns:
        True если успешно, False в противном случае
    """
    webhook_url = get_n8n_webhook_url(workflow_name)
    if not webhook_url:
        return False
    
    try:
        response = requests.post(
            webhook_url,
            json=data,
            timeout=timeout
        )
        response.raise_for_status()
        logger.info(f"Данные успешно отправлены в N8N workflow: {workflow_name}")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при отправке данных в N8N: {e}")
        return False


def send_telegram_event_to_n8n(event_type: str, event_data: Dict[str, Any]) -> bool:
    """
    Отправить событие Telegram бота в N8N
    
    Args:
        event_type: Тип события (например, 'new_subscription', 'subscription_expired')
        event_data: Данные события
        
    Returns:
        True если успешно, False в противном случае
    """
    data = {
        'event_type': event_type,
        'timestamp': event_data.get('timestamp'),
        'data': event_data
    }
    
    return send_to_n8n_webhook('telegram-events', data)


def send_notification_to_n8n(message: str, priority: str = 'info', metadata: Optional[Dict] = None) -> bool:
    """
    Отправить уведомление в N8N для обработки
    
    Args:
        message: Текст уведомления
        priority: Приоритет (info, warning, error)
        metadata: Дополнительные метаданные
        
    Returns:
        True если успешно, False в противном случае
    """
    data = {
        'message': message,
        'priority': priority,
        'metadata': metadata or {}
    }
    
    return send_to_n8n_webhook('notifications', data)

