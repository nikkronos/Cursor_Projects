# Разница между Test URL и Production URL в N8N

## Два типа Webhook URL

В N8N есть два типа webhook URL:

### 1. **Test URL** (Тестовый URL)
- Формат: `https://nikkronos.app.n8n.cloud/webhook-test/telegram-events`
- **Назначение:** Для тестирования workflow во время разработки
- **Особенности:**
  - Работает только когда нажата кнопка **"Listen for test event"**
  - После закрытия тестового режима перестаёт работать
  - Не требует активации workflow
  - Удобно для отладки

### 2. **Production URL** (Продакшн URL)
- Формат: `https://nikkronos.app.n8n.cloud/webhook/telegram-events`
- **Назначение:** Для реальной работы в продакшене
- **Особенности:**
  - Работает постоянно (когда workflow активирован)
  - Требует активации workflow (тумблер "Active" должен быть ON)
  - Используется для реальной интеграции с ботами

## Какую выбрать?

### Для интеграции с ботами → **Production URL**

✅ **Используйте Production URL** (`/webhook/telegram-events`), потому что:
- Нужна постоянная работа
- Бот должен отправлять данные 24/7
- Не нужно каждый раз нажимать "Listen for test event"

### Для тестирования → **Test URL**

✅ **Используйте Test URL** (`/webhook-test/telegram-events`), когда:
- Тестируете workflow
- Отлаживаете логику
- Проверяете, что данные приходят правильно

## Настройка для продакшена

1. **Выберите "Production URL"** в настройках webhook ноды
2. **Скопируйте Production URL:** `https://nikkronos.app.n8n.cloud/webhook/telegram-events`
3. **Добавьте в `env_vars.txt`:**
   ```
   N8N_WEBHOOK_URL=https://nikkronos.app.n8n.cloud/webhook/telegram-events
   ```
4. **Активируйте workflow:**
   - Нажмите "Save" (Ctrl+S)
   - Переключите тумблер "Active" в положение ON
5. **Готово!** Webhook будет принимать данные постоянно

## Важно!

⚠️ **Production URL работает только если:**
- Workflow **сохранён** (Save)
- Workflow **активирован** (тумблер "Active" = ON)

Если workflow не активирован, Production URL не будет работать!

---

**Последнее обновление:** 2025-12-23























