# Monitoring & Attendance Tracking Guide

## Current Status

✅ **Working:**
- Google Calendar integration connected
- Meeting scheduled successfully
- Background monitoring service running (checks every 2 minutes)
- Frontend dashboard showing active sessions

⚠️ **Not Working (Yet):**
- Real-time attendance tracking (requires webhook setup)
- Participant join/exit notifications
- Automatic attendance logging

---

## How Monitoring Works

### 1. Scheduled Class Monitoring

The system automatically:
- **Activates classes** when start time arrives
- **Creates session records** in database
- **Marks classes completed** when end time passes

Check scheduled classes status:
```bash
# View your scheduled classes
curl http://localhost:8000/api/schedule/classes?teacher_email=adil@orinex.co.uk
```

### 2. Active Session Monitoring

View active sessions in two ways:

**A. Frontend Dashboard:**
- Go to: http://localhost:3000
- Click "Real-time Monitoring" tab
- See all active sessions

**B. API Endpoint:**
```bash
curl http://localhost:8000/api/monitoring/active-sessions
```

### 3. Attendance Logs

View attendance history:
```bash
curl http://localhost:8000/api/monitoring/attendance-logs
```

---

## Setting Up Webhook for Real-Time Attendance

To track who joins/exits meetings in real-time, you need to configure Google Meet webhooks:

### Option 1: Local Development (ngrok)

1. **Install ngrok:**
   ```bash
   # Download from: https://ngrok.com/download
   # Or use: choco install ngrok (Windows)
   ```

2. **Start ngrok tunnel:**
   ```bash
   ngrok http 8000
   ```
   
   This gives you a public URL like: `https://abc123.ngrok.io`

3. **Update your .env:**
   ```env
   BACKEND_URL=https://abc123.ngrok.io
   ```

4. **Restart backend:**
   ```bash
   docker-compose restart app
   ```

5. **Configure in Google Workspace:**
   - Go to: https://admin.google.com
   - Navigate to: Apps → Google Workspace → Google Meet
   - Settings → Meet Interoperability
   - Add webhook: `https://abc123.ngrok.io/api/webhook/meet-events`

### Option 2: Production Deployment

Deploy your backend to a public server (AWS, Azure, DigitalOcean, etc.) and use:
```
https://yourdomain.com/api/webhook/meet-events
```

---

## Monitoring Without Webhooks (Manual Testing)

While webhooks aren't set up, you can still test attendance tracking manually:

### Test Attendance Logging

```bash
# Simulate a teacher joining
curl -X POST http://localhost:8000/api/webhook/meet-events \
  -H "Content-Type: application/json" \
  -d '{
    "meetingId": "abc-defg-hij",
    "participantEmail": "adil@orinex.co.uk",
    "eventType": "join",
    "timestamp": "2026-01-02T12:00:00Z"
  }'

# Simulate a student joining
curl -X POST http://localhost:8000/api/webhook/meet-events \
  -H "Content-Type: application/json" \
  -d '{
    "meetingId": "abc-defg-hij",
    "participantEmail": "student@email.com",
    "eventType": "join",
    "timestamp": "2026-01-02T12:01:00Z"
  }'

# Simulate exit
curl -X POST http://localhost:8000/api/webhook/meet-events \
  -H "Content-Type: application/json" \
  -d '{
    "meetingId": "abc-defg-hij",
    "participantEmail": "student@email.com",
    "eventType": "exit",
    "timestamp": "2026-01-02T12:45:00Z"
  }'
```

Then check the monitoring dashboard to see the updates!

---

## Current Monitoring Capabilities

### What You Can Monitor NOW (Without Webhooks):

1. **Scheduled Classes Status:**
   - View upcoming classes
   - See which classes are active
   - Track completed classes

2. **Session Records:**
   - Start/end times of sessions
   - Duration calculations
   - Teacher assignments

3. **Manual Attendance Logs:**
   - Can manually create attendance records
   - View attendance history
   - Generate billing reports

### What Requires Webhooks:

1. **Real-Time Join/Exit Tracking:**
   - Automatic detection when someone joins
   - Automatic logging when someone leaves
   - Live participant count

2. **Automated Attendance:**
   - No manual intervention needed
   - Accurate timestamp capture
   - Automatic duration calculation

---

## Quick Test: Schedule Another Meeting

Try scheduling a meeting for the near future:

```bash
curl -X POST http://localhost:8000/api/schedule/class \
  -H "Content-Type: application/json" \
  -d '{
    "teacher_email": "adil@orinex.co.uk",
    "student_emails": ["student@email.com"],
    "subject": "Test Session",
    "start_time": "2026-01-02T18:00:00Z",
    "duration_minutes": 30
  }'
```

Then:
1. Wait for the start time
2. Check the monitoring dashboard
3. The session should automatically appear as "active"
4. After 30 minutes, it should automatically complete

---

## Frontend Monitoring Views

Your frontend has three monitoring tabs:

### 1. Real-time Monitoring
- Shows currently active sessions
- Displays participants (when webhook is set up)
- Live updates every few seconds

### 2. Attendance Logs
- Historical record of all join/exit events
- Filterable by date, teacher, student
- Exportable for billing

### 3. Financial Hub
- Billing calculations based on attendance
- Revenue reports per teacher/student
- Payment tracking

---

## Next Steps

**For Full Monitoring:**
1. Set up ngrok for local development
2. Configure Google Meet webhook
3. Test with real meetings

**For Production:**
1. Deploy backend to public server
2. Configure production webhook URL
3. Update OAuth redirect URIs

**Current Testing:**
1. Use manual webhook simulation (see above)
2. Monitor scheduled classes via API
3. Check attendance logs manually
