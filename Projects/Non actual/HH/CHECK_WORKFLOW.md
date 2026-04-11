# Проверка Workflow в N8N

## Критически важные проверки

### 1. Workflow активирован?

**Проверка:**
- Откройте workflow "HeadHunter Automation" в N8N
- В правом верхнем углу найдите тумблер **"Active"**
- Он должен быть **ВКЛЮЧЕН** (зелёный/синий цвет)

**Если выключен:**
- Переключите тумблер в положение ON
- Должно появиться сообщение "Workflow activated"

### 2. Правильный Webhook URL?

**Проверка:**
1. Откройте ноду **"Webhook"** в workflow
2. Нажмите **"Listen for Test Event"** (или кнопку "Test")
3. Скопируйте **Production URL** (НЕ Test URL!)
   - ✅ Правильно: `https://nikkronos.app.n8n.cloud/webhook/hh-apply`
   - ❌ Неправильно: `https://nikkronos.app.n8n.cloud/webhook-test/hh-apply`

4. Проверьте на сервере в `/opt/testn8n/env_vars.txt`:
   ```bash
   cat /opt/testn8n/env_vars.txt | grep N8N_WEBHOOK_URL
   ```
   
   Должно быть:
   ```env
   N8N_WEBHOOK_URL=https://nikkronos.app.n8n.cloud/webhook/hh-apply
   ```

### 3. Тест Webhook напрямую

**Проверка через curl:**

В PowerShell выполните:

```powershell
curl -X POST https://nikkronos.app.n8n.cloud/webhook/hh-apply `
  -H "Content-Type: application/json" `
  -d '{\"event_type\":\"hh_apply\",\"data\":{\"user_id\":123,\"username\":\"test\"}}'
```

**Ожидаемый результат:**
- В N8N на вкладке **"Executions"** должно появиться новое выполнение
- Если появилось - webhook работает!

### 4. Проверка логов бота

На сервере:

```bash
journalctl -u testn8n.service -n 50 --no-pager
```

Ищите строки:
- `Событие 'hh_apply' успешно отправлено в N8N` ✅
- `Ошибка при отправке события в N8N` ❌

### 5. Проверка Code Node

Убедитесь, что Code node "Check Access" обновлён:
- Должен фильтровать по `event_type === 'hh_apply'`
- Если workflow импортирован из старого JSON, обновите Code node вручную

### 6. Проверка HTTP Request Node

**Настройки ноды "Start HH Automation":**
- **Method:** POST
- **URL:** `http://127.0.0.1:5000/run`
- **Headers:**
  - **Name:** `Authorization`
  - **Value:** `Bearer _1Qxe0GPbojVA2bbgyVdoS4GmWTx40Aey4lt2RcGO7c`

**Важно:** 
- Если используется `{{$env.HH_API_TOKEN}}`, убедитесь, что переменная создана в N8N:
  - Settings → Variables
  - Добавьте `HH_API_TOKEN` = `_1Qxe0GPbojVA2bbgyVdoS4GmWTx40Aey4lt2RcGO7c`

## Пошаговая диагностика

### Шаг 1: Проверка активации
```
Workflow → Тумблер "Active" → Должен быть ON
```

### Шаг 2: Проверка Webhook
```
Webhook node → Production URL → Скопировать
Сравнить с env_vars.txt на сервере
```

### Шаг 3: Тест через curl
```
Отправить POST запрос → Проверить Executions
```

### Шаг 4: Проверка логов
```
Логи бота → Искать "успешно отправлено" или "ошибка"
```

### Шаг 5: Проверка выполнения
```
Executions → Должно быть новое выполнение
```

## Частые проблемы

### Проблема: Executions пустое

**Причины:**
1. Workflow не активирован
2. Webhook URL неправильный (Test вместо Production)
3. Запрос не доходит до N8N (проблемы с сетью)

**Решение:**
1. Активируйте workflow
2. Используйте Production URL
3. Проверьте через curl

### Проблема: Запрос доходит, но HTTP Request падает

**Причины:**
1. Flask API сервер не запущен
2. Неправильный токен
3. N8N не может достучаться до localhost:5000

**Решение:**
1. Запустите API сервер: `python scripts\hh_api_server.py`
2. Проверьте токен
3. Если N8N на другом сервере, используйте IP вместо localhost

---

**Если ничего не помогает:**
1. Пересоздайте workflow с нуля
2. Используйте Test URL для отладки (но помните, что он работает только во время тестирования)
3. Проверьте логи N8N (если есть доступ)





















