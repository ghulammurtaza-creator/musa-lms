# Test script to simulate participants leaving the meeting

$webhookUrl = "http://localhost:8000/api/webhook/google-meet"
$secret = "99cda0a876930791b1b15d8163286cefc32273e47e9f52b95735fcd9363ffe12"

Write-Host "`n=== Simulating Meeting Exits ===" -ForegroundColor Cyan

# Student 1 leaves
Write-Host "`n1. Student 1 leaves meeting..." -ForegroundColor Yellow
$student1Exit = @{
    event_type = "participant.left"
    meeting_id = "math-class-101"
    user_email = "student1@academy.com"
    user_name = "Alice Johnson"
    timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
} | ConvertTo-Json

try {
    $response = Invoke-WebRequest -Uri $webhookUrl -Method POST -Body $student1Exit -ContentType "application/json" -Headers @{"X-Webhook-Secret"=$secret} -UseBasicParsing
    Write-Host "✓ Student 1 left successfully" -ForegroundColor Green
} catch {
    Write-Host "✗ Error: $($_.Exception.Message)" -ForegroundColor Red
}

Start-Sleep -Seconds 2

# Student 2 leaves
Write-Host "`n2. Student 2 leaves meeting..." -ForegroundColor Yellow
$student2Exit = @{
    event_type = "participant.left"
    meeting_id = "math-class-101"
    user_email = "student2@academy.com"
    user_name = "Bob Williams"
    timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
} | ConvertTo-Json

try {
    $response = Invoke-WebRequest -Uri $webhookUrl -Method POST -Body $student2Exit -ContentType "application/json" -Headers @{"X-Webhook-Secret"=$secret} -UseBasicParsing
    Write-Host "✓ Student 2 left successfully" -ForegroundColor Green
} catch {
    Write-Host "✗ Error: $($_.Exception.Message)" -ForegroundColor Red
}

Start-Sleep -Seconds 2

# Teacher leaves (ends meeting)
Write-Host "`n3. Teacher leaves meeting..." -ForegroundColor Yellow
$teacherExit = @{
    event_type = "participant.left"
    meeting_id = "math-class-101"
    user_email = "teacher@academy.com"
    user_name = "Mr. Smith"
    timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
} | ConvertTo-Json

try {
    $response = Invoke-WebRequest -Uri $webhookUrl -Method POST -Body $teacherExit -ContentType "application/json" -Headers @{"X-Webhook-Secret"=$secret} -UseBasicParsing
    Write-Host "✓ Teacher left successfully - Meeting ended" -ForegroundColor Green
} catch {
    Write-Host "✗ Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n=== Meeting Complete ===" -ForegroundColor Cyan
Write-Host "Check the 'Attendance Logs' tab to see the recorded attendance"
Write-Host ""
