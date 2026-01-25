# Quick Setup: Enable Real-Time Attendance Tracking

## Why It's Not Working

Your system is monitoring sessions, but **Google Meet isn't sending participant join/exit events** because webhooks aren't configured yet.

## Solution: Set Up ngrok (5 minutes)

### Step 1: Install ngrok

**Download:** https://ngrok.com/download

Or use Chocolatey (Windows):
```powershell
choco install ngrok
```

### Step 2: Start ngrok

```powershell
ngrok http 8000
```

You'll see output like:
```
Forwarding  https://abc123.ngrok-free.app -> http://localhost:8000
```

**Copy that URL!** (e.g., `https://abc123.ngrok-free.app`)

### Step 3: Update Your Environment

Open the root `.env` file and add:
```env
BACKEND_URL=https://abc123.ngrok-free.app
```

### Step 4: Restart Backend

```powershell
docker-compose restart app
```

### Step 5: Reconnect Google Calendar

1. Go to: http://localhost:3000
2. Navigate to "Schedule Classes" tab
3. Click "Disconnect Calendar"
4. Click "Connect Google Calendar" again
5. Authorize

This updates the webhook URL in Google's system.

### Step 6: Configure Google Workspace (Admin Access Required)

**Important:** You need Google Workspace Admin access for this.

1. Go to: https://admin.google.com
2. Navigate to: **Apps → Google Workspace → Google Meet**
3. Click **Meet Interoperability**
4. Under **Webhooks**, add:
   ```
   https://abc123.ngrok-free.app/api/webhook/meet-events
   ```
5. Set **Webhook secret** to the value in your `.env`: `GOOGLE_WEBHOOK_SECRET`

### Step 7: Test!

1. Schedule a new meeting through your dashboard
2. Join the meeting
3. Watch the dashboard - you should see participants appear in real-time!

---

## Alternative: Testing Without Webhooks

If you can't set up ngrok right now, you can manually test attendance tracking:

### Get Your Meeting Code

From your Google Meet URL: `meet.google.com/xxx-yyyy-zzz`
The code is: `xxx-yyyy-zzz`

### Simulate Join Event

```powershell
# Replace with your actual meeting code and emails
$meetCode = "your-meet-code"
$teacherEmail = "adil@orinex.co.uk"
$studentEmail = "participant@email.com"

# Teacher joins
curl.exe -X POST http://localhost:8000/api/webhook/meet-events `
  -H "Content-Type: application/json" `
  -d "{\"meetingId\":\"$meetCode\",\"participantEmail\":\"$teacherEmail\",\"eventType\":\"join\",\"timestamp\":\"2026-01-02T12:50:00Z\"}"

# Student joins
curl.exe -X POST http://localhost:8000/api/webhook/meet-events `
  -H "Content-Type: application/json" `
  -d "{\"meetingId\":\"$meetCode\",\"participantEmail\":\"$studentEmail\",\"eventType\":\"join\",\"timestamp\":\"2026-01-02T12:51:00Z\"}"

# Student leaves
curl.exe -X POST http://localhost:8000/api/webhook/meet-events `
  -H "Content-Type: application/json" `
  -d "{\"meetingId\":\"$meetCode\",\"participantEmail\":\"$studentEmail\",\"eventType\":\"exit\",\"timestamp\":\"2026-01-02T13:30:00Z\"}"

# Teacher leaves
curl.exe -X POST http://localhost:8000/api/webhook/meet-events `
  -H "Content-Type: application/json" `
  -d "{\"meetingId\":\"$meetCode\",\"participantEmail\":\"$teacherEmail\",\"eventType\":\"exit\",\"timestamp\":\"2026-01-02T13:35:00Z\"}"
```

Then refresh your dashboard - you'll see the attendance logs!

---

## What Happens After Webhook Setup

Once webhooks are configured:

1. **Teacher/Student joins Google Meet** → Webhook fires → Attendance logged automatically
2. **Someone leaves** → Webhook fires → Duration calculated automatically
3. **Dashboard updates** → Shows participants in real-time
4. **Billing calculated** → Based on actual attendance time

## Production Deployment

For production, instead of ngrok:
1. Deploy backend to a public server (AWS, Azure, DigitalOcean)
2. Use your domain: `https://api.yourdomain.com/api/webhook/meet-events`
3. Configure that URL in Google Workspace Admin

---

## Quick Check: Is Your Session There?

```powershell
# Check if your session exists
curl http://localhost:8000/api/monitoring/active-sessions

# Check attendance logs
curl http://localhost:8000/api/monitoring/attendance-logs
```
