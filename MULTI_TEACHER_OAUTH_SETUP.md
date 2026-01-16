# Google Calendar Multi-Teacher OAuth Setup Guide

## Overview
This system allows each teacher to connect their own Google Calendar account, enabling them to schedule classes with automatic Google Meet links. Each teacher authenticates separately through the web interface.

## Step 1: Create Web Application OAuth Client

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Select your project (or create one)
3. Navigate to **APIs & Services** > **Credentials**
4. Click **Create Credentials** > **OAuth 2.0 Client ID**
5. Configure OAuth consent screen if not already done:
   - User Type: **External** (or Internal for Workspace)
   - App name: "Academy Management System"
   - User support email: Your email
   - Scopes: Add `../auth/calendar.events`
   - Test users: Add teacher emails who will use the system

6. Create OAuth Client ID:
   - Application type: **Web application**
   - Name: "Academy LMS Web Client"
   - Authorized redirect URIs:
     - `http://localhost:8000/api/oauth/callback` (for development)
     - `https://yourdomain.com/api/oauth/callback` (for production)
   
7. Click **Create** and note down:
   - Client ID (e.g., `123456789-abc.apps.googleusercontent.com`)
   - Client Secret (e.g., `GOCSPX-...`)

## Step 2: Configure Environment Variables

Edit `backend/.env`:

```env
GOOGLE_CLIENT_ID=your_client_id_here.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_client_secret_here
```

Replace the placeholder values with your actual Client ID and Secret from Step 1.

## Step 3: Enable Required APIs

In Google Cloud Console, enable these APIs:
1. **Google Calendar API**
2. **Google Meet API** (if not already enabled)

## Step 4: Restart Backend

```powershell
docker restart academy_backend
```

## Step 5: Teacher Authentication Flow

### For Teachers:
1. Log into the Academy Management System
2. Go to **Schedule Classes** tab
3. Click **Connect Google Calendar** button
4. You'll be redirected to Google sign-in
5. Sign in with your Google account
6. Grant permissions to create calendar events
7. You'll be redirected back to the app with success message
8. You can now schedule classes with automatic Meet links

### What Gets Stored:
- OAuth credentials are stored securely in the database per teacher
- Only access tokens and refresh tokens are stored (encrypted JSON)
- No passwords are ever stored
- Each teacher's credentials are isolated

## Step 6: Schedule a Class

After connecting Google Calendar:

1. Fill out the **Schedule New Class** form:
   - Teacher email (must be connected)
   - Student emails
   - Subject
   - Start time
   - Duration
   
2. Click **Schedule Class**

3. The system will:
   - Create a Google Calendar event
   - Generate a Google Meet link
   - Send email invitations to students
   - Store the class in the database
   
4. Students receive:
   - Calendar invitation
   - Google Meet link
   - Email reminder before class

## API Endpoints

### Check Connection Status
```http
GET /api/oauth/status/{teacher_email}
```

Response:
```json
{
  "connected": true,
  "teacher_email": "teacher@example.com",
  "teacher_name": "John Doe"
}
```

### Initiate OAuth Flow
```http
GET /api/oauth/connect?teacher_email=teacher@example.com
```

Response:
```json
{
  "authorization_url": "https://accounts.google.com/o/oauth2/v2/auth?..."
}
```

### OAuth Callback (Handled Automatically)
```http
GET /api/oauth/callback?code=...&state=...
```

### Disconnect Google Calendar
```http
POST /api/oauth/disconnect/{teacher_email}
```

## Troubleshooting

### Error: "Teacher must connect Google Calendar first"
- Teacher hasn't connected their Google account yet
- Have the teacher click "Connect Google Calendar" button
- Complete the OAuth flow

### Error: "Invalid OAuth credentials"
- Check that GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET are correct in .env
- Verify the OAuth client is configured as **Web application** (not Desktop)
- Ensure redirect URI matches exactly: `http://localhost:8000/api/oauth/callback`

### Error: "Access denied"
- Teacher declined permissions during OAuth
- Have them reconnect and grant all requested permissions
- Check that teacher's email is added to Test Users (if app is in testing mode)

### Calendar events not created
- Check backend logs: `docker logs academy_backend`
- Verify Google Calendar API is enabled
- Verify teacher's OAuth token hasn't expired (refresh handled automatically)

### Multiple teachers can't connect
- Each teacher must use their own Google account
- Don't share credentials between teachers
- Each teacher gets their own OAuth flow

## Security Notes

1. **OAuth credentials are per-teacher**: Each teacher authenticates separately
2. **Tokens are stored in database**: Encrypted JSON in `teachers.google_credentials` column
3. **Refresh tokens**: Automatically refresh expired access tokens
4. **Scope limits**: Only calendar.events scope (minimal permissions)
5. **Web application flow**: More secure than desktop app flow

## Testing

Test the OAuth flow:

```powershell
# 1. Check if teacher is connected
curl http://localhost:8000/api/oauth/status/teacher@example.com

# 2. If not connected, get authorization URL
curl http://localhost:8000/api/oauth/connect?teacher_email=teacher@example.com

# 3. Open the URL in browser, complete OAuth
# 4. After redirect, check status again
curl http://localhost:8000/api/oauth/status/teacher@example.com

# 5. Schedule a test class through the UI
```

## Production Deployment

When deploying to production:

1. Add production redirect URI to Google OAuth config:
   - `https://yourdomain.com/api/oauth/callback`

2. Update .env with production settings:
   ```env
   FRONTEND_URL=https://yourdomain.com
   ```

3. Ensure HTTPS is enabled (OAuth requires HTTPS in production)

4. Restart backend after configuration changes

## Architecture Benefits

✅ **Multi-tenant**: Each teacher has their own Calendar integration  
✅ **Scalable**: No shared credentials bottleneck  
✅ **Secure**: OAuth2 with automatic token refresh  
✅ **User-friendly**: One-click connection through web UI  
✅ **Maintainable**: No manual token management required  
