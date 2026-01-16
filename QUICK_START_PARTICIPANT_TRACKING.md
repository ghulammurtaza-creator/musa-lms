# Quick Start: Get Real Participant Data from Google Meet

## The Problem
Your current system detects when a meeting **starts** but doesn't get actual participant **join/leave times**.

## The Solution (5 Steps - 10 Minutes)

### Step 1: Enable Admin SDK API (2 min)
1. Go to https://console.cloud.google.com/
2. Select your project
3. Click **APIs & Services** → **Library**
4. Search: **"Admin SDK API"**
5. Click **ENABLE**

### Step 2: Re-authenticate with Reports Scope (3 min)
```bash
cd backend

# Delete old token
rm token.json

# Run setup with reports flag
python setup_google_oauth.py --reports

# Browser will open - grant ALL permissions
```

⚠️ **You must use a Google Workspace Admin account**

### Step 3: Test It (5 min)
```bash
# 1. Schedule a test meeting
POST /api/schedule/class
{
  "teacher_email": "your-admin@workspace.com",
  "student_emails": ["student@email.com"],
  "subject": "Test",
  "start_time": "2026-01-15T15:00:00Z",
  "duration_minutes": 15
}

# 2. Join the meeting (both users)
# 3. Stay 2-3 minutes
# 4. Leave the meeting
```

### Step 4: Wait for Reports (1-24 hours)
Google processes reports **after** the meeting ends. Usually takes 1-2 hours, max 24 hours.

### Step 5: Sync Participant Data
```bash
# Get the session_id from your database or API response
POST /api/webhook/sessions/123/sync-participants
```

**Response:**
```json
{
  "status": "success",
  "updated": 2,
  "participants": [
    {
      "email": "teacher@workspace.com",
      "join_time": "2026-01-15T15:00:23Z",
      "leave_time": "2026-01-15T15:12:45Z",
      "duration_seconds": 742
    },
    {
      "email": "student@email.com", 
      "join_time": "2026-01-15T15:01:15Z",
      "leave_time": "2026-01-15T15:12:30Z",
      "duration_seconds": 675
    }
  ]
}
```

## What You Get

✅ **Exact join time** (not scheduled time)  
✅ **Exact leave time** (not estimated)  
✅ **Real duration** in seconds  
✅ **Device type** (web/mobile/app)  
✅ **IP address** and location  
✅ **Multiple sessions** if they rejoin  

## Important Notes

⚠️ **Not Real-Time**: Reports available 1-24 hours after meeting  
⚠️ **Admin Required**: Must be Google Workspace Admin  
⚠️ **Workspace Only**: Free Gmail users not tracked  
⚠️ **180 Days**: Reports deleted after 6 months  

## Troubleshooting

### "No participant data found"
→ **Wait longer** - reports can take 24 hours  
→ **Check meeting happened** - verify someone joined  

### "Insufficient permissions"  
→ **Use Workspace Admin account**  
→ **Enable Admin SDK API** in Cloud Console  

### "No valid credentials"
→ **Delete token.json**  
→ **Re-run setup with --reports flag**  
→ **Grant all permissions** in browser  

## Need Real-Time Tracking?

If you need **instant** join/leave notifications, you have these options:

1. **Build a Meet Add-on** (complex, requires Apps Script)
2. **Build a Chrome Extension** (requires users to install)
3. **Use a third-party service** (e.g., Whereby, Zoom API)

For most LMS use cases, **1-2 hour delay is acceptable** for billing/attendance.

## Files Created/Modified

✅ `backend/app/services/google_meet_reports.py` - Reports API integration  
✅ `backend/app/routers/webhook.py` - Added sync endpoint  
✅ `backend/setup_google_oauth.py` - Added --reports flag  
✅ `MEET_PARTICIPANT_TRACKING.md` - Full documentation  

## Next Steps

1. **Enable Admin SDK API** (link above)
2. **Run**: `python setup_google_oauth.py --reports`
3. **Schedule a test meeting**
4. **Join and leave**
5. **Wait 1-2 hours**
6. **Call sync endpoint**
7. **See real data!** 🎉
