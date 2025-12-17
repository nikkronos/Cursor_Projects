# Script for automatic SSH key creation for GitHub Actions deployment
# Run: powershell -ExecutionPolicy Bypass -File .\scripts\setup-ssh-key.ps1

Write-Host "=== SSH Key Setup for GitHub Actions Deployment ===" -ForegroundColor Green
Write-Host ""

$sshKeyPath = "$env:USERPROFILE\.ssh\github_deploy_key"
$sshKeyPathPub = "$sshKeyPath.pub"

# Check if key already exists
if (Test-Path $sshKeyPath) {
    Write-Host "Warning: SSH key already exists!" -ForegroundColor Yellow
    $overwrite = Read-Host "Overwrite? (y/n)"
    if ($overwrite -ne "y") {
        Write-Host "Cancelled." -ForegroundColor Red
        exit
    }
}

# Create .ssh directory if it doesn't exist
$sshDir = "$env:USERPROFILE\.ssh"
if (-not (Test-Path $sshDir)) {
    New-Item -ItemType Directory -Path $sshDir | Out-Null
    Write-Host "Created .ssh directory" -ForegroundColor Green
}

# Create SSH key
Write-Host "Creating SSH key..." -ForegroundColor Cyan
ssh-keygen -t ed25519 -C "github-actions-deploy" -f $sshKeyPath -N '""' -q

if (Test-Path $sshKeyPath) {
    Write-Host "SSH key created successfully!" -ForegroundColor Green
    Write-Host ""
    
    # Show private key
    Write-Host ("=" * 60) -ForegroundColor Yellow
    Write-Host "PRIVATE KEY (SSH_PRIVATE_KEY for GitHub Secrets):" -ForegroundColor Red
    Write-Host ("=" * 60) -ForegroundColor Yellow
    Write-Host ""
    $privateKey = Get-Content $sshKeyPath -Raw
    Write-Host $privateKey -ForegroundColor White
    Write-Host ""
    Write-Host ("=" * 60) -ForegroundColor Yellow
    Write-Host "IMPORTANT: Copy all text above (from -----BEGIN to -----END)" -ForegroundColor Red
    Write-Host "This key is needed for GitHub Secret: SSH_PRIVATE_KEY" -ForegroundColor Yellow
    Write-Host ""
    
    # Show public key
    Write-Host ("=" * 60) -ForegroundColor Green
    Write-Host "PUBLIC KEY (for adding to server):" -ForegroundColor Green
    Write-Host ("=" * 60) -ForegroundColor Green
    Write-Host ""
    $publicKey = Get-Content $sshKeyPathPub
    Write-Host $publicKey -ForegroundColor White
    Write-Host ""
    Write-Host ("=" * 60) -ForegroundColor Green
    Write-Host "Copy the public key above" -ForegroundColor Green
    Write-Host ""
    
    # Instructions
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1. Add public key to server:" -ForegroundColor Yellow
    Write-Host "   ssh root@81.200.146.32" -ForegroundColor White
    Write-Host "   mkdir -p ~/.ssh" -ForegroundColor White
    Write-Host "   echo 'PASTE_PUBLIC_KEY_HERE' >> ~/.ssh/authorized_keys" -ForegroundColor White
    Write-Host "   chmod 600 ~/.ssh/authorized_keys" -ForegroundColor White
    Write-Host ""
    Write-Host "2. Add private key to GitHub Secrets:" -ForegroundColor Yellow
    Write-Host "   - Open your repository on GitHub" -ForegroundColor White
    Write-Host "   - Settings -> Secrets and variables -> Actions" -ForegroundColor White
    Write-Host "   - New repository secret" -ForegroundColor White
    Write-Host "   - Name: SSH_PRIVATE_KEY" -ForegroundColor White
    Write-Host "   - Value: (paste private key from above)" -ForegroundColor White
    Write-Host ""
    Write-Host "3. Add other secrets:" -ForegroundColor Yellow
    Write-Host "   SSH_HOST = 81.200.146.32" -ForegroundColor White
    Write-Host "   SSH_PORT = 22" -ForegroundColor White
    Write-Host "   SSH_USER = root" -ForegroundColor White
    Write-Host "   DEPLOY_PATH = /opt/tradetherapybot" -ForegroundColor White
    Write-Host "   SERVICE_NAME = tradetherapybot" -ForegroundColor White
    Write-Host ""
    
    # Copy to clipboard (optional)
    Write-Host "Copy public key to clipboard? (y/n)" -ForegroundColor Cyan
    $copy = Read-Host
    if ($copy -eq "y") {
        $publicKey | Set-Clipboard
        Write-Host "Public key copied to clipboard!" -ForegroundColor Green
    }
    
} else {
    Write-Host "Error creating SSH key!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=== Done! ===" -ForegroundColor Green
