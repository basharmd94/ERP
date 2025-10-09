# Performance Optimization Script for ERP Django Application
# This script applies performance optimizations and restarts services

param(
    [switch]$SkipBuild = $false,
    [switch]$CollectStatic = $true
)

Write-Host "Starting performance optimization..." -ForegroundColor Green

# Stop current services
Write-Host "Stopping Docker services..." -ForegroundColor Yellow
.\scripts\docker_setup.ps1 -Stop

if (!$SkipBuild) {
    # Rebuild with optimizations
    Write-Host "Rebuilding Docker images with optimizations..." -ForegroundColor Yellow
    .\scripts\docker_setup.ps1 -Build
}

# Start services
Write-Host "Starting optimized services..." -ForegroundColor Yellow
.\scripts\docker_setup.ps1 -Start

# Wait for services to be ready
Write-Host "Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

if ($CollectStatic) {
    # Collect static files for better performance
    Write-Host "Collecting static files..." -ForegroundColor Yellow
    docker exec erp_web python manage.py collectstatic --noinput
}

# Run database optimizations
Write-Host "Running database optimizations..." -ForegroundColor Yellow
docker exec erp_web python manage.py migrate

# Check service status
Write-Host "Checking service status..." -ForegroundColor Yellow
.\scripts\docker_setup.ps1 -Status

Write-Host "Performance optimization completed!" -ForegroundColor Green
Write-Host "Your application should now perform better for remote access." -ForegroundColor Green
Write-Host "Access your app at: http://206.191.180.107:8090" -ForegroundColor Cyan