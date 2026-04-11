# Быстрый старт: HeadHunter Automation через N8N

## Шаг 1: Установка зависимостей

```powershell
cd HeadHunterAutomation
pip install -r requirements.txt
```

## Шаг 2: Настройка env_vars.txt

Добавьте в `env_vars.txt` (в корне проекта):

```env
# HeadHunter Automation
HH_COVER_LETTER=Доброго времени суток.\n\nПоследние два года...

# HH API Server
HH_API_TOKEN=your_secure_token_here
HH_API_PORT=5000

# N8N Webhook (для бота)
N8N_WEBHOOK_URL=https://nikkronos.app.n8n.cloud/webhook/hh-apply
```

## Шаг 3: Запуск API сервера

```powershell
run_api_server.bat
```

Или вручную:
```powershell
python scripts\hh_api_server.py
```

Сервер запустится на `http://127.0.0.1:5000`

## Шаг 4: Настройка N8N

1. Откройте N8N: https://nikkronos.app.n8n.cloud
2. Импортируйте workflow: **Add workflow** → **Import from File** → выберите `n8n_workflow.json`
3. Настройте:
   - **Webhook node:** Скопируйте Production URL
   - **HTTP Request node:** Убедитесь, что URL = `http://127.0.0.1:5000/run`
   - **Telegram node:** Добавьте credentials вашего бота
   - **Code node (Check Access):** Добавьте ваш Telegram ID в `adminIds`
4. Активируйте workflow (переключите тумблер "Active")

## Шаг 5: Использование

1. **Залогиньтесь на hh.ru** в браузере
2. **Выполните поиск** "project assistant" и нажмите "Найти"
3. **Отправьте команду** `/hh_apply` в Telegram бот
4. **Получите уведомление** о результате

## Проверка работы

```powershell
# Проверка здоровья API
curl http://127.0.0.1:5000/health

# Статус выполнения
curl http://127.0.0.1:5000/status
```

## Устранение проблем

- **"Connection refused"** → Убедитесь, что API сервер запущен
- **"Unauthorized"** → Проверьте `HH_API_TOKEN` в env_vars.txt и N8N
- **Бот не отвечает** → Проверьте `N8N_WEBHOOK_URL` и активацию workflow

Подробная инструкция: [N8N_SETUP.md](N8N_SETUP.md)





















