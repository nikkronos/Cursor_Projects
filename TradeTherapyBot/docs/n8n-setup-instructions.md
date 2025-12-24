# Инструкции по настройке N8N

## ✅ Что уже сделано

1. ✅ Создана структура папок для N8N
2. ✅ Созданы утилиты для интеграции (`n8n/utils.py`)
3. ✅ Создан пример workflow (`n8n/workflows/telegram-webhook-example.json`)
4. ✅ Обновлён `.gitignore` для защиты секретов
5. ✅ Обновлён `env_vars.example.txt` с N8N переменными
6. ✅ Создана документация (`docs/n8n-integration.md`)
7. ✅ Создан быстрый старт (`n8n/QUICK_START.md`)
8. ✅ Создана инструкция для ручной настройки (`docs/n8n-manual-setup.md`)

## 📝 Текущий статус

У вас уже создан workflow "Telegram Event Webhook Receiver" через AI. Теперь нужно настроить его вручную.

## 📋 Что нужно сделать вам

### Шаг 1: Установить расширения в Cursor (если ещё не установлены)

Откройте Extensions (`Ctrl+Shift+X`) и установите:
- **GitLens** - для работы с Git
- **Git History** - для просмотра истории
- **markdownlint** - для проверки Markdown

Подробнее: `docs/extensions-recommendations.md`

### Шаг 2: Создать первый workflow с Webhook

**Важно:** Для базовой интеграции через webhooks API ключ НЕ нужен! Нам нужен только webhook URL.

1. В N8N нажмите **"Start from scratch"** (или "Try an AI workflow")
2. Добавьте ноду **"Webhook"** (найдите в списке нод слева)
3. Настройте Webhook:
   - **HTTP Method:** POST
   - **Path:** `telegram-events` (или любое другое имя)
   - **Response Mode:** Respond When Last Node Finishes
4. Нажмите **"Listen for Test Event"** (или "Test" кнопку)
5. **Скопируйте Webhook URL** - это и есть ваш `N8N_WEBHOOK_URL`
   - Формат: `https://nikkronos.app.n8n.cloud/webhook/telegram-events`
6. Сохраните workflow (Ctrl+S или кнопка Save)
7. **Активируйте workflow** - переключите тумблер "Active" в положение ON (вверху справа)

**Примечание:** API ключ нужен только для управления workflow через API. Для базовой интеграции через webhooks он не требуется.

### Шаг 3: Настроить env_vars.txt

1. Откройте файл `env_vars.txt` в корне проекта
2. **Важно:** Используйте **Production URL**, а не Test URL!
   - В настройках webhook ноды выберите **"Production URL"** (не "Test URL")
   - Test URL (`/webhook-test/`) работает только во время тестирования
   - Production URL (`/webhook/`) работает постоянно
3. Добавьте следующие строки (замените на реальные значения):

```
# N8N Configuration
N8N_WEBHOOK_URL=https://nikkronos.app.n8n.cloud/webhook/telegram-events
```

**Важно:** 
- Замените URL на **Production URL**, который вы скопировали из webhook ноды
- Убедитесь, что используете `/webhook/`, а не `/webhook-test/`
- `N8N_API_KEY` и `N8N_API_URL` не обязательны для базовой интеграции через webhooks
- Если позже понадобится API ключ, он находится в **Settings** → **API** (может быть недоступен на триале)

**Важно:** 
- Файл `env_vars.txt` НЕ коммитится в Git (уже в `.gitignore`)
- Используйте `env_vars.example.txt` как шаблон

### Шаг 4: Активировать workflow

**Важно:** Workflow уже сохранён (видно "Saved" в правом верхнем углу)!

1. **Найдите тумблер "Active"** в правом верхнем углу (рядом с "Publish" и "Saved")
2. **Переключите тумблер "Active" в положение ON** (включено)
   - Когда включен: подсвечен (зелёный/синий)
   - Когда выключен: серый
3. После активации workflow готов принимать данные!

**Если не видите тумблер:**
- Попробуйте нажать **"Publish"** - это тоже активирует workflow
- Или через меню (три точки "...") → "Activate"

Подробная инструкция: `docs/n8n-activate-workflow.md`

### Шаг 5: Установить зависимости

Убедитесь, что установлен `requests`:

```powershell
cd "C:\Users\krono\OneDrive\Рабочий стол\Cursor_test"
pip install requests
```

### Шаг 6: Протестировать интеграцию

1. Запустите один из ботов (TradeTherapyBot или PastuhiBot)
2. Добавьте в код отправку события в N8N:

```python
from n8n.utils import send_telegram_event_to_n8n

# Пример: при новой подписке
event_data = {
    'user_id': user_id,
    'chat_id': chat_id,
    'timestamp': datetime.now().isoformat()
}

send_telegram_event_to_n8n('new_subscription', event_data)
```

3. Проверьте в N8N, что workflow получил данные

## 📚 Документация

- **Полная документация:** `docs/n8n-integration.md`
- **Быстрый старт:** `n8n/QUICK_START.md`
- **Утилиты:** `n8n/utils.py`
- **Пример workflow:** `n8n/workflows/telegram-webhook-example.json`

## 🔒 Безопасность

⚠️ **ВАЖНО:**
- Все API ключи хранить в `env_vars.txt` (НЕ коммитить!)
- Не хранить секреты в workflow файлах
- Использовать переменные окружения в N8N
- Регулярно обновлять API ключи

## 🚀 Следующие шаги

После настройки базовой интеграции:

1. Создать workflow для автоматических уведомлений
2. Интегрировать с Google Sheets
3. Настроить синхронизацию данных между ботами
4. Создать workflow для мониторинга ошибок
5. Настроить автоматический бэкап через N8N

---

**Последнее обновление:** 2025-12-23

