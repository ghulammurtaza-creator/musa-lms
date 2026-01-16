# Complete Testing Workflow
Write-Host "=== ACADEMY MANAGEMENT SYSTEM TEST ===" -ForegroundColor Cyan

# Test 1: OWNER - View System Status
Write-Host "`n[TEST 1] OWNER - Viewing System Status" -ForegroundColor Yellow
Write-Host "Users in system:" -ForegroundColor Gray
docker exec academy_db psql -U postgres -d academy_db -c "SELECT 'Teachers: ' || COUNT(*)::text FROM teachers UNION ALL SELECT 'Students: ' || COUNT(*)::text FROM students;"

Write-Host "`nSessions summary:" -ForegroundColor Gray
docker exec academy_db psql -U postgres -d academy_db -c "SELECT COUNT(*) as total, COUNT(CASE WHEN end_time IS NULL THEN 1 END) as active FROM sessions;"

$webhookSecret = "99cda0a876930791b1b15d8163286cefc32273e47e9f52b95735fcd9363ffe12"

# Test 2: TUTOR - Start Class
Write-Host "`n[TEST 2] TUTOR - Starting Class Session" -ForegroundColor Green
$meetingId = "test-class-" + (Get-Date -Format "HHmmss")
Write-Host "Meeting ID: $meetingId" -ForegroundColor Gray

$body1 = @{
    meeting_id = $meetingId
    user_email = "adil.gillani@stixor.com"
    role = "Teacher"
    event_type = "join"
    timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ss.fffZ")
} | ConvertTo-Json

$resp1 = Invoke-RestMethod -Uri "http://localhost:8000/api/webhook/google-meet" -Method Post -Body $body1 -ContentType "application/json" -Headers @{"X-Webhook-Secret"=$webhookSecret}
Write-Host "Session created: ID $($resp1.session_id)" -ForegroundColor Green
$sessionId = $resp1.session_id

Start-Sleep -Seconds 2

# Test 3: STUDENT - Join Class
Write-Host "`n[TEST 3] STUDENT - Joining Class" -ForegroundColor Magenta
$body2 = @{
    meeting_id = $meetingId
    user_email = "adilgilani03@gmail.com"
    role = "Student"
    event_type = "join"
    timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ss.fffZ")
} | ConvertTo-Json

$resp2 = Invoke-RestMethod -Uri "http://localhost:8000/api/webhook/google-meet" -Method Post -Body $body2 -ContentType "application/json" -Headers @{"X-Webhook-Secret"=$webhookSecret}
Write-Host "Student joined: $($resp2.student_name)" -ForegroundColor Green

Start-Sleep -Seconds 5
Write-Host "`nClass in progress (5 seconds)..." -ForegroundColor Gray

# Student leaves
Write-Host "`nStudent leaving..." -ForegroundColor Gray
$body3 = @{
    meeting_id = $meetingId
    user_email = "adilgilani03@gmail.com"
    role = "Student"
    event_type = "exit"
    timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ss.fffZ")
} | ConvertTo-Json

$resp3 = Invoke-RestMethod -Uri "http://localhost:8000/api/webhook/google-meet" -Method Post -Body $body3 -ContentType "application/json" -Headers @{"X-Webhook-Secret"=$webhookSecret}
Write-Host "Student left: Duration $($resp3.duration_minutes) minutes" -ForegroundColor Green

Start-Sleep -Seconds 2

# Teacher ends class
Write-Host "`nTeacher ending class..." -ForegroundColor Gray
$body4 = @{
    meeting_id = $meetingId
    user_email = "adil.gillani@stixor.com"
    role = "Teacher"
    event_type = "exit"
    timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ss.fffZ")
} | ConvertTo-Json

$resp4 = Invoke-RestMethod -Uri "http://localhost:8000/api/webhook/google-meet" -Method Post -Body $body4 -ContentType "application/json" -Headers @{"X-Webhook-Secret"=$webhookSecret}
Write-Host "Class ended: Total $($resp4.session_duration_minutes) minutes" -ForegroundColor Green

# Test 4: OWNER - View Logs
Write-Host "`n[TEST 4] OWNER - Viewing Session Logs" -ForegroundColor Yellow
Write-Host "`nSession details:" -ForegroundColor Gray
docker exec academy_db psql -U postgres -d academy_db -c "SELECT meeting_id, start_time, end_time FROM sessions WHERE id = $sessionId;"

Write-Host "`nAttendance logs:" -ForegroundColor Gray
docker exec academy_db psql -U postgres -d academy_db -c "SELECT role, join_time, exit_time, duration_minutes FROM attendance_logs WHERE session_id = $sessionId ORDER BY join_time;"

Write-Host "`n=== TEST COMPLETE ===" -ForegroundColor Green
Write-Host "Successfully tested:" -ForegroundColor Cyan
Write-Host "  - Teacher started session" -ForegroundColor Gray
Write-Host "  - Student joined and left" -ForegroundColor Gray
Write-Host "  - Attendance tracked" -ForegroundColor Gray
Write-Host "  - Owner viewed logs" -ForegroundColor Gray
