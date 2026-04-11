# Быстрое обновление TestN8N бота на сервере
# Запустите этот скрипт в PowerShell

$SERVER_IP = "81.200.146.32"
$SERVER_USER = "root"
$LOCAL_BOT_FILE = "TestN8N\handlers\user.py"
$REMOTE_BOT_PATH = "/opt/testn8n/handlers/user.py"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Обновление TestN8N бота на сервере" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Проверка существования файла
if (-not (Test-Path $LOCAL_BOT_FILE)) {
    Write-Host "❌ Файл не найден: $LOCAL_BOT_FILE" -ForegroundColor Red
    Write-Host "Убедитесь, что вы находитесь в корне проекта" -ForegroundColor Yellow
    exit 1
}

Write-Host "📤 Копирование файла на сервер..." -ForegroundColor Yellow
Write-Host "   Локальный: $LOCAL_BOT_FILE" -ForegroundColor Gray
Write-Host "   Удаленный: $REMOTE_BOT_PATH" -ForegroundColor Gray
Write-Host ""

# Копирование файла
scp $LOCAL_BOT_FILE "${SERVER_USER}@${SERVER_IP}:${REMOTE_BOT_PATH}"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Файл успешно скопирован!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🔄 Перезапуск бота на сервере..." -ForegroundColor Yellow
    
    # Перезапуск бота
    ssh "${SERVER_USER}@${SERVER_IP}" "systemctl restart testn8n.service && systemctl status testn8n.service --no-pager"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ Бот успешно обновлен и перезапущен!" -ForegroundColor Green
        Write-Host ""
        Write-Host "📋 Проверка логов (последние 20 строк):" -ForegroundColor Cyan
        ssh "${SERVER_USER}@${SERVER_IP}" "journalctl -u testn8n.service -n 20 --no-pager"
    } else {
        Write-Host "❌ Ошибка при перезапуске бота" -ForegroundColor Red
    }
} else {
    Write-Host "❌ Ошибка при копировании файла" -ForegroundColor Red
    Write-Host "Проверьте SSH подключение к серверу" -ForegroundColor Yellow
}





















