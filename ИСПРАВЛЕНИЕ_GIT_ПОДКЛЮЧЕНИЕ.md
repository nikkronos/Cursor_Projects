# Исправление: Подключение Git к приватному репозиторию

## Проблема

Git просит логин и пароль при `git pull`, потому что репозиторий приватный.

## Решение 1: Использовать SSH URL (рекомендуется)

### Шаг 1: Отменить текущую операцию

На сервере нажмите **Ctrl + C**, чтобы отменить запрос пароля.

### Шаг 2: Изменить remote на SSH

На сервере выполните:

```bash
git remote set-url origin git@github.com:nikkronos/TradeTherapyBot.git
```

### Шаг 3: Загрузить код

```bash
git pull origin main
```

Если будет ошибка "Permission denied", нужно добавить SSH ключ сервера в GitHub. Но для автоматического деплоя это не обязательно - можно использовать другое решение.

---

## Решение 2: Использовать GitHub Personal Access Token (проще)

### Шаг 1: Отменить текущую операцию

На сервере нажмите **Ctrl + C**.

### Шаг 2: Создать Personal Access Token на GitHub

1. Откройте GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Нажмите "Generate new token (classic)"
3. Назовите токен: `server-deploy`
4. Выберите срок действия (например, 90 дней)
5. Отметьте права: **repo** (доступ к репозиторию)
6. Нажмите "Generate token"
7. **СКОПИРУЙТЕ ТОКЕН** (он показывается только один раз!)

### Шаг 3: Использовать токен при pull

На сервере выполните:

```bash
git pull https://ВАШ_ТОКЕН@github.com/nikkronos/TradeTherapyBot.git main
```

Или изменить remote:

```bash
git remote set-url origin https://ВАШ_ТОКЕН@github.com/nikkronos/TradeTherapyBot.git
```

---

## Решение 3: Просто скопировать файлы (если не критично)

Если у вас уже есть все файлы на сервере, можно просто инициализировать git без pull:

```bash
cd /opt/tradetherapybot
git init
git remote add origin https://github.com/nikkronos/TradeTherapyBot.git
git add .
git commit -m "Initial commit from server"
git branch -M main
```

Но это не идеально для деплоя.

---

## Рекомендация

**Лучше всего использовать Solution 2 (Personal Access Token)** - это проще и безопаснее для приватного репозитория.

