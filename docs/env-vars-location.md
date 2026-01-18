# Где найти и создать env_vars.txt

## Расположение файла

Файл `env_vars.txt` находится в **корне проекта**:

```
C:\Users\krono\OneDrive\Рабочий стол\Cursor_test\env_vars.txt
```

## Если файла нет

Если файла `env_vars.txt` нет, создайте его:

1. **Скопируйте пример:**
   - Откройте `env_vars.example.txt` (он есть в корне проекта)
   - Скопируйте содержимое

2. **Создайте новый файл:**
   - Создайте файл `env_vars.txt` в корне проекта
   - Вставьте скопированное содержимое

3. **Заполните реальными значениями:**
   - Замените `your_bot_token_here` на реальный токен бота
   - Замените `your_telegram_id` на ваш Telegram ID
   - И так далее

## Важно!

⚠️ **Файл `env_vars.txt` НЕ коммитится в Git!**
- Он уже добавлен в `.gitignore`
- Секреты остаются только на вашем компьютере
- Не отправляйте этот файл никому

## Структура файла

```txt
# Telegram Bot Configuration
BOT_TOKEN=your_bot_token_here
ADMIN_ID=your_telegram_id
GROUP_CHAT_ID=your_group_chat_id

# N8N Configuration
N8N_WEBHOOK_URL=https://nikkronos.app.n8n.cloud/webhook/telegram-events

# Server Configuration
SERVER_IP=your_server_ip
```

## Как открыть файл

### Через Cursor:
1. В Explorer (левая панель) найдите файл `env_vars.txt`
2. Кликните на него, чтобы открыть

### Через Проводник Windows:
1. Откройте папку: `C:\Users\krono\OneDrive\Рабочий стол\Cursor_test`
2. Найдите файл `env_vars.txt`
3. Откройте в любом текстовом редакторе

### Через PowerShell:
```powershell
cd "C:\Users\krono\OneDrive\Рабочий стол\Cursor_test"
notepad env_vars.txt
```

---

**Последнее обновление:** 2025-12-23























