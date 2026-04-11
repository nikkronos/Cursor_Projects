# Быстрый старт с N8N

## Шаг 1: Создание Webhook workflow

**Важно:** Для базовой интеграции через webhooks API ключ НЕ нужен!

1. В N8N нажмите **"Start from scratch"**
2. Нажмите на **"Add first step..."** (большой "+" в центре)
3. **Найдите ноду Webhook:**
   - В поиске введите: **"webhook"**
   - Или найдите в категории "Core Nodes" / "Trigger Nodes"
   - Или используйте **"Build with AI"** и попросите создать webhook workflow
4. Добавьте ноду **"Webhook"** на canvas
3. Настройте Webhook:
   - **HTTP Method:** POST
   - **Path:** `telegram-events` (или любое другое имя)
   - **Response Mode:** Respond When Last Node Finishes
4. Нажмите **"Listen for Test Event"** или кнопку **"Test"**
5. **Скопируйте Webhook URL** - это ваш `N8N_WEBHOOK_URL`
   - Формат: `https://nikkronos.app.n8n.cloud/webhook/telegram-events`
6. Сохраните workflow (Ctrl+S)
7. **Активируйте workflow** - переключите тумблер "Active" в положение ON

## Шаг 2: Настройка env_vars.txt

Откройте файл `env_vars.txt` в корне проекта и добавьте:

```
# N8N Configuration
N8N_WEBHOOK_URL=https://nikkronos.app.n8n.cloud/webhook/telegram-events
```

**Важно:** 
- Замените URL на тот, который вы скопировали из webhook ноды
- `N8N_API_KEY` и `N8N_API_URL` не обязательны для базовой интеграции
- Если понадобится API ключ позже, он находится в **Settings** → **API** (может быть недоступен на триале)

## Шаг 3: Создание первого workflow

### 3.1. Создание Webhook workflow

1. В N8N нажмите **"New Workflow"**
2. Добавьте ноду **"Webhook"**
3. Настройте:
   - **HTTP Method:** POST
   - **Path:** `telegram-events` (или любое другое имя)
   - **Response Mode:** Respond When Last Node Finishes
4. Нажмите **"Listen for Test Event"**
5. Скопируйте **Webhook URL** (например: `https://your-instance.n8n.cloud/webhook/telegram-events`)

### 3.2. Добавление обработки данных

1. Добавьте ноду **"Code"** после Webhook
2. Вставьте код для обработки данных:
```javascript
// Получаем данные из webhook
const eventData = $input.all()[0].json;

// Обрабатываем событие
if (eventData.event_type === 'new_subscription') {
  return {
    json: {
      message: `Новая подписка: пользователь ${eventData.data.user_id}`,
      priority: 'info'
    }
  };
}

return { json: eventData };
```

### 3.3. Добавление отправки в Telegram

1. Добавьте ноду **"Telegram"**
2. Настройте:
   - **Operation:** Send Message
   - **Chat ID:** ваш chat ID
   - **Text:** `={{ $json.message }}`
3. Подключите credentials для Telegram (добавьте токен бота)

### 3.4. Активация workflow

1. Нажмите **"Save"**
2. Переключите тумблер **"Active"** в положение ON
3. Workflow готов к приёму данных!

## Шаг 4: Интеграция с ботом

### 4.1. Установка зависимостей

Убедитесь, что установлен `requests`:

```bash
pip install requests
```

### 4.2. Использование в коде бота

```python
from n8n.utils import send_telegram_event_to_n8n

# При новой подписке
event_data = {
    'user_id': user_id,
    'chat_id': chat_id,
    'timestamp': datetime.now().isoformat(),
    'subscription_days': days
}

send_telegram_event_to_n8n('new_subscription', event_data)
```

## Шаг 5: Тестирование

1. Запустите бота
2. Выполните действие, которое должно отправить событие в N8N
3. Проверьте в N8N, что workflow получил данные
4. Проверьте, что сообщение отправлено в Telegram

## Полезные ссылки

- [N8N Документация](https://docs.n8n.io/)
- [N8N Community](https://community.n8n.io/)
- [N8N Workflow Templates](https://n8n.io/workflows/)

## Следующие шаги

- Создать workflow для автоматических уведомлений
- Интегрировать с Google Sheets
- Настроить синхронизацию данных
- Создать workflow для мониторинга ошибок

---

**Последнее обновление:** 2025-12-23

