# Delete test session (ID 3) from database
Write-Host "Deleting test session (ID 3) from database..." -ForegroundColor Yellow

# Check if container is running
$containerStatus = docker ps --filter "name=academy_db" --format "{{.Names}}" 2>$null
if (-not $containerStatus) {
    Write-Host "Error: Database container is not running. Please start containers first with:" -ForegroundColor Red
    Write-Host "  docker-compose up -d" -ForegroundColor Cyan
    exit 1
}

# Delete the session
docker exec academy_db psql -U postgres -d academy_db -c "DELETE FROM sessions WHERE id = 3;"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Successfully deleted test session (ID 3)" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to delete session" -ForegroundColor Red
    exit 1
}
