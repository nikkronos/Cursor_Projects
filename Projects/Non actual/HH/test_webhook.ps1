# Тест Webhook для HeadHunter Automation
# Запустите этот скрипт в PowerShell

$webhookUrl = "https://nikkronos.app.n8n.cloud/webhook/hh-apply"
$body = @{
    event_type = "hh_apply"
    timestamp = (Get-Date -Format "o")
    data = @{
        user_id = 123
        username = "test"
        command = "hh_apply"
        message = "Тестовый запрос"
    }
} | ConvertTo-Json -Depth 10

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Тест Webhook для HeadHunter Automation" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "URL: $webhookUrl" -ForegroundColor Yellow
Write-Host "Body: $body" -ForegroundColor Gray
Write-Host ""

try {
    Write-Host "Отправка запроса..." -ForegroundColor Yellow
    
    $response = Invoke-WebRequest -Uri $webhookUrl `
        -Method POST `
        -ContentType "application/json" `
        -Body $body `
        -UseBasicParsing
    
    Write-Host "✅ Запрос успешно отправлен!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Статус код: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "Ответ: $($response.Content)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Проверьте в N8N на вкладке 'Executions' - должно появиться новое выполнение!" -ForegroundColor Cyan
    
} catch {
    Write-Host "❌ Ошибка при отправке запроса:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    
    if ($_.Exception.Response) {
        $statusCode = $_.Exception.Response.StatusCode.value__
        Write-Host "Статус код: $statusCode" -ForegroundColor Red
        
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "Ответ сервера: $responseBody" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Нажмите любую клавишу для выхода..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
