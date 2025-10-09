# ERP Docker Quick Guide

## Start to Finish Commands

### 1. Build & Start

```powershell
.\scripts\docker_setup.ps1 -Build
.\scripts\docker_setup.ps1 -Start
```

### 2. Access App

- **Web**: http://localhost
- **Direct**: http://localhost:8090

### 3. Database Backup/Restore

```powershell
# Backup local DB
pg_dump -h localhost -U postgres -d fixit > backups/backup.sql
# Backup with PowerShell script for local DB
$env:PGPASSWORD="postgres"; & "C:\Program Files\PostgreSQL\17\bin\pg_dump.exe" --host=localhost --port=5432 --username=postgres --dbname=fixit --verbose --clean --no-owner --no-privileges --file=.\backups\fixit_backup.sql

# Backup with PowerShell script for remote DB
$env:PGPASSWORD="postgres"; & "C:\Program Files\PostgreSQL\9.4\bin\pg_dump.exe" --host=localhost --port=5432 --username=postgres --password=postgres --dbname=da --verbose --clean --no-owner --no-privileges --file=.\backups\fixit_backup.sql

# Restore to Docker
.\scripts\restore_db.ps1 -BackupFile "backups/backup.sql"
```

# Restore with PowerShell script

.\scripts\restore_db.ps1 -BackupPath ".\backups\fixit_backup.sql" -Database "fixit" -Username "postgres" -Password "postgres"

## Essential Commands

### Docker Management

```powershell
.\scripts\docker_setup.ps1 -Status    # Check status
.\scripts\docker_setup.ps1 -Logs      # View logs
.\scripts\docker_setup.ps1 -Stop      # Stop all
.\scripts\docker_setup.ps1 -Restart   # Restart all
.\scripts\optimize_performance.ps1  # Optimize performance
```

### Database Operations

```powershell
# Django commands
docker exec erp_web python manage.py migrate
docker exec erp_web python manage.py createsuperuser
# on remote
docker exec -it erp_web python manage.py createsuperuser
docker exec erp_web python manage.py collectstatic --noinput

# Database access
docker exec -it erp_postgres psql -U postgres -d fixit
```

### Troubleshooting

```powershell
# Check connectivity
docker exec erp_web python manage.py check --database default

# View specific logs
.\scripts\docker_setup.ps1 -Logs -Service web
.\scripts\docker_setup.ps1 -Logs -Service postgres
```

## Port Configuration (Changed from 8000 to 8090)

Files updated:

- `gunicorn-cfg.py` → `bind = "0.0.0.0:8090"`
- `docker-compose.yml` → `"8090:8090"`
- `nginx/web-project-django.conf` → `server web:8090`
- `Dockerfile` → `EXPOSE 8090`

## Services

- **web**: Django (8090)
- **postgres**: Database (5433)
- **redis**: Cache (6379)
- **nginx**: Proxy (80, 443)
- **celery**: Background tasks
- **celery-beat**: Scheduler
