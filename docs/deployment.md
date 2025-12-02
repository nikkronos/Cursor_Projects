# Развертывание (Deployment)

## Текущее окружение
- **Сервер:** Локальный запуск (Windows PowerShell) или Timeweb Cloud/VPS.
- **База данных:** SQLite (файл `bot.db` в корне проекта). **Не требует отдельного сервера БД.**

## Инструкция по запуску
1. Убедиться, что установлен Python 3.7+.
2. Установить зависимости:
   ```bash
   pip install -r requirements.txt
   ```
   Или вручную:
   ```bash
   pip install pyTelegramBotAPI python-dotenv APScheduler
   ```
3. Создать файл `env_vars.txt` в корне проекта и заполнить переменные:
   ```
   BOT_TOKEN=ваш_токен_бота
   ADMIN_ID=ваш_telegram_id
   GROUP_CHAT_ID=id_закрытой_группы
   ```
   **Примечание:** Больше не нужны параметры `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST` (используется SQLite).
4. Запустить бота:
   ```bash
   python main.py
   ```

## Автоматический запуск на сервере

Для автоматического запуска бота на сервере используйте systemd service. Подробная инструкция находится в файле `README_DEPLOYMENT.md` в корне проекта.

**Быстрый старт:**
1. Скопируйте `tradetherapybot.service` в `/etc/systemd/system/`
2. Обновите пути в файле service
3. Выполните: `sudo systemctl enable tradetherapybot.service && sudo systemctl start tradetherapybot.service`

Бот будет автоматически запускаться при загрузке сервера и перезапускаться при падении.

## Мониторинг
- Логи пишутся в консоль и в файл `logs/bot.log`.
- При использовании systemd: `sudo journalctl -u tradetherapybot.service -f`
- **Важно:** Регулярно делайте бэкап базы данных командой `/backup` (только для администратора).

## Резервное копирование
- Используйте команду `/backup` в боте для получения файла `bot.db`.
- Рекомендуется делать бэкап раз в неделю или после важных изменений.
- Файл базы данных можно восстановить, просто скопировав его обратно в папку проекта.
