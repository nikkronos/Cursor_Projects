# Инструкция по настройке автоматического CI/CD деплоя

## Что это даст?

После настройки каждый раз, когда вы делаете `git push` в ветку `main`, GitHub автоматически:
1. Запустит тесты
2. Если тесты прошли → обновит код на сервере
3. Перезапустит бота

Вам больше не нужно вручную загружать файлы через `scp` и перезапускать бота!

---

## Шаг 1: Создание SSH ключа для деплоя

### Вариант А: Автоматический (рекомендуется)

Используйте готовый скрипт для автоматизации:

1. Откройте PowerShell

2. Перейдите в папку проекта:
   ```powershell
   cd "C:\Users\krono\OneDrive\Рабочий стол\Cursor_test\TradeTherapyBot"
   ```

3. Запустите скрипт:
   ```powershell
   powershell -ExecutionPolicy Bypass -File ".\scripts\setup-ssh-key.ps1"
   ```
   
   **Или с полным путем:**
   ```powershell
   powershell -ExecutionPolicy Bypass -File "C:\Users\krono\OneDrive\Рабочий стол\Cursor_test\TradeTherapyBot\scripts\setup-ssh-key.ps1"
   ```
3. Скрипт автоматически:
   - Создаст SSH ключ
   - Покажет приватный и публичный ключи
   - Даст инструкции по дальнейшим шагам

### Вариант Б: Вручную

1. Откройте PowerShell
2. Выполните команду для создания SSH ключа:
   ```powershell
   ssh-keygen -t ed25519 -C "github-actions-deploy" -f $env:USERPROFILE\.ssh\github_deploy_key
   ```
   
   При запросе пароля **просто нажмите Enter** (без пароля - для автоматизации).

3. После создания ключа, скопируйте **ПРИВАТНЫЙ** ключ:
   ```powershell
   Get-Content $env:USERPROFILE\.ssh\github_deploy_key
   ```
   
   **ВНИМАНИЕ:** Это приватный ключ! Сохраните его, он понадобится для GitHub Secrets.

4. Скопируйте **ПУБЛИЧНЫЙ** ключ:
   ```powershell
   Get-Content $env:USERPROFILE\.ssh\github_deploy_key.pub
   ```

---

## Шаг 2: Добавление публичного ключа на сервер

1. Скопируйте **публичный ключ** (из предыдущего шага)

2. Подключитесь к серверу:
   ```powershell
   ssh root@81.200.146.32
   ```

3. На сервере выполните:
   ```bash
   mkdir -p ~/.ssh
   chmod 700 ~/.ssh
   echo "ВАШ_ПУБЛИЧНЫЙ_КЛЮЧ_ЗДЕСЬ" >> ~/.ssh/authorized_keys
   chmod 600 ~/.ssh/authorized_keys
   ```
   
   **Замените** `ВАШ_ПУБЛИЧНЫЙ_КЛЮЧ_ЗДЕСЬ` на публичный ключ из шага 1.

4. Проверьте подключение:
   ```powershell
   ssh -i $env:USERPROFILE\.ssh\github_deploy_key root@81.200.146.32
   ```
   
   Должно подключиться без запроса пароля.

---

## Шаг 3: Настройка GitHub Secrets

1. Откройте ваш репозиторий на GitHub
2. Перейдите в **Settings** → **Secrets and variables** → **Actions**
3. Нажмите **New repository secret**
4. Добавьте следующие секреты:

### SSH_PRIVATE_KEY
- **Name:** `SSH_PRIVATE_KEY`
- **Value:** Весь содержимый приватного ключа (из шага 1, пункт 3)
  - Начните с `-----BEGIN OPENSSH PRIVATE KEY-----`
  - Завершите `-----END OPENSSH PRIVATE KEY-----`
  - Включите все строки между ними

### SSH_HOST
- **Name:** `SSH_HOST`
- **Value:** `81.200.146.32`

### SSH_PORT
- **Name:** `SSH_PORT`
- **Value:** `22`

### SSH_USER
- **Name:** `SSH_USER`
- **Value:** `root`

### DEPLOY_PATH
- **Name:** `DEPLOY_PATH`
- **Value:** `/opt/tradetherapybot`

### SERVICE_NAME
- **Name:** `SERVICE_NAME`
- **Value:** `tradetherapybot`

**Важно о GROUP_CHAT_ID:**
- `GROUP_CHAT_ID` должен быть актуальным (бот должен быть администратором в этой группе)
- Для групп ID начинается с `-100` (например, `-1002346216181`)
- При смене группы обязательно обновить `GROUP_CHAT_ID` в GitHub Secrets
- Если бот был исключен из группы, обновить `GROUP_CHAT_ID` и перезапустить бота
- Ошибка 403 Forbidden: "bot was kicked from the supergroup chat" означает, что `GROUP_CHAT_ID` указывает на старую группу

---

## Шаг 4: Проверка SSH подключения

После добавления публичного ключа на сервер, проверьте подключение:

### Автоматическая проверка (рекомендуется)

Запустите скрипт проверки:
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\test-ssh-connection.ps1
```

Скрипт проверит:
- ✅ SSH подключение к серверу
- ✅ Наличие директории проекта
- ✅ Статус systemd service
- ✅ Наличие git репозитория

### Ручная проверка

Попробуйте подключиться вручную:
```powershell
ssh -i $env:USERPROFILE\.ssh\github_deploy_key root@81.200.146.32
```

Если подключение работает без запроса пароля - всё настроено правильно!

---

## Шаг 5: Проверка настройки (тестовый деплой)

После того, как вы:
1. ✅ Создали SSH ключ
2. ✅ Добавили публичный ключ на сервер
3. ✅ Добавили все секреты в GitHub

Сделайте тестовый коммит и push:
```powershell
git add .
git commit -m "test: проверка CI/CD"
git push origin main
```

Затем проверьте:
- Откройте репозиторий на GitHub
- Перейдите в **Actions**
- Убедитесь, что сначала запустились тесты (Run Tests)
- После успешных тестов запустится деплой (Deploy to Server)
- Убедитесь, что оба workflow выполнились успешно

---

## Что делать, если что-то пошло не так?

### Проблема: SSH подключение не работает
- Проверьте, что публичный ключ правильно добавлен на сервер
- Проверьте права доступа: `chmod 600 ~/.ssh/authorized_keys`
- Попробуйте подключиться вручную: `ssh -i ~/.ssh/github_deploy_key root@81.200.146.32`

### Проблема: GitHub Actions не может подключиться
- Проверьте, что все секреты добавлены правильно
- Убедитесь, что приватный ключ скопирован полностью (все строки)
- Проверьте логи в разделе Actions на GitHub

### Проблема: Деплой не работает
- Проверьте логи workflow на GitHub
- Убедитесь, что путь `/opt/tradetherapybot` правильный
- Проверьте, что service называется `tradetherapybot.service`

---

## Безопасность

⚠️ **ВАЖНО:**
- Приватный SSH ключ должен храниться ТОЛЬКО в GitHub Secrets
- Никогда не коммитьте приватный ключ в Git
- Если ключ скомпрометирован - создайте новый и удалите старый

---

## Ручной деплой (если CI/CD не работает)

Если автоматический деплой не работает, можно обновить бота вручную:

```powershell
# 1. Подключиться к серверу
ssh root@81.200.146.32

# 2. Перейти в директорию проекта
cd /opt/tradetherapybot

# 3. Обновить код
git pull origin main

# 4. Установить зависимости (если requirements.txt изменился)
pip3 install -r requirements.txt

# 5. Перезапустить бота
systemctl restart tradetherapybot.service

# 6. Проверить статус
systemctl status tradetherapybot.service
```

