# Database Restore Script for Docker PostgreSQL
# This script restores a database backup to the Docker PostgreSQL container

param(
    [string]$BackupPath = ".\db_backup.sql",
    [string]$ContainerName = "erp_postgres",
    [string]$Database = "fixit",
    [string]$Username = "postgres"
)

Write-Host "Starting database restore to Docker container..." -ForegroundColor Green

# Check if backup file exists
if (!(Test-Path $BackupPath)) {
    Write-Host "Error: Backup file not found at $BackupPath" -ForegroundColor Red
    Write-Host "Please run the backup script first or provide the correct path." -ForegroundColor Yellow
    exit 1
}

# Check if Docker is running
try {
    $dockerVersion = docker --version
    Write-Host "Found Docker: $dockerVersion" -ForegroundColor Yellow
} catch {
    Write-Host "Error: Docker not found or not running. Please ensure Docker is installed and running." -ForegroundColor Red
    exit 1
}

# Check if container is running
try {
    $containerStatus = docker ps --filter "name=$ContainerName" --format "{{.Status}}"
    if ([string]::IsNullOrEmpty($containerStatus)) {
        Write-Host "Error: Container '$ContainerName' is not running." -ForegroundColor Red
        Write-Host "Please start your Docker containers first using: docker-compose up -d" -ForegroundColor Yellow
        exit 1
    }
    Write-Host "Container '$ContainerName' is running: $containerStatus" -ForegroundColor Yellow
} catch {
    Write-Host "Error checking container status: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Copy backup file to container
try {
    Write-Host "Copying backup file to container..." -ForegroundColor Yellow
    docker cp $BackupPath "$ContainerName`:/tmp/backup.sql"
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: Failed to copy backup file to container" -ForegroundColor Red
        exit 1
    }
    Write-Host "Backup file copied successfully" -ForegroundColor Green
} catch {
    Write-Host "Error copying file to container: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Restore database
try {
    Write-Host "Restoring database '$Database'..." -ForegroundColor Yellow
    
    # First, drop and recreate the database to ensure clean restore
    Write-Host "Dropping and recreating database..." -ForegroundColor Yellow
    docker exec -i $ContainerName psql -U $Username -c "DROP DATABASE IF EXISTS $Database;"
    docker exec -i $ContainerName psql -U $Username -c "CREATE DATABASE $Database;"
    
    # Restore the backup
    Write-Host "Restoring from backup file..." -ForegroundColor Yellow
    docker exec -i $ContainerName psql -U $Username -d $Database -f /tmp/backup.sql
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Database restore completed successfully!" -ForegroundColor Green
    } else {
        Write-Host "Database restore failed with exit code: $LASTEXITCODE" -ForegroundColor Red
        Write-Host "Check the output above for specific error details." -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "Error during restore: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Clean up temporary file in container
try {
    Write-Host "Cleaning up temporary files..." -ForegroundColor Yellow
    docker exec $ContainerName rm -f /tmp/backup.sql
} catch {
    Write-Host "Warning: Could not clean up temporary file in container" -ForegroundColor Yellow
}

Write-Host "Database restore process completed successfully!" -ForegroundColor Green
Write-Host "Your local database has been restored to the Docker PostgreSQL container." -ForegroundColor Green