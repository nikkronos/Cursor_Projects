# Следующие шаги после настройки N8N

## ✅ Что уже сделано

1. ✅ Создан workflow "Telegram Event Webhook Receiver"
2. ✅ Настроен Production URL: `https://nikkronos.app.n8n.cloud/webhook/telegram-events`
3. ✅ Workflow активирован (видна кнопка "Deactivate", тест вернул "OK")
4. ✅ URL добавлен в `env_vars.txt`

## 🚀 Следующие шаги

### Шаг 1: Интегрировать с ботом

Теперь можно отправлять данные из ваших ботов в N8N.

#### Для TradeTherapyBot:

Добавьте в код отправку событий в N8N:

```python
from n8n.utils import send_telegram_event_to_n8n
from datetime import datetime

# Пример: при новой подписке
def on_new_subscription(user_id, chat_id, days):
    event_data = {
        'user_id': user_id,
        'chat_id': chat_id,
        'subscription_days': days,
        'timestamp': datetime.now().isoformat()
    }
    
    # Отправляем в N8N
    send_telegram_event_to_n8n('new_subscription', event_data)
```

#### Для PastuhiBot:

Аналогично можно отправлять события о копировании каналов:

```python
from n8n.utils import send_telegram_event_to_n8n

# Пример: при копировании сообщения
def on_message_copied(channel_id, message_id):
    event_data = {
        'channel_id': channel_id,
        'message_id': message_id,
        'timestamp': datetime.now().isoformat()
    }
    
    send_telegram_event_to_n8n('message_copied', event_data)
```

### Шаг 2: Добавить обработку данных в N8N

Сейчас workflow просто отвечает "OK". Можно добавить обработку:

1. **Добавить ноду Code** между "Telegram Webhook" и "Respond to Telegram"
2. Вставить код для обработки:

```javascript
// Получаем данные из webhook
const eventData = $input.all()[0].json;

// Логируем
console.log('Received event:', eventData);

// Обрабатываем разные типы событий
if (eventData.event_type === 'new_subscription') {
  // Логика для новой подписки
  return {
    json: {
      ...eventData,
      processed: true,
      message: `Новая подписка: пользователь ${eventData.data.user_id}`
    }
  };
}

// Передаём данные дальше
return { json: eventData };
```

### Шаг 3: Добавить уведомления в Telegram

1. Добавьте ноду **"Telegram"** после ноды Code
2. Настройте:
   - **Operation:** Send Message
   - **Chat ID:** ваш Telegram chat ID
   - **Text:** `={{ $json.message }}`
3. Подключите credentials для Telegram (добавьте токен бота)

### Шаг 4: Добавить синхронизацию с Google Sheets (опционально)

1. Добавьте ноду **"Google Sheets"**
2. Настройте:
   - **Operation:** Append Row
   - **Spreadsheet ID:** ваш spreadsheet ID
   - **Range:** название листа
   - **Values:** данные из события

## Полезные типы событий для отправки

### TradeTherapyBot:
- `new_subscription` - новая подписка
- `subscription_expired` - подписка истекла
- `user_banned` - пользователь забанен
- `user_unbanned` - пользователь разбанен

### PastuhiBot:
- `message_copied` - сообщение скопировано
- `channel_added` - канал добавлен
- `channel_removed` - канал удалён

## Тестирование интеграции

После добавления кода в бот:

1. Запустите бота
2. Выполните действие, которое должно отправить событие
3. Проверьте в N8N:
   - Перейдите на вкладку **"Executions"**
   - Должно появиться новое выполнение workflow
   - Кликните на него, чтобы увидеть данные

## Документация

- Полная интеграция: `docs/n8n-integration.md`
- Утилиты: `n8n/utils.py`
- Ручная настройка: `docs/n8n-manual-setup.md`

---

**Последнее обновление:** 2025-12-23

