# Руководство по работе с N8N Webhooks

## Быстрый старт (без API ключа)

Для базовой интеграции через webhooks **API ключ НЕ нужен**! Достаточно создать workflow с webhook нодой.

## Создание Webhook workflow

### Шаг 1: Создать новый workflow

1. В N8N нажмите **"Start from scratch"** (или используйте AI workflow)
2. Откроется редактор workflow

### Шаг 2: Добавить Webhook ноду

**Как найти ноду Webhook:**

1. Нажмите на **"Add first step..."** (большой "+" в центре экрана)
2. В открывшейся панели:
   - **Вариант А:** Введите в поиск "webhook" и выберите ноду
   - **Вариант Б:** Найдите в категории "Core Nodes" или "Trigger Nodes"
3. Перетащите ноду **"Webhook"** на canvas или кликните на неё

**Альтернатива:** Используйте **"Build with AI"** и попросите: "Create a webhook workflow"

2. Настройте параметры:
   - **HTTP Method:** `POST` (по умолчанию)
   - **Path:** `telegram-events` (или любое другое имя)
   - **Response Mode:** `Respond When Last Node Finishes`
3. Нажмите **"Listen for Test Event"** или кнопку **"Test"**
4. **Скопируйте Webhook URL** - это ваш `N8N_WEBHOOK_URL`
   - Пример: `https://nikkronos.app.n8n.cloud/webhook/telegram-events`

### Шаг 3: Активировать workflow

1. Нажмите **"Save"** (Ctrl+S)
2. Переключите тумблер **"Active"** в положение ON (вверху справа)
3. Workflow готов принимать данные!

## Использование в коде

### Базовый пример

```python
from n8n.utils import send_to_n8n_webhook

# Отправка данных в webhook
data = {
    'event_type': 'new_subscription',
    'user_id': 123456,
    'timestamp': '2025-12-23T12:00:00'
}

# Используйте полный URL из N8N_WEBHOOK_URL
send_to_n8n_webhook('telegram-events', data)
```

### Или используйте готовую функцию

```python
from n8n.utils import send_telegram_event_to_n8n

event_data = {
    'user_id': 123456,
    'chat_id': -1001234567890,
    'timestamp': datetime.now().isoformat()
}

send_telegram_event_to_n8n('new_subscription', event_data)
```

## Где найти Settings и API ключ (если понадобится)

Если позже понадобится API ключ для управления workflow через API:

1. В N8N нажмите на иконку **Settings** (⚙️) в левом меню
2. Перейдите в раздел **"API"**
3. Нажмите **"Create API Key"**
4. Скопируйте ключ

**Примечание:** На триальном плане API ключ может быть недоступен. Для базовой интеграции через webhooks он не нужен.

## Тестирование webhook

### Через N8N

1. В webhook ноде нажмите **"Listen for Test Event"**
2. Отправьте тестовый запрос из вашего бота
3. Проверьте, что данные пришли в N8N

### Через curl (для тестирования)

```bash
curl -X POST https://nikkronos.app.n8n.cloud/webhook/telegram-events \
  -H "Content-Type: application/json" \
  -d '{"event_type": "test", "message": "Hello N8N!"}'
```

### Через Python

```python
import requests

url = "https://nikkronos.app.n8n.cloud/webhook/telegram-events"
data = {
    "event_type": "test",
    "message": "Hello N8N!"
}

response = requests.post(url, json=data)
print(response.status_code)
```

## Обработка данных в N8N

После получения данных в webhook, вы можете:

1. **Добавить ноду "Code"** для обработки данных
2. **Добавить ноду "Telegram"** для отправки уведомлений
3. **Добавить ноду "Google Sheets"** для сохранения данных
4. **Добавить любые другие ноды** для автоматизации

## Частые проблемы

### Webhook не получает данные

1. Проверьте, что workflow **активирован** (тумблер "Active" включен)
2. Проверьте правильность URL в `env_vars.txt`
3. Проверьте, что отправляете POST запрос с правильным Content-Type

### Ошибка 404

1. Проверьте правильность пути в webhook ноде
2. Убедитесь, что workflow сохранён и активирован
3. Проверьте URL в `N8N_WEBHOOK_URL`

---

**Последнее обновление:** 2025-12-23

