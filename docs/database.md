# База Данных

## Схема

### Таблица `users`
Основная таблица для хранения информации о пользователях и их подписках.

| Поле | Тип | Описание |
|------|-----|----------|
| `telegram_id` | BIGINT (PK) | Уникальный ID пользователя в Telegram |
| `first_name` | VARCHAR(255) | Имя пользователя |
| `username` | VARCHAR(255) | Никнейм (@username) |
| `subscription_status` | VARCHAR(50) | Статус: `active` (активен), `inactive` (неактивен) |
| `subscription_start_date` | TIMESTAMP | Дата начала текущей подписки |
| `subscription_end_date` | TIMESTAMP | Дата окончания подписки |
| `payment_status` | VARCHAR(50) | Статус оплаты: `pending`, `pending_review`, `paid`, `rejected` |
| `last_notification_level` | VARCHAR(20) | Уровень последнего напоминания: `3days`, `1day`, `1hour`, `expired`, `kicked` |

### Таблица `receipts`
Таблица для хранения ссылок на файлы чеков (для отчетности).

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | SERIAL (PK) | Внутренний ID записи |
| `user_id` | BIGINT | ID пользователя, приславшего чек |
| `file_id` | TEXT | ID файла в Telegram (file_id) |
| `file_type` | VARCHAR(20) | Тип файла: `photo` или `document` |
| `created_at` | TIMESTAMP | Дата и время загрузки чека (Default: NOW) |
