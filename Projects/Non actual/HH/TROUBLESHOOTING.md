# Устранение проблем: HeadHunter Automation через N8N

## Проблема: В Executions ничего нет

### Причина 1: Используется Test URL вместо Production URL

**Симптомы:**
- Бот отвечает, но в Executions ничего не появляется
- В `env_vars.txt` указан `/webhook-test/`

**Решение:**
1. Откройте Webhook node в N8N
2. Скопируйте **Production URL** (не Test URL!)
3. Обновите `env_vars.txt`:
   ```env
   N8N_WEBHOOK_URL=https://nikkronos.app.n8n.cloud/webhook/hh-apply
   ```
4. Обновите `env_vars.txt` на сервере
5. Перезапустите бота: `systemctl restart testn8n.service`

### Причина 2: Workflow не активирован

**Симптомы:**
- Webhook URL правильный, но ничего не происходит

**Решение:**
1. В N8N откройте workflow "HeadHunter Automation"
2. Убедитесь, что тумблер **"Active"** включен (зелёный/синий)
3. Если выключен - включите его

### Причина 3: Бот не обновлён на сервере

**Симптомы:**
- Команда `/hh_apply` обрабатывается как обычное сообщение
- Бот отвечает через `handle_all_messages`, а не через `handle_hh_apply`

**Решение:**
1. Обновите `handlers/user.py` на сервере:
   ```powershell
   scp TestN8N\handlers\user.py root@81.200.146.32:/opt/testn8n/handlers/user.py
   ```
2. Перезапустите бота:
   ```bash
   systemctl restart testn8n.service
   ```

## Проблема: Предупреждение на ноде "Start HH Automation"

**Симптомы:**
- Красный треугольник с восклицательным знаком на ноде

**Возможные причины:**
1. Не настроен заголовок Authorization
2. Неправильный URL
3. Credentials не настроены

**Решение:**
1. Откройте ноду "Start HH Automation"
2. Проверьте URL: `http://127.0.0.1:5000/run`
3. В разделе **Headers** добавьте:
   - **Name:** `Authorization`
   - **Value:** `Bearer _1Qxe0GPbojVA2bbgyVdoS4GmWTx40Aey4lt2RcGO7c`
4. Сохраните ноду

## Проблема: "Connection refused" в N8N

**Симптомы:**
- Ошибка при выполнении HTTP Request node
- "Connection refused" или "ECONNREFUSED"

**Решение:**
1. Убедитесь, что Flask API сервер запущен:
   ```powershell
   python scripts\hh_api_server.py
   ```
2. Проверьте, что сервер работает:
   ```powershell
   curl http://127.0.0.1:5000/health
   ```
3. Если сервер на другом компьютере, используйте IP адрес вместо `127.0.0.1`

## Проблема: "Unauthorized" в API

**Симптомы:**
- HTTP Request возвращает 401 Unauthorized

**Решение:**
1. Проверьте `HH_API_TOKEN` в `env_vars.txt`
2. Убедитесь, что токен в N8N совпадает с токеном в `env_vars.txt`
3. Проверьте формат заголовка: `Bearer TOKEN` (с пробелом!)

## Проверка работы workflow

### Шаг 1: Проверка Webhook

1. Откройте Webhook node
2. Нажмите **"Listen for Test Event"**
3. Скопируйте Test URL
4. Отправьте POST запрос:
   ```powershell
   curl -X POST https://nikkronos.app.n8n.cloud/webhook-test/hh-apply -H "Content-Type: application/json" -d '{"event_type":"hh_apply","data":{"user_id":123}}'
   ```
5. Проверьте, появилось ли выполнение в Executions

### Шаг 2: Проверка API сервера

```powershell
# Health check
curl http://127.0.0.1:5000/health

# Статус
curl http://127.0.0.1:5000/status
```

### Шаг 3: Проверка бота

1. Отправьте `/hh_apply` в Telegram бот
2. Проверьте логи бота на сервере:
   ```bash
   journalctl -u testn8n.service -n 50
   ```
3. Убедитесь, что событие отправлено в N8N

## Логи для отладки

### Логи Flask API сервера
```
HeadHunterAutomation/logs/hh_api_*.log
```

### Логи Python-скрипта
```
HeadHunterAutomation/logs/hh_automation_*.log
```

### Логи бота на сервере
```bash
journalctl -u testn8n.service -f
```

---

**Если проблема не решена:**
1. Проверьте все логи
2. Убедитесь, что все сервисы запущены
3. Проверьте настройки в N8N
4. Проверьте `env_vars.txt` на сервере





















