# VeloC Windows Installation Script
$installPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
Write-Host "Installing VeloC 1.0.0 GA from: $installPath" -ForegroundColor Cyan

# Add to user PATH
$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($currentPath -notlike "*$installPath*") {
    [Environment]::SetEnvironmentVariable("Path", "$currentPath;$installPath", "User")
    Write-Host "[SUCCESS] Added VeloC to User PATH!" -ForegroundColor Green
} else {
    Write-Host "[INFO] VeloC is already in User PATH." -ForegroundColor Yellow
}

Write-Host "VeloC 1.0.0 GA is ready to use! Restart terminal and run: veloc dev-setup" -ForegroundColor Green
