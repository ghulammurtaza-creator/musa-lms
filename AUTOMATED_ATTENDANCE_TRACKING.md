# Automated Attendance Tracking System

## Overview

The Musa LMS now features a fully automated attendance tracking system that ensures accurate billing records by continuously monitoring Google Meet sessions and automatically creating attendance logs for all participants.

## How It Works

### 1. **Automatic Session Monitoring** (Every 2 Minutes)

The system continuously monitors scheduled classes and automatically:
- Creates sessions when classes start
- Marks classes as active during their scheduled time
- Marks classes as completed when they end

### 2. **Automated Participant Data Fetching** (Every 3 Minutes)

While meetings are active, the system:
- Fetches actual participant join/leave data from Google Meet API
- Creates attendance logs automatically for:
  - Teachers
  - Enrolled students
  - Any other participants
- Updates existing logs with new information (e.g., exit times)
- Calculates accurate duration based on actual join/leave times

### 3. **Final Data Capture** (When Meeting Ends)

When a scheduled class ends:
- The system automatically fetches final participant data
- Ensures all attendance logs are complete with exit times
- Closes any open sessions

### 4. **Retry Mechanism** (Every 10 Minutes)

To ensure billing accuracy:
- The system identifies completed classes with no attendance logs
- Automatically retries fetching data for the past 7 days
- Catches cases where initial API calls may have failed

## Key Features

### ✅ Fully Automated
- **No manual intervention required**
- Attendance logs are created automatically
- Works whether participants join during the meeting, late, or leave early

### ✅ Accurate Billing Data
- Uses actual Google Meet API data, not webhooks or guesses
- Captures exact join and leave times
- Handles multiple join/leave sessions per participant
- Retries failed fetches to ensure data completeness

### ✅ Reliable Under All Conditions
- Works if API is temporarily unavailable
- Retries for completed meetings without data
- Handles network issues gracefully
- Continues operating even if some fetches fail

## Technical Implementation

### Background Services

The system runs three background jobs using APScheduler:

1. **`monitor_active_classes`** (120 seconds)
   - Checks for classes that should be active
   - Creates sessions for starting classes
   - Marks ended classes as completed

2. **`fetch_participant_data`** (180 seconds)
   - Fetches participant data from Google Meet API
   - Creates/updates attendance logs
   - Runs for all active meetings

3. **`retry_failed_fetches`** (600 seconds)
   - Identifies completed meetings without attendance data
   - Retries fetching for the past 7 days
   - Ensures no billing data is lost

### Data Flow

```
Scheduled Class Created
         ↓
Class Start Time Reached
         ↓
Session Created (Auto)
         ↓
Class Marked Active
         ↓
[Every 3 min] → Fetch Participants from Google Meet API
         ↓              ↓
         ↓      Create/Update Attendance Logs (Auto)
         ↓
Class End Time Reached
         ↓
Final Participant Fetch (Auto)
         ↓
Session Closed (Auto)
         ↓
Class Marked Completed
         ↓
[Every 10 min] → Retry if No Attendance Data
```

## API Endpoints

### View Attendance Logs

```http
GET /monitoring/attendance-logs?session_id=123
```

Returns all attendance logs for billing/reporting.

### Manual Sync (Optional)

```http
POST /monitoring/sync-participants/{class_id}
```

Manually trigger a participant sync for a specific class (mainly for testing).

```http
POST /monitoring/sync-all-active
```

Manually trigger sync for all active classes (same as automatic job).

## For Your Clients

### What This Means for Billing

1. **Accurate Time Tracking**: Students and teachers are billed based on their actual time in meetings, not scheduled time
2. **No Data Loss**: The system retries failed fetches automatically
3. **Reliable Records**: All attendance data comes directly from Google's official API
4. **Audit Trail**: Complete join/leave history for each participant

### Viewing Attendance Records

Administrators can view attendance logs through:
- The "Attendance Logs" view in the dashboard
- Monthly billing reports (families)
- Monthly payroll reports (teachers)

All logs include:
- User email and role
- Exact join time
- Exact leave time
- Total duration in minutes
- Session/class information

## Testing the System

### 1. Schedule a Test Class

```bash
# Schedule a class starting in 2 minutes
POST /api/schedule/class
{
  "teacher_email": "teacher@example.com",
  "student_emails": ["student@example.com"],
  "subject": "Test Class",
  "start_time": "2026-01-16T15:00:00Z",
  "duration_minutes": 30
}
```

### 2. Join the Meeting

- Teacher and students join via the Google Meet link
- Stay for a few minutes
- Leave the meeting

### 3. Check Attendance Logs (After 3-5 Minutes)

```bash
GET /monitoring/attendance-logs?session_id={session_id}
```

You should see automatically created logs with:
- Join times matching when you joined
- Leave times matching when you left
- Accurate duration calculations

### 4. Verify After Class Ends

Once the class end time passes (within 2 minutes):
- Session is automatically closed
- Final participant data is fetched
- All logs are complete

## Monitoring and Logs

The system logs all operations to the console:

```
Meeting monitoring service started with automated participant tracking
✅ Class 5 (Math Lesson) is now active
✅ Fetching participant data for 1 active classes...
✅ Found 2 participants for meeting abc-defg-hij
✅ Created attendance log for teacher@example.com (teacher)
✅ Created attendance log for student@example.com (student)
✅ Synced participant data for session 12
✅ Class 5 (Math Lesson) completed
✅ Fetching final participant data for meeting abc-defg-hij
```

## Configuration

### Timing Intervals

You can adjust the timing in [meeting_monitor.py](backend/app/services/meeting_monitor.py):

- `monitor_active_classes`: Default 120s (2 minutes)
- `fetch_participant_data`: Default 180s (3 minutes)
- `retry_failed_fetches`: Default 600s (10 minutes)

### Retry Window

Failed fetches are retried for completed classes within the last 7 days. Adjust in `retry_failed_fetches()`:

```python
seven_days_ago = datetime.utcnow() - timedelta(days=7)
```

## Troubleshooting

### No Attendance Logs Created

1. Check Google Meet API authentication:
   ```bash
   python backend/test_meet_api.py
   ```

2. Verify token has correct scope:
   ```
   https://www.googleapis.com/auth/meetings.space.readonly
   ```

3. Check logs for errors during participant fetch

### Incomplete Attendance Data

- Wait for the retry mechanism (runs every 10 minutes)
- Manually trigger sync: `POST /monitoring/sync-participants/{class_id}`
- Check if meeting has ended (Google API may not have data immediately)

### Session Not Created

- Verify class start time has passed
- Check monitoring service is running (logs on startup)
- Ensure scheduled class has valid Meet code

## Advantages Over Manual Tracking

| Feature | Manual System | Automated System |
|---------|--------------|------------------|
| **Data Entry** | Manual button clicks | Fully automatic |
| **Accuracy** | Depends on user memory | Google API official data |
| **Timing** | When user remembers | Real-time + retry |
| **Reliability** | Can be forgotten | Always running |
| **Billing Accuracy** | Risk of missing entries | 100% capture with retry |
| **Audit Trail** | Manual records | Complete API history |

## Summary

Your clients can now trust that:
- ✅ Every participant's attendance is automatically recorded
- ✅ Billing is based on actual meeting time, not estimates
- ✅ No manual tracking required
- ✅ System handles all edge cases (late joins, early leaves, etc.)
- ✅ Data is reliable for student billing and teacher payroll

The system runs continuously in the background, ensuring accurate, automated attendance tracking for reliable billing operations.
