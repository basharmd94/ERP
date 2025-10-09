# Docker Setup Script for ERP Application
# This script handles the complete dockerization process

param(
    [switch]$Build,
    [switch]$Start,
    [switch]$Stop,
    [switch]$Restart,
    [switch]$Logs,
    [switch]$Status,
    [switch]$Clean,
    [switch]$BackupAndRestore,
    [string]$Service = ""
)

function Show-Help {
    Write-Host "ERP Docker Management Script" -ForegroundColor Green
    Write-Host "Usage: .\docker_setup.ps1 [OPTIONS]" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Options:" -ForegroundColor Yellow
    Write-Host "  -Build              Build Docker images" -ForegroundColor White
    Write-Host "  -Start              Start all services" -ForegroundColor White
    Write-Host "  -Stop               Stop all services" -ForegroundColor White
    Write-Host "  -Restart            Restart all services" -ForegroundColor White
    Write-Host "  -Logs               Show logs for all services" -ForegroundColor White
    Write-Host "  -Status             Show status of all services" -ForegroundColor White
    Write-Host "  -Clean              Clean up containers, networks, and volumes" -ForegroundColor White
    Write-Host "  -BackupAndRestore   Backup local DB and restore to Docker" -ForegroundColor White
    Write-Host "  -Service <name>     Target specific service for logs/restart" -ForegroundColor White
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Yellow
    Write-Host "  .\docker_setup.ps1 -Build -Start" -ForegroundColor White
    Write-Host "  .\docker_setup.ps1 -Logs -Service web" -ForegroundColor White
    Write-Host "  .\docker_setup.ps1 -BackupAndRestore" -ForegroundColor White
}

function Test-DockerInstallation {
    try {
        $dockerVersion = docker --version
        $composeVersion = docker-compose --version
        Write-Host "[OK] Docker: $dockerVersion" -ForegroundColor Green
        Write-Host "[OK] Docker Compose: $composeVersion" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "[ERROR] Docker or Docker Compose not found!" -ForegroundColor Red
        Write-Host "Please install Docker Desktop and ensure it's running." -ForegroundColor Yellow
        return $false
    }
}

function Build-Images {
    Write-Host "Building Docker images..." -ForegroundColor Yellow
    docker-compose build --no-cache
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Images built successfully!" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] Failed to build images" -ForegroundColor Red
        exit 1
    }
}

function Start-Services {
    Write-Host "Starting Docker services..." -ForegroundColor Yellow
    docker-compose up -d
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Services started successfully!" -ForegroundColor Green
        Start-Sleep -Seconds 5
        Show-Status
    } else {
        Write-Host "[ERROR] Failed to start services" -ForegroundColor Red
        exit 1
    }
}

function Stop-Services {
    Write-Host "Stopping Docker services..." -ForegroundColor Yellow
    docker-compose down
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Services stopped successfully!" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] Failed to stop services" -ForegroundColor Red
    }
}

function Restart-Services {
    if ($Service) {
        Write-Host "Restarting service: $Service" -ForegroundColor Yellow
        docker-compose restart $Service
    } else {
        Write-Host "Restarting all services..." -ForegroundColor Yellow
        docker-compose restart
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Services restarted successfully!" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] Failed to restart services" -ForegroundColor Red
    }
}

function Show-Logs {
    if ($Service) {
        Write-Host "Showing logs for service: $Service" -ForegroundColor Yellow
        docker-compose logs -f $Service
    } else {
        Write-Host "Showing logs for all services..." -ForegroundColor Yellow
        docker-compose logs -f
    }
}

function Show-Status {
    Write-Host "Docker Services Status:" -ForegroundColor Yellow
    docker-compose ps
    Write-Host ""
    Write-Host "Application URLs:" -ForegroundColor Yellow
    Write-Host "  Web Application: http://localhost" -ForegroundColor Green
    Write-Host "  PostgreSQL:      localhost:5433" -ForegroundColor Green
    Write-Host "  Redis:           localhost:6379" -ForegroundColor Green
}

function Clean-Environment {
    Write-Host "Cleaning up Docker environment..." -ForegroundColor Yellow
    
    # Stop and remove containers
    docker-compose down -v --remove-orphans
    
    # Remove unused images
    docker image prune -f
    
    # Remove unused networks
    docker network prune -f
    
    Write-Host "[OK] Environment cleaned successfully!" -ForegroundColor Green
}

function Backup-And-Restore {
    Write-Host "Starting backup and restore process..." -ForegroundColor Yellow
    
    # Run backup script
    Write-Host "Step 1: Backing up local database..." -ForegroundColor Yellow
    & ".\scripts\backup_db.ps1"
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Backup failed!" -ForegroundColor Red
        exit 1
    }
    
    # Ensure Docker services are running
    Write-Host "Step 2: Ensuring Docker services are running..." -ForegroundColor Yellow
    docker-compose up -d postgres
    Start-Sleep -Seconds 10
    
    # Run restore script
    Write-Host "Step 3: Restoring database to Docker container..." -ForegroundColor Yellow
    & ".\scripts\restore_db.ps1"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Backup and restore completed successfully!" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] Restore failed!" -ForegroundColor Red
        exit 1
    }
}

# Main script execution
if (-not (Test-DockerInstallation)) {
    exit 1
}

# Show help if no parameters provided
if (-not ($Build -or $Start -or $Stop -or $Restart -or $Logs -or $Status -or $Clean -or $BackupAndRestore)) {
    Show-Help
    exit 0
}

# Execute requested actions
if ($Clean) { Clean-Environment }
if ($Build) { Build-Images }
if ($Start) { Start-Services }
if ($Stop) { Stop-Services }
if ($Restart) { Restart-Services }
if ($BackupAndRestore) { Backup-And-Restore }
if ($Logs) { Show-Logs }
if ($Status) { Show-Status }