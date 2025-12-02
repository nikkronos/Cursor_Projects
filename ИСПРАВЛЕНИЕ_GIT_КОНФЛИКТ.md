# Исправление: Конфликт файлов при git pull

## Проблема

Git не может загрузить код, потому что на сервере уже есть файлы, которые будут перезаписаны.

## Решение: Сохранить важные файлы и обновить код

### Шаг 1: Сохранить базу данных и важные файлы

На сервере выполните (важно сделать бэкап!):

```bash
cd /opt/tradetherapybot
```

```bash
cp bot.db bot.db.backup
```

```bash
cp env_vars.txt env_vars.txt.backup 2>/dev/null || echo "env_vars.txt not found"
```

### Шаг 2: Добавить все файлы в git

```bash
git add .
```

### Шаг 3: Сделать commit

```bash
git commit -m "Initial commit from server"
```

### Шаг 4: Объединить с GitHub (принудительно)

```bash
git pull origin main --allow-unrelated-histories
```

Если будет конфликт, используйте:

```bash
git reset --hard origin/main
```

**Внимание:** Это перезапишет все файлы на сервере файлами с GitHub!

### Шаг 5: Восстановить важные файлы

```bash
cp bot.db.backup bot.db
```

```bash
cp env_vars.txt.backup env_vars.txt 2>/dev/null || echo "env_vars.txt not restored"
```

---

## Альтернативное решение (проще, но удалит локальные изменения)

Если не важно сохранить локальные изменения на сервере:

### Шаг 1: Сохранить только базу данных

```bash
cd /opt/tradetherapybot
cp bot.db /tmp/bot.db.backup
```

### Шаг 2: Удалить все, кроме .git

```bash
find . -maxdepth 1 ! -name '.git' ! -name '.' -exec rm -rf {} +
```

### Шаг 3: Загрузить код с GitHub

```bash
git pull origin main
```

### Шаг 4: Восстановить базу данных

```bash
cp /tmp/bot.db.backup bot.db
```

---

## Готово!

После этого git репозиторий будет настроен, и деплой сможет работать.

