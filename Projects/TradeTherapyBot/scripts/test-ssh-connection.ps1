# Script for testing SSH connection to server
# Run: powershell -ExecutionPolicy Bypass -File .\scripts\test-ssh-connection.ps1

Write-Host "=== Testing SSH Connection to Server ===" -ForegroundColor Green
Write-Host ""

$sshKeyPath = "$env:USERPROFILE\.ssh\github_deploy_key"

if (-not (Test-Path $sshKeyPath)) {
    Write-Host "Error: SSH key not found!" -ForegroundColor Red
    Write-Host "First run setup-ssh-key.ps1 script" -ForegroundColor Yellow
    exit 1
}

Write-Host "Checking connection to server..." -ForegroundColor Cyan
Write-Host ""

# Test connection
Write-Host "Connecting to root@81.200.146.32..." -ForegroundColor Yellow
$testResult = ssh -i $sshKeyPath -o StrictHostKeyChecking=no -o ConnectTimeout=5 root@81.200.146.32 "echo 'Connection successful!'" 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "SSH connection works!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Testing commands on server..." -ForegroundColor Cyan
    
    # Check project directory
    $deployPath = "/opt/tradetherapybot"
    Write-Host "Checking path: $deployPath" -ForegroundColor Yellow
    $pathCheck = ssh -i $sshKeyPath root@81.200.146.32 "test -d $deployPath && echo 'exists' || echo 'not found'" 2>&1
    
    if ($pathCheck -eq "exists") {
        Write-Host "Project directory found" -ForegroundColor Green
    } else {
        Write-Host "Warning: Project directory not found: $deployPath" -ForegroundColor Yellow
        Write-Host "Make sure the path is correct in GitHub Secret: DEPLOY_PATH" -ForegroundColor Yellow
    }
    
    # Check systemd service
    Write-Host "Checking systemd service: tradetherapybot.service" -ForegroundColor Yellow
    $serviceCheck = ssh -i $sshKeyPath root@81.200.146.32 "systemctl status tradetherapybot.service --no-pager -l 2>&1 | head -3" 2>&1
    
    if ($serviceCheck -match "Active: active") {
        Write-Host "Service is running" -ForegroundColor Green
    } elseif ($serviceCheck -match "Active: inactive") {
        Write-Host "Warning: Service is inactive" -ForegroundColor Yellow
    } else {
        Write-Host "Warning: Service not found or unavailable" -ForegroundColor Yellow
        Write-Host "Make sure service name is correct in GitHub Secret: SERVICE_NAME" -ForegroundColor Yellow
    }
    
    # Check git repository
    Write-Host "Checking git repository..." -ForegroundColor Yellow
    $gitCheck = ssh -i $sshKeyPath root@81.200.146.32 "cd $deployPath && git status 2>&1 | head -1" 2>&1
    
    if ($gitCheck -match "On branch" -or $gitCheck -match "fatal: not a git repository") {
        if ($gitCheck -match "fatal: not a git repository") {
            Write-Host "Warning: Git repository not found in $deployPath" -ForegroundColor Yellow
            Write-Host "Need to initialize git or clone repository" -ForegroundColor Yellow
        } else {
            Write-Host "Git repository found" -ForegroundColor Green
        }
    }
    
    Write-Host ""
    Write-Host "=== All checks completed ===" -ForegroundColor Green
    
} else {
    Write-Host "SSH connection error!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Possible reasons:" -ForegroundColor Yellow
    Write-Host "1. Public key not added to server" -ForegroundColor White
    Write-Host "2. Wrong IP address or port" -ForegroundColor White
    Write-Host "3. Server unavailable" -ForegroundColor White
    Write-Host ""
    Write-Host "Error details:" -ForegroundColor Yellow
    Write-Host $testResult -ForegroundColor Red
    exit 1
}
