# Развертывание (Deployment)

## Текущее окружение
- **Сервер:** Локальный запуск (Windows PowerShell) или Timeweb Cloud.
- **База данных:** Timeweb Managed PostgreSQL.

## Инструкция по запуску
1. Убедиться, что установлен Python 3.x.
2. Установить зависимости:
   ```bash
   pip install pyTelegramBotAPI psycopg2-binary apscheduler python-dotenv
   ```
3. Создать файл `env_vars.txt` в корне проекта и заполнить переменные:
   ```
   BOT_TOKEN=ваш_токен
   ADMIN_ID=ваш_ид
   GROUP_CHAT_ID=ид_группы
   DB_NAME=...
   DB_USER=...
   DB_PASSWORD=...
   DB_HOST=...
   ```
4. Запустить бота:
   ```bash
   python bot.py
   ```

## Мониторинг
- Логи пишутся в консоль и в файл `logs/bot.log`.
- При перезапуске сервера (или ПК) бот нужно запускать вручную (если не настроен systemd/Docker).
