# Test joining a meeting
$joinData = @{
    event_type = "participant.joined"
    meeting_id = "test-meeting-123"
    user_email = "student@example.com"
    user_name = "Test Student"
    timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/api/webhook/google-meet" -Method POST -Body $joinData -ContentType "application/json" -Headers @{"X-Webhook-Secret"="99cda0a876930791b1b15d8163286cefc32273e47e9f52b95735fcd9363ffe12"}
