# Database Backup Script for Windows
# This script backs up the local PostgreSQL database

param(
    [string]$BackupPath = ".\db_backup.sql",
    [string]$DatabaseHost = "localhost",
    [string]$Port = "5432",
    [string]$Database = "fixit",
    [string]$Username = "postgres"
)

Write-Host "Starting database backup..." -ForegroundColor Green

# Check if pg_dump is available
try {
    $pgDumpVersion = pg_dump --version
    Write-Host "Found pg_dump: $pgDumpVersion" -ForegroundColor Yellow
} catch {
    Write-Host "Error: pg_dump not found. Please ensure PostgreSQL client tools are installed and in PATH." -ForegroundColor Red
    exit 1
}

# Create backup directory if it doesn't exist
$backupDir = Split-Path -Parent $BackupPath
if (![string]::IsNullOrEmpty($backupDir) -and !(Test-Path $backupDir)) {
    New-Item -ItemType Directory -Path $backupDir -Force
    Write-Host "Created backup directory: $backupDir" -ForegroundColor Yellow
}

# Set environment variable for password (you'll be prompted if not set)
if (-not $env:PGPASSWORD) {
    Write-Host "Note: Set PGPASSWORD environment variable to avoid password prompt" -ForegroundColor Yellow
}

# Perform backup
try {
    Write-Host "Backing up database '$Database' from $DatabaseHost`:$Port..." -ForegroundColor Yellow
    
    $pgDumpArgs = @(
        "--host=$DatabaseHost",
        "--port=$Port",
        "--username=$Username",
        "--dbname=$Database",
        "--verbose",
        "--clean",
        "--no-owner",
        "--no-privileges",
        "--file=$BackupPath"
    )
    
    & pg_dump @pgDumpArgs
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Database backup completed successfully!" -ForegroundColor Green
        Write-Host "Backup saved to: $BackupPath" -ForegroundColor Green
        
        # Show backup file size
        $backupFile = Get-Item $BackupPath
        $sizeInMB = [math]::Round($backupFile.Length / 1MB, 2)
        Write-Host "Backup file size: $sizeInMB MB" -ForegroundColor Yellow
    } else {
        Write-Host "Database backup failed with exit code: $LASTEXITCODE" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "Error during backup: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host "Backup process completed." -ForegroundColor Green