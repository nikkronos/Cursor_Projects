# Исправление: Настройка Git на сервере

## Проблема

На сервере в папке `/opt/tradetherapybot` нет git репозитория. Нужно инициализировать git.

## Решение: Инициализировать Git на сервере

### Шаг 1: Подключиться к серверу

Откройте PowerShell и выполните:

```powershell
ssh root@81.200.146.32
```

### Шаг 2: Перейти в папку проекта

На сервере выполните:

```bash
cd /opt/tradetherapybot
```

### Шаг 3: Инициализировать Git

Выполните команды по очереди:

```bash
git init
```

### Шаг 4: Добавить remote (ссылка на GitHub репозиторий)

**Вам нужно знать URL вашего репозитория на GitHub.**

1. Откройте ваш репозиторий на GitHub
2. Нажмите зеленую кнопку **Code**
3. Скопируйте URL (например: `https://github.com/ваш_ник/TradeTherapyBot.git`)

Затем на сервере выполните (замените URL на ваш):

```bash
git remote add origin https://github.com/ВАШ_НИК/TradeTherapyBot.git
```

**Если репозиторий приватный**, используйте SSH URL (замените на ваш):
```bash
git remote add origin git@github.com:ВАШ_НИК/TradeTherapyBot.git
```

### Шаг 5: Загрузить код с GitHub

Выполните:

```bash
git pull origin main
```

Если будет ошибка, попробуйте:

```bash
git fetch origin
git checkout -b main origin/main
```

### Шаг 6: Выйти с сервера

```bash
exit
```

## Готово!

После этого деплой должен работать. Попробуйте еще раз сделать `git push origin main` с вашего компьютера.

---

## Альтернативный способ: Склонировать репозиторий заново

Если у вас на сервере нет важных данных (кроме базы данных), можно склонировать репозиторий заново:

1. Подключитесь к серверу
2. Сделайте бэкап базы данных:
   ```bash
   cp /opt/tradetherapybot/bot.db /opt/tradetherapybot/bot.db.backup
   ```
3. Удалите старую папку (осторожно!):
   ```bash
   cd /opt
   rm -rf tradetherapybot
   ```
4. Склонируйте репозиторий:
   ```bash
   git clone https://github.com/ВАШ_НИК/TradeTherapyBot.git tradetherapybot
   ```
5. Восстановите базу данных:
   ```bash
   cp /opt/tradetherapybot/bot.db.backup /opt/tradetherapybot/bot.db
   ```
6. Настройте env_vars.txt заново

**Внимание:** Этот способ удалит все файлы, кроме базы данных (если вы сделали бэкап).

