# How to Get Real Join/End Times from Google Meet

## Current Situation
You're getting meeting start notifications but **NOT getting actual participant join/leave data** because Google Meet doesn't send these events automatically via webhook.

## The Solution: Google Meet Reports API

Google provides a **Reports API** that gives you **actual participant data** including:
- ✅ Real join times
- ✅ Real leave times  
- ✅ Actual duration in seconds
- ✅ Device type used
- ✅ IP address and location
- ✅ Multiple join/leave sessions

⚠️ **Important**: Reports data is available **after the meeting ends** and can take up to **24 hours** to appear.

---

## Setup Steps

### Step 1: Enable Reports API in Google Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project
3. Navigate to **APIs & Services > Library**
4. Search for "**Admin SDK API**"
5. Click **Enable**

### Step 2: Add Reports API Scope to Your OAuth

You need to re-authenticate with additional scope:

1. **Update your `backend/setup_google_oauth.py`** to include the Reports scope:

```python
# Add this scope
SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/calendar.events',
    'https://www.googleapis.com/auth/admin.reports.audit.readonly'  # ADD THIS
]
```

2. **Delete your existing token**:
```bash
cd backend
rm token.json
```

3. **Re-run the OAuth setup**:
```bash
python setup_google_oauth.py
```

4. **Grant the new permissions** when the browser opens

### Step 3: Install Required Package

The Reports API is already included in `google-api-python-client`, but make sure you have it:

```bash
pip install --upgrade google-api-python-client
```

---

## How to Use It

### Option A: Manual Sync After Meeting Ends

Call this endpoint after a meeting finishes:

```bash
POST /api/webhook/sessions/{session_id}/sync-participants
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/webhook/sessions/123/sync-participants
```

**Response:**
```json
{
  "status": "success",
  "message": "Synced 5 participants",
  "updated": 3,
  "created": 2,
  "participants": [
    {
      "email": "teacher@school.com",
      "join_time": "2026-01-15T10:00:23Z",
      "leave_time": "2026-01-15T10:45:12Z",
      "duration_seconds": 2689,
      "device_type": "web",
      "ip_address": "192.168.1.1",
      "location": "US"
    },
    {
      "email": "student@school.com",
      "join_time": "2026-01-15T10:02:15Z",
      "leave_time": "2026-01-15T10:44:30Z",
      "duration_seconds": 2535
    }
  ]
}
```

### Option B: Automatic Sync When Meeting Ends

Update your `meeting_monitor.py` to automatically sync after meeting ends:

```python
# In complete_class method
async def complete_class(self, db: AsyncSession, scheduled_class: ScheduledClass):
    """Mark class as completed and close the session"""
    if scheduled_class.session_id:
        # ... existing code ...
        
        scheduled_class.is_active = False
        scheduled_class.is_completed = True
        await db.commit()
        
        # Schedule participant sync (after a delay to let reports generate)
        # You could use APScheduler to run this 30 minutes later
        await asyncio.sleep(1800)  # Wait 30 minutes
        await self.sync_participants(db, scheduled_class.session_id)

async def sync_participants(self, db: AsyncSession, session_id: int):
    """Sync real participant data from Google Reports"""
    try:
        from app.services.google_meet_reports import get_reports_service
        
        # Get session
        stmt = select(Session).where(Session.id == session_id)
        result = await db.execute(stmt)
        session = result.scalars().first()
        
        if session and session.google_meet_code:
            reports_service = get_reports_service()
            reports_service.authenticate()
            
            participant_data = reports_service.get_meeting_participants(
                meet_code=session.google_meet_code,
                start_time=session.start_time,
                end_time=session.end_time
            )
            
            # Update attendance logs with real data
            for participant in participant_data:
                # ... update logic from webhook endpoint ...
                pass
    except Exception as e:
        print(f"Error syncing participants: {e}")
```

---

## Understanding the Data

### What You Get

| Field | Description | Example |
|-------|-------------|---------|
| `email` | Participant email | `student@school.com` |
| `join_time` | Exact time they joined | `2026-01-15T10:02:15Z` |
| `leave_time` | Exact time they left | `2026-01-15T10:44:30Z` |
| `duration_seconds` | Total time in meeting | `2535` (42 min 15 sec) |
| `device_type` | How they joined | `web`, `android`, `ios` |
| `ip_address` | Their IP address | `192.168.1.1` |
| `location` | Country code | `US`, `UK`, etc. |

### Multiple Sessions

If someone joins, leaves, and rejoins, you'll get **multiple records**:

```json
[
  {
    "email": "student@school.com",
    "join_time": "2026-01-15T10:02:15Z",
    "leave_time": "2026-01-15T10:20:00Z",
    "duration_seconds": 1065
  },
  {
    "email": "student@school.com",
    "join_time": "2026-01-15T10:25:00Z",
    "leave_time": "2026-01-15T10:44:30Z",
    "duration_seconds": 1170
  }
]
```

---

## Important Limitations

### ⚠️ Report Delay
- Reports can take **up to 24 hours** to appear
- Most appear within **1-2 hours** after meeting ends
- For real-time tracking, you need a different solution

### ⚠️ Admin Privileges Required
- You must be a **Google Workspace Admin**
- Or have **delegated admin** for Reports
- Consumer Gmail accounts won't work

### ⚠️ Data Retention
- Reports are available for **180 days** (6 months)
- After that, they're deleted by Google

---

## Alternative Solutions

### If You Need Real-Time Data

**Option 1: Google Meet Add-on**
- Build a Meet add-on with Google Apps Script
- Runs inside the meeting
- Can send real-time webhooks
- **Complex to build and deploy**

**Option 2: Chrome Extension**
- Build extension that monitors Meet tab
- Detects join/leave events from DOM
- Sends to your backend
- **Requires all users to install extension**

**Option 3: Polling Calendar API**
- Check calendar event attendee status
- Not reliable (shows who accepted, not who joined)
- **Very limited data**

### Recommended Approach

**Hybrid Solution:**
1. ✅ Use your current webhook for meeting start/end
2. ✅ Track estimated attendance based on scheduled times
3. ✅ After meeting ends, sync with Reports API for **accurate data**
4. ✅ Update billing based on actual join times

---

## Testing

### Test the Setup

1. **Schedule a test class**:
```bash
POST /api/schedule/class
{
  "teacher_email": "your-email@workspace.com",
  "student_emails": ["student@email.com"],
  "subject": "Test Class",
  "start_time": "2026-01-15T10:00:00Z",
  "duration_minutes": 30
}
```

2. **Join the Meet link** (both teacher and student)

3. **Stay for a few minutes**, then leave

4. **Wait 1-2 hours** for reports to generate

5. **Sync the participants**:
```bash
POST /api/webhook/sessions/{session_id}/sync-participants
```

6. **Check your attendance logs** - they should now have real times!

---

## Troubleshooting

### Error: "No participant data found"
- **Wait longer** - reports can take 24 hours
- **Check meeting actually happened** - no data if no one joined
- **Verify meet_code is correct** in database

### Error: "No valid credentials found"
- **Re-run OAuth setup** with Reports scope
- **Delete token.json** first
- **Grant all permissions** in browser

### Error: "Insufficient permissions"
- **Use Google Workspace Admin account**
- **Enable Admin SDK API** in Cloud Console
- **Check IAM permissions** on your project

### No data for some participants
- **Free Gmail users** may not appear in reports
- **Only Workspace users** are tracked
- **External guests** have limited data

---

## Summary

✅ **What you have now**: Meeting start detection  
✅ **What you need**: Real participant join/leave times  
✅ **Solution**: Google Meet Reports API  
✅ **When available**: 1-24 hours after meeting  
✅ **Setup time**: ~10 minutes  
✅ **Code added**: Already implemented!

**Next Steps:**
1. Enable Admin SDK API
2. Re-authenticate with Reports scope
3. Test with a real meeting
4. Wait for reports to generate
5. Call sync endpoint
6. Verify accurate data!
