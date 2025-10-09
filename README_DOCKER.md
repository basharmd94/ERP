# ERP Application Docker Setup

This guide will help you dockerize and run your ERP application using Docker and Docker Compose.

## Prerequisites

- Docker Desktop installed and running
- PostgreSQL client tools (for database backup/restore)
- PowerShell (for Windows scripts)

## Architecture

The dockerized application consists of:

- **Web Application**: Django app running on Python 3.12
- **PostgreSQL**: Database server (latest version, port 5433)
- **Redis**: Cache and message broker (latest version)
- **Celery Worker**: Background task processing
- **Celery Beat**: Scheduled task management
- **Nginx**: Reverse proxy and static file serving

## Quick Start

### 1. Build and Start Services

```powershell
# Build images and start all services
.\scripts\docker_setup.ps1 -Build -Start
```

### 2. Backup and Restore Database

```powershell
# Backup local database and restore to Docker
.\scripts\docker_setup.ps1 -BackupAndRestore
```

### 3. Access the Application

- **Web Application**: http://localhost
- **PostgreSQL**: localhost:5433
- **Admin Interface**: http://localhost/admin

## Detailed Setup

### Environment Configuration

The application uses environment variables defined in `.env`:

```env
# Database Configuration
POSTGRES_DB=da
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# Redis Configuration
REDIS_URL=redis://redis:6379/0

# Celery Configuration
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Django Configuration
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,web,erp_web
```

### Docker Services

#### Web Application
- **Image**: Custom Django app (Python 3.12-slim)
- **Port**: 8000 (internal)
- **Volumes**: Static files, media files
- **Dependencies**: PostgreSQL, Redis

#### PostgreSQL
- **Image**: postgres:16
- **Port**: 5433 (external) → 5432 (internal)
- **Volume**: Persistent data storage
- **Environment**: Database credentials from .env

#### Redis
- **Image**: redis:7-alpine
- **Port**: 6379
- **Volume**: Persistent data storage

#### Celery Worker
- **Image**: Same as web application
- **Command**: `celery -A config worker -l info`
- **Dependencies**: PostgreSQL, Redis

#### Celery Beat
- **Image**: Same as web application
- **Command**: `celery -A config beat -l info`
- **Dependencies**: PostgreSQL, Redis

#### Nginx
- **Image**: nginx:1.25-alpine
- **Ports**: 80, 443
- **Configuration**: Reverse proxy to Django app
- **Volumes**: Static files, media files, SSL certificates

## Management Scripts

### Docker Setup Script

```powershell
# Show help
.\scripts\docker_setup.ps1

# Build images
.\scripts\docker_setup.ps1 -Build

# Start services
.\scripts\docker_setup.ps1 -Start

# Stop services
.\scripts\docker_setup.ps1 -Stop

# Restart services
.\scripts\docker_setup.ps1 -Restart

# Show logs
.\scripts\docker_setup.ps1 -Logs

# Show logs for specific service
.\scripts\docker_setup.ps1 -Logs -Service web

# Show status
.\scripts\docker_setup.ps1 -Status

# Clean environment
.\scripts\docker_setup.ps1 -Clean

# Backup and restore database
.\scripts\docker_setup.ps1 -BackupAndRestore
```

### Database Management

#### Backup Local Database

```powershell
# Backup with default settings
.\scripts\backup_db.ps1

# Backup with custom parameters
.\scripts\backup_db.ps1 -BackupPath ".\backups\backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').sql" -Host localhost -Port 5432 -Database da -Username postgres
```

#### Restore to Docker Container

```powershell
# Restore with default settings
.\scripts\restore_db.ps1

# Restore with custom parameters
.\scripts\restore_db.ps1 -BackupPath ".\backups\backup_20240101_120000.sql" -ContainerName erp_postgres -Database da -Username postgres
```

## Development Workflow

### 1. Initial Setup

```powershell
# Clone repository and navigate to project
cd F:\ERP

# Build and start services
.\scripts\docker_setup.ps1 -Build -Start

# Backup and restore database
.\scripts\docker_setup.ps1 -BackupAndRestore
```

### 2. Daily Development

```powershell
# Start services
.\scripts\docker_setup.ps1 -Start

# View logs
.\scripts\docker_setup.ps1 -Logs -Service web

# Restart after code changes
.\scripts\docker_setup.ps1 -Restart -Service web

# Stop services when done
.\scripts\docker_setup.ps1 -Stop
```

### 3. Code Changes

After making code changes:

```powershell
# Rebuild and restart web service
docker-compose build web
docker-compose restart web

# Or rebuild everything
.\scripts\docker_setup.ps1 -Build -Restart
```

## Troubleshooting

### Common Issues

1. **Port Conflicts**
   - Ensure local PostgreSQL is not running on port 5433
   - Check if any other services are using ports 80, 443, 6379

2. **Database Connection Issues**
   - Verify PostgreSQL container is running: `docker-compose ps`
   - Check database logs: `docker-compose logs postgres`

3. **Static Files Not Loading**
   - Run collectstatic: `docker-compose exec web python manage.py collectstatic --noinput`
   - Check Nginx configuration and volume mounts

4. **Celery Tasks Not Processing**
   - Check Celery worker logs: `docker-compose logs celery_worker`
   - Verify Redis connection: `docker-compose logs redis`

### Useful Commands

```powershell
# Execute Django management commands
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic --noinput

# Access container shell
docker-compose exec web bash
docker-compose exec postgres psql -U postgres -d da

# View real-time logs
docker-compose logs -f web
docker-compose logs -f postgres

# Check container resource usage
docker stats
```

## Production Considerations

### Security

1. **Environment Variables**
   - Use strong, unique passwords
   - Set `DEBUG=False` in production
   - Configure proper `ALLOWED_HOSTS`

2. **SSL/TLS**
   - Uncomment HTTPS configuration in Nginx
   - Obtain and configure SSL certificates
   - Update security headers

3. **Database**
   - Use external managed database service
   - Configure regular backups
   - Set up monitoring and alerting

### Performance

1. **Resource Limits**
   - Configure memory and CPU limits in docker-compose.yml
   - Monitor resource usage and adjust as needed

2. **Scaling**
   - Scale Celery workers: `docker-compose up -d --scale celery_worker=3`
   - Use load balancer for multiple web instances

3. **Caching**
   - Configure Redis for session storage
   - Implement application-level caching
   - Use CDN for static files

## Backup and Recovery

### Automated Backups

Create a scheduled task to run regular backups:

```powershell
# Create backup with timestamp
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
.\scripts\backup_db.ps1 -BackupPath ".\backups\backup_$timestamp.sql"
```

### Disaster Recovery

1. **Database Recovery**
   - Restore from latest backup
   - Verify data integrity
   - Update application configuration

2. **Application Recovery**
   - Rebuild Docker images
   - Restore configuration files
   - Restart services

## Monitoring

### Health Checks

- **Application**: http://localhost/health/
- **Database**: Check container logs and connection
- **Redis**: Monitor memory usage and connections
- **Celery**: Monitor task queue and worker status

### Logs

All service logs are available through Docker Compose:

```powershell
# All services
docker-compose logs

# Specific service
docker-compose logs web
docker-compose logs postgres
docker-compose logs redis
docker-compose logs celery_worker
docker-compose logs celery_beat
docker-compose logs nginx
```

## Support

For issues and questions:

1. Check the troubleshooting section
2. Review Docker and application logs
3. Verify environment configuration
4. Test with minimal configuration

Remember to keep your Docker images and dependencies updated regularly for security and performance improvements.