# Google Calendar Integration Setup Guide

## Overview
Your Academy Management System now supports:
- ✅ **Scheduled Classes** - Teachers schedule classes through your platform
- ✅ **Google Calendar Integration** - Auto-creates Meet links
- ✅ **Automatic Monitoring** - Background service tracks attendance
- ✅ **Webhook Integration** - Real-time attendance updates

## Prerequisites
You need:
1. ✅ Google Workspace account (you have this)
2. ✅ Google Calendar API enabled (you have this)
3. ✅ Google Meet API enabled (you have this)
4. ⚠️ OAuth2 credentials for Calendar API (need to set up)

---

## Setup Steps

### Step 1: Create OAuth2 Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project
3. Navigate to **APIs & Services > Credentials**
4. Click **Create Credentials > OAuth 2.0 Client ID**
5. Select **Desktop application**
6. Download the JSON file
7. Rename it to `credentials.json`
8. Place it in: `backend/credentials.json`

### Step 2: First Authentication

The first time you schedule a class, you'll need to authenticate:

```bash
# The system will open a browser window
# Log in with your Google Workspace admin account
# Grant Calendar access
# Token will be saved automatically
```

### Step 3: Test Scheduling

```bash
# Test the schedule endpoint
curl -X POST http://localhost:8000/api/schedule/class \
  -H "Content-Type: application/json" \
  -d '{
    "teacher_email": "adil.gillani@stixor.com",
    "student_emails": ["adilgilani03@gmail.com"],
    "subject": "Physics",
    "start_time": "2026-01-03T10:00:00Z",
    "duration_minutes": 60
  }'
```

---

## How It Works

### 1. **Teacher Schedules Class**
   - Teacher uses your frontend to schedule
   - Backend calls Google Calendar API
   - Creates calendar event with Meet link
   - Sends invites to students
   - Stores in your database

### 2. **Automatic Monitoring**
   - Background service runs every 2 minutes
   - Checks which classes should be active
   - Creates session automatically at start time
   - Marks class as completed at end time

### 3. **Attendance Tracking**
   - Still uses webhook for real-time updates
   - When teacher/student joins Meet → webhook triggered
   - Attendance logged automatically
   - Duration calculated on exit

---

## API Endpoints

### Schedule a Class
```http
POST /api/schedule/class
Content-Type: application/json

{
  "teacher_email": "teacher@youracademy.com",
  "student_emails": ["student1@email.com", "student2@email.com"],
  "subject": "Mathematics",
  "start_time": "2026-01-03T14:00:00Z",
  "duration_minutes": 90,
  "description": "Algebra lesson"
}
```

**Response:**
```json
{
  "id": 1,
  "teacher_id": 1,
  "subject": "Mathematics",
  "start_time": "2026-01-03T14:00:00Z",
  "end_time": "2026-01-03T15:30:00Z",
  "duration_minutes": 90,
  "google_meet_link": "https://meet.google.com/abc-defg-hij",
  "google_meet_code": "abc-defg-hij",
  "is_active": false,
  "is_completed": false,
  "created_at": "2026-01-02T10:00:00Z"
}
```

### Get Scheduled Classes
```http
GET /api/schedule/classes?teacher_email=teacher@youracademy.com
GET /api/schedule/classes?student_email=student@email.com
GET /api/schedule/classes?upcoming_only=true
```

### Update a Class
```http
PUT /api/schedule/class/1
Content-Type: application/json

{
  "start_time": "2026-01-03T15:00:00Z",
  "duration_minutes": 60
}
```

### Cancel a Class
```http
DELETE /api/schedule/class/1
```

---

## Database Schema

### New Table: `scheduled_classes`
```sql
CREATE TABLE scheduled_classes (
    id SERIAL PRIMARY KEY,
    teacher_id INTEGER REFERENCES teachers(id),
    subject VARCHAR(255),
    start_time TIMESTAMPTZ,
    end_time TIMESTAMPTZ,
    duration_minutes INTEGER,
    google_calendar_event_id VARCHAR(255),
    google_meet_link VARCHAR(500),
    google_meet_code VARCHAR(255),
    session_id INTEGER REFERENCES sessions(id),
    is_active BOOLEAN DEFAULT FALSE,
    is_completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);
```

### Updates to `sessions` Table
```sql
ALTER TABLE sessions ADD COLUMN is_scheduled BOOLEAN DEFAULT FALSE;
ALTER TABLE sessions ADD COLUMN google_meet_code VARCHAR(255);
ALTER TABLE sessions ADD COLUMN google_calendar_event_id VARCHAR(255);
```

---

## Monitoring Service

The background service automatically:

1. **Activates Classes** (at start_time)
   - Creates Session record
   - Marks class as active
   - Ready for webhook events

2. **Completes Classes** (at end_time)
   - Closes Session
   - Auto-exits any remaining participants
   - Calculates final durations
   - Marks class as completed

3. **Runs Every 2 Minutes**
   - Lightweight checks
   - No Google API calls during monitoring
   - All data from your database

---

## Workflow Comparison

### Old Workflow (Manual)
1. Teacher creates Meet link manually
2. Teacher shares link via WhatsApp/Email
3. Student joins from anywhere
4. ❌ No automatic tracking
5. ❌ Manual attendance entry

### New Workflow (Automated)
1. ✅ Teacher schedules via your platform
2. ✅ Google Calendar auto-creates Meet link
3. ✅ Invites sent automatically
4. ✅ Monitoring service creates session
5. ✅ Webhook tracks attendance automatically
6. ✅ Billing calculated automatically

---

## Next Steps

### Phase 1 (Current) ✅
- [x] Backend API complete
- [x] Database models created
- [x] Google Calendar integration
- [x] Monitoring service running

### Phase 2 (Next) 🚧
- [ ] Teacher frontend: Schedule class UI
- [ ] Student frontend: View classes UI
- [ ] Calendar view component
- [ ] Real-time notifications

### Phase 3 (Future) 📋
- [ ] Google Meet API direct integration
- [ ] Live participant tracking
- [ ] Recording management
- [ ] Analytics dashboard

---

## Testing

Test with PowerShell:

```powershell
# Schedule a class
$scheduleData = @{
    teacher_email = "adil.gillani@stixor.com"
    student_emails = @("adilgilani03@gmail.com")
    subject = "Test Class"
    start_time = "2026-01-03T10:00:00Z"
    duration_minutes = 60
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/api/schedule/class" `
  -Method POST `
  -Body $scheduleData `
  -ContentType "application/json"

# View scheduled classes
Invoke-WebRequest -Uri "http://localhost:8000/api/schedule/classes?teacher_email=adil.gillani@stixor.com" `
  -Method GET
```

---

## Troubleshooting

### Error: "Credentials file not found"
- Download `credentials.json` from Google Cloud Console
- Place in `backend/credentials.json`

### Error: "Calendar API not enabled"
- Go to Google Cloud Console
- Enable Calendar API for your project

### Classes not activating automatically
- Check monitoring service logs: `docker logs academy_backend`
- Verify scheduled_classes table has data
- Ensure start_time is in future

### Meet link not created
- Verify Google Workspace account (not free Gmail)
- Check OAuth scopes include Calendar
- Re-authenticate if needed

---

## Security Notes

1. **OAuth Token**: Stored in `backend/token.json` - add to .gitignore
2. **Credentials**: Never commit `credentials.json`
3. **Webhook Secret**: Keep secure in environment variables
4. **Domain Restriction**: Consider limiting to your Workspace domain

---

## Support

For issues:
1. Check backend logs: `docker logs academy_backend`
2. Verify Google Calendar in browser
3. Test API endpoints directly
4. Check database: `docker exec -it academy_db psql -U postgres -d academy_db`

---

**System Status**: ✅ Backend Ready | 🚧 Frontend Pending
**Next**: Build scheduling UI for teachers
