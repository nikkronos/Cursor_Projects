# Проверка логов бота на сервере

## Важно: journalctl - это Linux команда!

`journalctl` работает только на Linux сервере, не в Windows PowerShell.

## Как проверить логи

### Вариант 1: Подключиться к серверу через SSH

В PowerShell:

```powershell
ssh root@81.200.146.32
```

Затем на сервере:

```bash
journalctl -u testn8n.service -n 50 --no-pager
```

Или искать конкретно по hh_apply:

```bash
journalctl -u testn8n.service -n 100 --no-pager | grep -i "hh_apply\|n8n"
```

### Вариант 2: Проверить логи в реальном времени

На сервере:

```bash
journalctl -u testn8n.service -f
```

Это покажет логи в реальном времени. Отправьте `/hh_apply` в бот и смотрите, что появляется в логах.

### Вариант 3: Проверить файл логов напрямую

На сервере:

```bash
tail -n 50 /opt/testn8n/logs/bot.log
```

Или если логи в другом месте:

```bash
find /opt/testn8n -name "*.log" -type f
```

## Что искать в логах

**Успешная отправка:**
```
Событие 'hh_apply' успешно отправлено в N8N
```

**Ошибка:**
```
Ошибка при отправке события в N8N
```

## Быстрая проверка через одну команду

```powershell
ssh root@81.200.146.32 "journalctl -u testn8n.service -n 50 --no-pager | grep -i 'hh_apply\|n8n'"
```

Эта команда выполнит проверку логов на сервере и вернёт результат в PowerShell.





















