# Проверка логов бота на сервере
# Запустите этот скрипт в PowerShell

$SERVER_IP = "81.200.146.32"
$SERVER_USER = "root"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Проверка логов TestN8N бота" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Подключение к серверу: ${SERVER_USER}@${SERVER_IP}" -ForegroundColor Yellow
Write-Host ""

Write-Host "Последние 50 строк логов (ищем упоминания hh_apply, n8n, webhook):" -ForegroundColor Cyan
Write-Host ""

ssh "${SERVER_USER}@${SERVER_IP}" "journalctl -u testn8n.service -n 50 --no-pager | grep -i 'hh_apply\|n8n\|webhook' || journalctl -u testn8n.service -n 50 --no-pager"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Если видите 'Событие успешно отправлено' - запрос доходит до N8N" -ForegroundColor Green
Write-Host "Если видите 'Ошибка при отправке' - проблема с отправкой" -ForegroundColor Red
Write-Host "========================================" -ForegroundColor Cyan

