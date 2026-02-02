# Копия иксуюемся

Telegram-бот для копирования информации из одного Telegram-канала в другой.

## Описание

Проект создан по аналогии с PastuhiBot. Бот состоит из двух компонентов:

1. **Юзербот (Pyrogram)** - участник Telegram-каналов, читает сообщения из оригинального канала
2. **Бот (aiogram)** - копирует сообщения в целевой канал

**Важно:** Подписочная система не используется. Доступ к каналу выдается вручную администратором.

## Архитектура

- **Юзербот (Pyrogram)** - для чтения сообщений из оригинального канала
- **Бот (aiogram/pyTelegramBotAPI)** - для управления подписками
- **SQLite** - база данных для хранения информации о подписках и пользователях
- **APScheduler** - планировщик задач (если потребуется)

## Структура проекта

```
xxx/
├── ROADMAP_КОПИЯ_ИКСУЮЕМСЯ.md    # Планы развития
├── DONE_LIST_КОПИЯ_ИКСУЮЕМСЯ.md  # История выполненных задач
├── SESSION_SUMMARY_YYYY-MM-DD.md  # Резюме сессий
├── README.md                      # Этот файл
├── README_FOR_NEXT_AGENT.md      # Инструкция для следующего агента
├── requirements.txt               # Зависимости проекта
├── env_vars.example.txt           # Пример переменных окружения
├── config.py                      # Конфигурация
├── loader.py                      # Инициализация бота и логгера
├── database.py                    # Работа с базой данных
├── main.py                        # Точка входа
├── userbot.py                     # Юзербот (Pyrogram) - чтение сообщений
├── copy_handler.py                # Модуль копирования сообщений
├── handlers/                      # Обработчики (user: /start)
├── TESTING_GUIDE.md               # Руководство по тестированию (Этап 6)
├── utils.py                       # Утилиты
└── docs/                          # Документация проекта
```

## Установка и запуск

1. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

2. Создайте файл `env_vars.txt` на основе `env_vars.example.txt` и заполните его:
   ```
   BOT_TOKEN=your_bot_token_here
   ADMIN_ID=your_telegram_id
   API_ID=your_api_id
   API_HASH=your_api_hash
   SOURCE_CHANNEL_ID=your_source_channel_id
   TARGET_CHANNEL_ID=your_target_channel_id
   ```

3. Запустите бота:
   ```bash
   python main.py
   ```

## Деплой на сервер

### systemd (рекомендуется)

1. Скопируйте репозиторий на сервер (например, в `/opt/cursor_test`).
2. Скопируйте `xxx/kopiya-iksuyemsya.service` в `/etc/systemd/system/`:
   ```bash
   sudo cp xxx/kopiya-iksuyemsya.service /etc/systemd/system/
   ```
3. Отредактируйте пути в юните под ваш сервер:
   ```bash
   sudo nano /etc/systemd/system/kopiya-iksuyemsya.service
   ```
   Укажите `WorkingDirectory` и `ExecStart` (например `/opt/cursor_test/xxx`).
4. Создайте `env_vars.txt` в папке `xxx/` на сервере (секреты не коммитятся).
5. Включите и запустите сервис:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable kopiya-iksuyemsya.service
   sudo systemctl start kopiya-iksuyemsya.service
   ```
6. Логи: `sudo journalctl -u kopiya-iksuyemsya.service -f`

### CI/CD (GitHub Actions)

При пуше в `main` workflow деплоя обновляет код в `DEPLOY_PATH`, ставит зависимости из `xxx/requirements.txt` и перезапускает `kopiya-iksuyemsya.service`, если на сервере есть папка `xxx`. Убедитесь, что `DEPLOY_PATH` указывает на корень репозитория (где есть папка `xxx`).

## Технологии

- Python 3.7+
- Pyrogram 2.0.106 (для юзербота)
- aiogram 2.25.1 или pyTelegramBotAPI (для бота управления)
- SQLite
- APScheduler (если потребуется)

## Статус проекта

**Текущий статус:** Юзербот и модуль копирования готовы. Добавлен TESTING_GUIDE.md и обработчик /start. Готов к ручному тестированию по TESTING_GUIDE.md (Этап 6).

## Документация

- `ROADMAP_КОПИЯ_ИКСУЮЕМСЯ.md` - планы развития проекта
- `DONE_LIST_КОПИЯ_ИКСУЮЕМСЯ.md` - история выполненных задач
- `SESSION_SUMMARY_YYYY-MM-DD.md` - резюме последней сессии
- `TESTING_GUIDE.md` - руководство по тестированию на тестовом канале (Этап 6)
- `README_FOR_NEXT_AGENT.md` - инструкция для следующего агента
