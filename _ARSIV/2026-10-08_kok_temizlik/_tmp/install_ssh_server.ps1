# Windows VDS - OpenSSH Server Kurulum Scripti
# PowerShell Yönetici (Admin) olarak çalıştırın

Write-Host "=== OpenSSH Server Kurulumu Başlıyor ===" -ForegroundColor Green

# 1. OpenSSH Server yükle
Write-Host "1/4 OpenSSH Server yükleniyor..." -ForegroundColor Yellow
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0

# 2. Servisi başlat ve otomatik yap
Write-Host "2/4 SSH servisi başlatılıyor ve otomatik yapılıyor..." -ForegroundColor Yellow
Start-Service sshd
Set-Service -Name sshd -StartupType 'Automatic'

# 3. Firewall port 22 aç
Write-Host "3/4 Firewall kuralı ekleniyor (port 22)..." -ForegroundColor Yellow
New-NetFirewallRule -Name 'sshd' -DisplayName 'OpenSSH Server' -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22

# 4. Doğrulama
Write-Host "4/4 Kurulum doğrulanıyor..." -ForegroundColor Yellow
$status = Get-Service sshd
Write-Host "SSH Servis Durumu: $($status.Status)" -ForegroundColor Cyan
$firewall = Get-NetFirewallRule -DisplayName 'OpenSSH Server'
Write-Host "Firewall Kuralı: $($firewall.Enabled)" -ForegroundColor Cyan

Write-Host "`n=== KURULUM TAMAMLANDI ===" -ForegroundColor Green
Write-Host "Test için lokalden: ssh Administrator@193.111.78.200" -ForegroundColor Cyan
Write-Host "Şifre: rJxUygMYVsf2Zi4w" -ForegroundColor Cyan

pause