# База Данных

## Технология
Используется **SQLite** (файл `bot.db` в корне проекта). База данных создается автоматически при первом запуске бота.

## Схема

### Таблица `users`
Основная таблица для хранения информации о пользователях и их подписках.

| Поле | Тип | Описание |
|------|-----|----------|
| `telegram_id` | INTEGER (PK) | Уникальный ID пользователя в Telegram |
| `first_name` | TEXT | Имя пользователя |
| `username` | TEXT | Никнейм (@username) |
| `subscription_status` | TEXT | Статус: `active` (активен), `inactive` (неактивен) |
| `subscription_start_date` | TEXT | Дата начала текущей подписки (формат: ISO datetime string) |
| `subscription_end_date` | TEXT | Дата окончания подписки (формат: ISO datetime string) |
| `payment_status` | TEXT | Статус оплаты: `pending`, `pending_review`, `paid`, `rejected` |
| `last_notification_level` | TEXT | Уровень последнего напоминания: `3days`, `1day`, `1hour`, `expired`, `kicked` |

### Таблица `receipts`
Таблица для хранения ссылок на файлы чеков (для отчетности).

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | INTEGER PRIMARY KEY AUTOINCREMENT | Внутренний ID записи |
| `user_id` | INTEGER | ID пользователя, приславшего чек |
| `file_id` | TEXT | ID файла в Telegram (file_id) |
| `file_type` | TEXT | Тип файла: `photo` или `document` |
| `created_at` | TEXT | Дата и время загрузки чека (Default: CURRENT_TIMESTAMP) |

### Таблица `tariff_answers`
Таблица для хранения ответов пользователей на вопросы опроса (ветка "Не буду платить").

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | INTEGER PRIMARY KEY AUTOINCREMENT | Внутренний ID записи |
| `user_id` | INTEGER | ID пользователя (FOREIGN KEY к users.telegram_id) |
| `question_number` | INTEGER | Номер вопроса в опросе |
| `answer` | TEXT | Ответ пользователя |
| `created_at` | TEXT | Дата и время ответа (Default: CURRENT_TIMESTAMP) |
| `status` | TEXT | Статус ответа: `pending`, `approved`, `rejected` |

## Индексы

Для оптимизации запросов в базе данных создаются следующие индексы:

- `idx_subscription_status` - на поле `subscription_status` таблицы `users`
- `idx_subscription_end_date` - на поле `subscription_end_date` таблицы `users`
- `idx_subscription_status_end_date` - комбинированный индекс на `(subscription_status, subscription_end_date)` таблицы `users`
- `idx_receipts_user_id` - на поле `user_id` таблицы `receipts`

Индексы создаются автоматически при инициализации новой базы данных. Для существующих баз данных выполняется автоматическая миграция при старте бота (функция `migrate_add_indexes()`).

## Резервное копирование
Рекомендуется регулярно делать бэкап файла `bot.db` с помощью команды `/backup` (доступна только администратору).
