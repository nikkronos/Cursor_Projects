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

## Резервное копирование
Рекомендуется регулярно делать бэкап файла `bot.db` с помощью команды `/backup` (доступна только администратору).
