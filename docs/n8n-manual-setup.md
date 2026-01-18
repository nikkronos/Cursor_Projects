# Ручная настройка N8N Workflow (без AI)

Пошаговая инструкция для ручной настройки workflow в N8N, когда AI промпты ограничены.

## Текущий статус

У вас уже создан workflow "Telegram Event Webhook Receiver" с двумя нодами:
- **Telegram Webhook** (триггер)
- **Respond to Telegram** (ответ)

## Шаг 1: Настройка Webhook ноды

1. **Кликните на ноду "Telegram Webhook"**
2. В правой панели настройте:
   - **HTTP Method:** `POST` (уже установлен)
   - **Path:** `telegram-events` (или оставьте как есть)
   - **Response Mode:** `Respond When Last Node Finishes`
3. **Выберите "Production URL"** (не Test URL!)
   - В разделе "Webhook URLs" переключите на "Production URL"
4. **Скопируйте Production URL** из поля "Webhook URL"
   - Формат: `https://nikkronos.app.n8n.cloud/webhook/telegram-events`
   - ⚠️ **НЕ используйте Test URL** (`/webhook-test/`) - он работает только во время тестирования!
5. Сохраните этот URL - он понадобится для `env_vars.txt`

**Важно:** Production URL работает только если workflow активирован (тумблер "Active" = ON)

## Шаг 2: Настройка Response ноды

1. **Кликните на ноду "Respond to Telegram"**
2. В правой панели настройте:
   - **Response Code:** `200` (OK)
   - **Response Body:** `OK` или `{"status": "received"}`
3. Это подтверждает получение данных

## Шаг 3: Добавление обработки данных (опционально)

### Добавить ноду Code для обработки

1. Нажмите на **"+"** справа от ноды "Respond to Telegram"
2. В поиске введите: **"code"** или **"function"**
3. Выберите ноду **"Code"** или **"Function"**
4. Вставьте код:

```javascript
// Получаем данные из webhook
const eventData = $input.all()[0].json;

// Логируем для отладки
console.log('Received event:', eventData);

// Можно обработать данные
if (eventData.event_type === 'new_subscription') {
  // Логика обработки
}

// Передаём данные дальше
return { json: eventData };
```

### Добавить ноду Telegram для уведомлений (опционально)

1. После ноды Code нажмите **"+"**
2. В поиске введите: **"telegram"**
3. Выберите ноду **"Telegram"**
4. Настройте:
   - **Operation:** `Send Message`
   - **Chat ID:** ваш Telegram chat ID
   - **Text:** `={{ $json.event_type }}: {{ JSON.stringify($json.data) }}`
5. Нажмите **"Create New Credential"** для добавления токена бота

## Шаг 4: Активация workflow

**Важно:** Workflow уже сохранён (видно "Saved" в правом верхнем углу)!

1. **Найдите тумблер "Active"** - он находится в **правом верхнем углу**, рядом с кнопками "Publish" и "Saved"
2. **Переключите тумблер "Active"** в положение **ON** (включено)
   - Когда тумблер включен, он будет подсвечен (обычно зелёным или синим)
   - Когда выключен - серый
3. После активации workflow готов принимать данные!

**Если не видите тумблер "Active":**
- Он может быть в выпадающем меню (три точки "..." справа)
- Или в настройках workflow (Settings)
- Или попробуйте нажать "Publish" - это тоже активирует workflow

## Шаг 5: Тестирование

### Через curl (в PowerShell)

```powershell
$url = "https://nikkronos.app.n8n.cloud/webhook/telegram-events"
$body = @{
    event_type = "test"
    message = "Hello N8N!"
} | ConvertTo-Json

Invoke-RestMethod -Uri $url -Method Post -Body $body -ContentType "application/json"
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
print(response.text)
```

## Шаг 6: Настройка env_vars.txt

Добавьте в `env_vars.txt`:

```
# N8N Configuration
N8N_WEBHOOK_URL=https://nikkronos.app.n8n.cloud/webhook/telegram-events
```

Замените URL на тот, который скопировали из webhook ноды.

## Полезные ноды для изучения

### Основные ноды:

1. **Webhook** - приём данных извне
2. **HTTP Request** - отправка HTTP запросов
3. **Code / Function** - выполнение JavaScript кода
4. **Telegram** - работа с Telegram API
5. **Google Sheets** - работа с Google Sheets
6. **IF** - условная логика
7. **Switch** - множественные условия
8. **Set** - установка значений
9. **Wait** - задержка выполнения

### Где найти ноды:

1. Нажмите **"+"** между нодами
2. В поиске введите название ноды
3. Или просмотрите категории:
   - **Core Nodes** - основные ноды
   - **Trigger Nodes** - триггеры (webhook, schedule, и т.д.)
   - **Communication** - Telegram, Email, и т.д.
   - **Data** - работа с данными

## Следующие шаги

1. ✅ Настроить webhook URL в `env_vars.txt`
2. ⬜ Добавить обработку данных (нода Code)
3. ⬜ Добавить отправку уведомлений (нода Telegram)
4. ⬜ Интегрировать с ботом (использовать `n8n/utils.py`)

---

**Последнее обновление:** 2025-12-23

