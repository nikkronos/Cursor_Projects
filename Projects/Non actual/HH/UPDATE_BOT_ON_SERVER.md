# Инструкция по обновлению TestN8N бота на сервере

## Шаг 1: Подключение к серверу

```powershell
ssh root@81.200.146.32
```

(Используйте пароль из env_vars.txt, если требуется)

## Шаг 2: Остановка бота

```bash
systemctl stop testn8n.service
```

## Шаг 3: Обновление файла handlers/user.py

### Вариант А: Через SCP (рекомендуется)

На вашем компьютере (PowerShell):

```powershell
cd "C:\Users\krono\OneDrive\Рабочий стол\Cursor_test"
scp TestN8N\handlers\user.py root@81.200.146.32:/opt/testn8n/handlers/user.py
```

### Вариант Б: Через SSH и редактирование

На сервере:

```bash
cd /opt/testn8n
nano handlers/user.py
```

Скопируйте содержимое обновленного файла `TestN8N/handlers/user.py` в редактор.

## Шаг 4: Обновление env_vars.txt на сервере

На сервере:

```bash
cd /opt/testn8n
nano env_vars.txt
```

Добавьте или обновите:

```env
N8N_WEBHOOK_URL=https://nikkronos.app.n8n.cloud/webhook/hh-apply
```

## Шаг 5: Перезапуск бота

```bash
systemctl start testn8n.service
systemctl status testn8n.service
```

## Шаг 6: Проверка логов

```bash
journalctl -u testn8n.service -n 50
```

## Проверка работы

Отправьте команду `/hh_apply` в Telegram бот. Бот должен ответить:
"✅ Запрос на запуск автоматизации HeadHunter отправлен в N8N!"

---

**Альтернативный способ (если есть Git на сервере):**

Если TestN8N находится в Git репозитории:

```bash
cd /opt/testn8n
git pull origin main
systemctl restart testn8n.service
```





















