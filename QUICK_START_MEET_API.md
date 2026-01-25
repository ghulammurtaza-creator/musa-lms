# 🚀 Quick Start: Google Meet Participant Tracking

## The Solution You Found ✅

**Google Meet REST API v2** - The official, modern API for Meet!

## Setup (3 Steps - 5 Minutes)

### 1️⃣ Enable API (1 min)
```
1. Go to: https://console.cloud.google.com/
2. APIs & Services → Library
3. Search: "Google Meet API"
4. Click: ENABLE
```

### 2️⃣ Authenticate (2 min)
```bash
cd backend
rm token.json  # Delete old token if exists
python setup_google_oauth.py --meet
# Browser opens → Grant permissions
```

### 3️⃣ Test It (2 min)
```bash
# Test the setup
python test_meet_api.py

# Schedule a meeting, join it, then:
POST /api/webhook/sessions/{session_id}/sync-participants
```

## What You Get

```json
{
  "email": "teacher@school.com",
  "display_name": "Teacher Name",
  "total_duration_seconds": 3600,
  "sessions": [
    {
      "start_time": "2026-01-16T15:00:23+00:00",
      "end_time": "2026-01-16T16:00:23+00:00",
      "duration_seconds": 3600
    }
  ]
}
```

## Benefits vs Old Method

| Feature | Meet API ✅ | Reports API ❌ |
|---------|-----------|---------------|
| Admin required | No | Yes |
| Data delay | Immediate | 1-24 hours |
| Setup | Simple | Complex |
| Accuracy | Exact | Exact |

## Files Added

```
backend/app/services/google_meet_api.py     ← New service
backend/app/routers/webhook.py              ← Updated
backend/setup_google_oauth.py               ← Added --meet flag
backend/test_meet_api.py                    ← Test script
GOOGLE_MEET_API_GUIDE.md                    ← Full docs
```

## Troubleshooting

**"Meet API not enabled"**  
→ Enable it in Cloud Console (step 1)

**"Invalid credentials"**  
→ Run: `python setup_google_oauth.py --meet`

**"No conference record found"**  
→ Someone must join the meeting first

## API Documentation

🔗 https://developers.google.com/workspace/meet/api/guides/overview

## That's It!

You now have the BEST solution for tracking Google Meet participants! 🎉
