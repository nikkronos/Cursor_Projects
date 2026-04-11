# Быстрый старт: Настройка автоматического CI/CD деплоя

> ⚠️ **Если вы не разработчик**, используйте файл **`ШАГ_ЗА_ШАГОМ_CICD.md`** - там все расписано подробно!

## 🚀 За 5 минут до автоматического деплоя!

### Шаг 1: Создать SSH ключ (1 минута)

1. Откройте PowerShell (Win+R → powershell → Enter)

2. Выполните эти команды по очереди (каждую отдельно, нажимая Enter):

```powershell
cd "C:\Users\krono\OneDrive\Рабочий стол\Cursor_test\TradeTherapyBot"
```

```powershell
powershell -ExecutionPolicy Bypass -File ".\scripts\setup-ssh-key.ps1"
```

**Или одной командой с полным путем:**

```powershell
powershell -ExecutionPolicy Bypass -File "C:\Users\krono\OneDrive\Рабочий стол\Cursor_test\TradeTherapyBot\scripts\setup-ssh-key.ps1"
```

Скрипт создаст ключ и покажет:
- ✅ Приватный ключ (для GitHub Secrets)
- ✅ Публичный ключ (для сервера)

---

### Шаг 2: Добавить публичный ключ на сервер (1 минута)

1. Скопируйте публичный ключ (из шага 1)

2. Подключитесь к серверу:
   ```powershell
   ssh root@81.200.146.32
   ```

3. На сервере выполните:
   ```bash
   mkdir -p ~/.ssh
   echo 'ВСТАВЬТЕ_ПУБЛИЧНЫЙ_КЛЮЧ_СЮДА' >> ~/.ssh/authorized_keys
   chmod 600 ~/.ssh/authorized_keys
   ```

4. Проверьте подключение (новый терминал):
   ```powershell
   powershell -ExecutionPolicy Bypass -File .\scripts\test-ssh-connection.ps1
   ```

---

### Шаг 3: Настроить GitHub Secrets (2 минуты)

1. Откройте ваш репозиторий на GitHub
2. Перейдите: **Settings** → **Secrets and variables** → **Actions**
3. Нажмите **New repository secret** и добавьте:

#### SSH_PRIVATE_KEY
- **Name:** `SSH_PRIVATE_KEY`
- **Value:** Приватный ключ из шага 1 (весь текст от `-----BEGIN` до `-----END`)

#### SSH_HOST
- **Name:** `SSH_HOST`
- **Value:** `81.200.146.32`

#### SSH_PORT
- **Name:** `SSH_PORT`
- **Value:** `22`

#### SSH_USER
- **Name:** `SSH_USER`
- **Value:** `root`

#### DEPLOY_PATH
- **Name:** `DEPLOY_PATH`
- **Value:** `/opt/tradetherapybot`

#### SERVICE_NAME
- **Name:** `SERVICE_NAME`
- **Value:** `tradetherapybot`

---

### Шаг 4: Тестирование (1 минута)

Сделайте тестовый коммит:

```powershell
git add .
git commit -m "ci: настройка автоматического деплоя"
git push origin main
```

Проверьте результат:
1. Откройте репозиторий на GitHub
2. Перейдите в **Actions**
3. Убедитесь, что:
   - ✅ Тесты прошли (Run Tests)
   - ✅ Деплой успешен (Deploy to Server)

---

## ✅ Готово!

Теперь каждый раз, когда вы делаете `git push origin main`:
1. Автоматически запускаются тесты
2. Если тесты прошли → автоматически обновляется код на сервере
3. Бот перезапускается с новой версией

**Больше не нужно вручную загружать файлы через `scp`!**

---

## 📚 Подробные инструкции

Если что-то пошло не так, смотрите:
- `docs/CICD_SETUP.md` - подробная инструкция
- `docs/specs/09-automatic-cicd-deployment.md` - техническое задание

---

## 🔧 Полезные команды

### Проверка SSH подключения
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\test-ssh-connection.ps1
```

### Ручной деплой (если CI/CD не работает)
```powershell
ssh root@81.200.146.32
cd /opt/tradetherapybot
git pull origin main
systemctl restart tradetherapybot.service
```

### Просмотр логов деплоя на GitHub
1. Откройте репозиторий → **Actions**
2. Выберите последний workflow
3. Просмотрите логи каждого шага

