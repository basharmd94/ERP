# Performance Monitoring Script for ERP Django Application

Write-Host "=== ERP Performance Diagnostics ===" -ForegroundColor Green

# Check Docker services
Write-Host "`n1. Docker Services Status:" -ForegroundColor Yellow
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Check Django debug status
Write-Host "`n2. Django Debug Status:" -ForegroundColor Yellow
$debugStatus = docker exec erp_web python -c "from django.conf import settings; print(f'DEBUG: {settings.DEBUG}')"
Write-Host $debugStatus

# Check database connections
Write-Host "`n3. Database Connection Pool:" -ForegroundColor Yellow
$dbStatus = docker exec erp_web python -c "from django.conf import settings; print(f'CONN_MAX_AGE: {settings.DATABASES[\"default\"].get(\"CONN_MAX_AGE\", \"Not set\")}')"
Write-Host $dbStatus

# Check static files
Write-Host "`n4. Static Files Status:" -ForegroundColor Yellow
$staticStatus = docker exec erp_web python -c "from django.conf import settings; print(f'STATIC_ROOT: {settings.STATIC_ROOT}'); import os; print(f'Static files exist: {os.path.exists(settings.STATIC_ROOT)}')"
Write-Host $staticStatus

# Test response time
Write-Host "`n5. Response Time Test:" -ForegroundColor Yellow
Write-Host "Testing local access (localhost:8090)..."
$localTime = Measure-Command { 
    try { 
        $response = Invoke-WebRequest -Uri "http://localhost:8090" -TimeoutSec 10 -UseBasicParsing
        Write-Host "Local Status: $($response.StatusCode)" -ForegroundColor Green
    } catch {
        Write-Host "Local Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}
Write-Host "Local response time: $($localTime.TotalMilliseconds) ms"

Write-Host "`nTesting remote access (206.191.180.107:8090)..."
$remoteTime = Measure-Command { 
    try { 
        $response = Invoke-WebRequest -Uri "http://206.191.180.107:8090" -TimeoutSec 10 -UseBasicParsing
        Write-Host "Remote Status: $($response.StatusCode)" -ForegroundColor Green
    } catch {
        Write-Host "Remote Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}
Write-Host "Remote response time: $($remoteTime.TotalMilliseconds) ms"

# Check nginx logs for errors
Write-Host "`n6. Recent Nginx Logs:" -ForegroundColor Yellow
docker logs erp_nginx --tail 10

Write-Host "`n=== Performance Check Complete ===" -ForegroundColor Green