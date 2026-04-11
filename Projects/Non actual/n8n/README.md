# N8N Workflows

Эта папка содержит экспортированные workflow из N8N и документацию по их использованию.

## Структура

```
n8n/
├── workflows/              # Экспортированные workflow (JSON файлы)
├── credentials/            # Шаблоны для credentials (без секретов)
└── README.md              # Этот файл
```

## Как использовать

### Экспорт workflow из N8N

1. Откройте workflow в N8N
2. Нажмите на меню (три точки) → "Download"
3. Сохраните JSON файл в папку `workflows/`
4. Обновите документацию ниже

### Импорт workflow в N8N

1. Откройте N8N
2. Нажмите "Import from File"
3. Выберите JSON файл из папки `workflows/`
4. Настройте credentials (API ключи, токены и т.д.)

## Workflow

### 1. Telegram Webhook Receiver

**Файл:** `workflows/telegram-webhook.json`

**Описание:** Принимает webhook от Telegram ботов и обрабатывает события

**Использование:**
- Подключить к TradeTherapyBot или PastuhiBot
- Отправлять события на webhook URL из N8N

### 2. Автоматические уведомления

**Файл:** `workflows/notifications.json`

**Описание:** Отправляет автоматические уведомления в Telegram при определенных событиях

**Использование:**
- Настроить триггеры (webhook, schedule, и т.д.)
- Настроить формат сообщений

### 3. Синхронизация с Google Sheets

**Файл:** `workflows/sheets-sync.json`

**Описание:** Синхронизирует данные между ботами и Google Sheets

**Использование:**
- Подключить Google Sheets credentials
- Настроить маппинг данных

## Credentials

Все credentials хранятся в N8N и НЕ коммитятся в Git.

Шаблоны для credentials находятся в папке `credentials/` (без реальных значений).

## Безопасность

⚠️ **ВАЖНО:**
- Никогда не коммитить файлы с реальными API ключами
- Все секреты хранить в N8N credentials или в `env_vars.txt`
- Использовать переменные окружения в workflow

---

**Последнее обновление:** 2025-12-23























