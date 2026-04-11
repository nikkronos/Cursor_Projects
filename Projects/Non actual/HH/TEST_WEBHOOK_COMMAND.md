# Команда для тестирования Webhook в PowerShell

## Вариант 1: Использовать скрипт (рекомендуется)

```powershell
cd "C:\Users\krono\OneDrive\Рабочий стол\Cursor_test\HeadHunterAutomation"
.\test_webhook.ps1
```

## Вариант 2: Команда напрямую

```powershell
$body = '{"event_type":"hh_apply","timestamp":"2025-12-25T12:00:00","data":{"user_id":123,"username":"test","command":"hh_apply"}}'
Invoke-WebRequest -Uri "https://nikkronos.app.n8n.cloud/webhook/hh-apply" -Method POST -ContentType "application/json" -Body $body
```

## Вариант 3: Использовать curl.exe (если установлен)

```powershell
curl.exe -X POST https://nikkronos.app.n8n.cloud/webhook/hh-apply -H "Content-Type: application/json" -d "{\"event_type\":\"hh_apply\",\"data\":{\"user_id\":123,\"username\":\"test\"}}"
```

## Что проверить после выполнения

1. В N8N откройте workflow "HeadHunter Automation"
2. Перейдите на вкладку **"Executions"**
3. Должно появиться новое выполнение

Если выполнение появилось - webhook работает! ✅
Если не появилось - проверьте:
- Workflow активирован?
- Production URL правильный?
- Нет ли ошибок в выполнении?





















