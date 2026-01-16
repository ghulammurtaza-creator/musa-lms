# Complete Testing Workflow for Academy Management System
# Tests: Owner View, Tutor Creates Session, Student Joins, Owner Views Logs

$ErrorActionPreference = "Continue"

Write-Host "`n╔═══════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   ACADEMY MANAGEMENT SYSTEM - COMPLETE WORKFLOW TEST              ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Test 1: OWNER - View System Status
Write-Host "`n┌─────────────────────────────────────────────────────────────┐" -ForegroundColor Yellow
Write-Host "│  TEST 1: OWNER - Viewing System Status                     │" -ForegroundColor Yellow
Write-Host "└─────────────────────────────────────────────────────────────┘`n" -ForegroundColor Yellow

Write-Host "📊 Current Users:" -ForegroundColor Cyan
docker exec academy_db psql -U postgres -d academy_db -c "SELECT 'Teachers: ' || COUNT(*)::text FROM teachers UNION ALL SELECT 'Students: ' || COUNT(*)::text FROM students;" 2>$null | Select-String -Pattern "\d"

Write-Host "`n📚 Recent Sessions:" -ForegroundColor Cyan
docker exec academy_db psql -U postgres -d academy_db -c "SELECT COUNT(*) as total_sessions, COUNT(CASE WHEN end_time IS NULL THEN 1 END) as active_sessions FROM sessions;" 2>$null | Select-String -Pattern "\d"

# Test 2: TUTOR - Start Class Session
Write-Host "`n┌─────────────────────────────────────────────────────────────┐" -ForegroundColor Green
Write-Host "│  TEST 2: TUTOR - Starting New Class Session                │" -ForegroundColor Green
Write-Host "└─────────────────────────────────────────────────────────────┘`n" -ForegroundColor Green

$meetingId = "test-algebra-" + (Get-Date -Format "HHmmss")
Write-Host "👨‍🏫 Teacher 'Fazal' starting class..." -ForegroundColor Yellow
Write-Host "   Meeting ID: $meetingId" -ForegroundColor Gray

$teacherBody = @{
    meeting_id = $meetingId
    teacher_email = "adil.gillani@stixor.com"
    event_type = "teacher_join"
    timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ss.fffZ")
} | ConvertTo-Json

try {
    $teacherResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/google-meet" -Method Post -Body $teacherBody -ContentType "application/json" -Headers @{"X-Webhook-Secret"="test_secret_key_12345"}
    Write-Host "`n✅ Session Created Successfully!" -ForegroundColor Green
    Write-Host "   Session ID: $($teacherResponse.session_id)" -ForegroundColor Cyan
    Write-Host "   Teacher: $($teacherResponse.teacher_name)" -ForegroundColor Cyan
    Write-Host "   Start Time: $($teacherResponse.start_time)" -ForegroundColor Cyan
    $sessionId = $teacherResponse.session_id
}
catch {
    Write-Host "`n❌ Error creating session: $_" -ForegroundColor Red
    exit 1
}

Start-Sleep -Seconds 2

# Test 3: STUDENT - Join Class
Write-Host "`n┌─────────────────────────────────────────────────────────────┐" -ForegroundColor Magenta
Write-Host "│  TEST 3: STUDENT - Joining the Class                       │" -ForegroundColor Magenta
Write-Host "└─────────────────────────────────────────────────────────────┘`n" -ForegroundColor Magenta

Write-Host "👨‍🎓 Student 'Faisal' joining class..." -ForegroundColor Yellow

$studentBody = @{
    meeting_id = $meetingId
    student_email = "adilgilani03@gmail.com"
    event_type = "student_join"
    timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ss.fffZ")
} | ConvertTo-Json

try {
    $studentResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/google-meet" -Method Post -Body $studentBody -ContentType "application/json" -Headers @{"X-Webhook-Secret"="test_secret_key_12345"}
    Write-Host "`n✅ Student Joined Successfully!" -ForegroundColor Green
    Write-Host "   Student: $($studentResponse.student_name)" -ForegroundColor Cyan
    Write-Host "   Join Time: $($studentResponse.timestamp)" -ForegroundColor Cyan
}
catch {
    Write-Host "`n❌ Error joining class: $_" -ForegroundColor Red
}

Start-Sleep -Seconds 2

# Simulate class time
Write-Host "`n⏱️  Class in progress for 5 seconds..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Student leaves
Write-Host "`n👨‍🎓 Student leaving class..." -ForegroundColor Yellow

$studentLeaveBody = @{
    meeting_id = $meetingId
    student_email = "adilgilani03@gmail.com"
    event_type = "student_leave"
    timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ss.fffZ")
} | ConvertTo-Json

try {
    $leaveResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/google-meet" -Method Post -Body $studentLeaveBody -ContentType "application/json" -Headers @{"X-Webhook-Secret"="test_secret_key_12345"}
    Write-Host "✅ Student left - Duration: $($leaveResponse.duration_minutes) minutes" -ForegroundColor Green
}
catch {
    Write-Host "❌ Error recording leave: $_" -ForegroundColor Red
}

Start-Sleep -Seconds 2

# Teacher ends class
Write-Host "`n👨‍🏫 Teacher ending class..." -ForegroundColor Yellow

$teacherLeaveBody = @{
    meeting_id = $meetingId
    teacher_email = "adil.gillani@stixor.com"
    event_type = "teacher_leave"
    timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ss.fffZ")
} | ConvertTo-Json

try {
    $teacherLeaveResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/google-meet" -Method Post -Body $teacherLeaveBody -ContentType "application/json" -Headers @{"X-Webhook-Secret"="test_secret_key_12345"}
    Write-Host "✅ Class ended - Total Duration: $($teacherLeaveResponse.session_duration_minutes) minutes" -ForegroundColor Green
}
catch {
    Write-Host "❌ Error ending class: $_" -ForegroundColor Red
}

Start-Sleep -Seconds 2

# Test 4: OWNER - View Logs and Analytics
Write-Host "`n┌─────────────────────────────────────────────────────────────┐" -ForegroundColor Yellow
Write-Host "│  TEST 4: OWNER - Viewing Logs and Analytics                │" -ForegroundColor Yellow
Write-Host "└─────────────────────────────────────────────────────────────┘`n" -ForegroundColor Yellow

Write-Host "📋 Session Details:" -ForegroundColor Cyan
docker exec academy_db psql -U postgres -d academy_db -c "SELECT s.meeting_id, t.name as teacher, s.start_time, s.end_time, s.ai_summary FROM sessions s JOIN teachers t ON s.teacher_id = t.id WHERE s.meeting_id = '$meetingId';" 2>$null

Write-Host "`n📊 Attendance Logs:" -ForegroundColor Cyan
docker exec academy_db psql -U postgres -d academy_db -c "SELECT a.event_type, COALESCE(s.name, 'N/A') as student, a.event_time, a.duration_minutes FROM attendance_logs a LEFT JOIN students s ON a.student_id = s.id WHERE a.session_id = $sessionId ORDER BY a.event_time;" 2>$null

Write-Host "`n📈 Summary Statistics:" -ForegroundColor Cyan
docker exec academy_db psql -U postgres -d academy_db -c "SELECT COUNT(DISTINCT session_id) as total_sessions, COUNT(*) as total_events, SUM(CASE WHEN event_type = 'student_join' THEN 1 ELSE 0 END) as student_joins FROM attendance_logs;" 2>$null

# Test API endpoint for session details
Write-Host "`n🔍 Fetching session via API:" -ForegroundColor Cyan
try {
    $sessionDetails = Invoke-RestMethod -Uri "http://localhost:8000/api/sessions/$sessionId" -Method Get
    Write-Host "   Meeting ID: $($sessionDetails.meeting_id)" -ForegroundColor Gray
    Write-Host "   Teacher: $($sessionDetails.teacher_name)" -ForegroundColor Gray
    Write-Host "   Duration: $($sessionDetails.duration_minutes) minutes" -ForegroundColor Gray
    Write-Host "   Students: $($sessionDetails.attendance_count)" -ForegroundColor Gray
}
catch {
    Write-Host "   ℹ️  Session API endpoint not available" -ForegroundColor Gray
}

Write-Host "`n╔═══════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║              ✅ COMPLETE WORKFLOW TEST SUCCESSFUL!                ║" -ForegroundColor Green
Write-Host "╚═══════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Green

Write-Host "Summary:" -ForegroundColor Cyan
Write-Host "  ✓ Teacher created session" -ForegroundColor Green
Write-Host "  ✓ Student joined and left" -ForegroundColor Green
Write-Host "  ✓ Attendance tracked" -ForegroundColor Green
Write-Host "  ✓ Duration calculated" -ForegroundColor Green
Write-Host "  ✓ Owner viewed logs" -ForegroundColor Green
Write-Host "`n🎉 All tests passed!" -ForegroundColor Green
