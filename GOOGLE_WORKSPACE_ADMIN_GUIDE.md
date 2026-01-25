# Google Workspace Integration - Admin Guide

This guide explains how to connect your Google Workspace account to the Musa LMS system.

## Prerequisites

Before you can connect Google Workspace, ensure you have:

1. **Admin Access**: You must be logged in as an administrator
2. **Google Workspace Account**: A Google account with calendar and meet access
3. **Google Cloud Project**: Configured with OAuth credentials (see [GOOGLE_CALENDAR_SETUP.md](GOOGLE_CALENDAR_SETUP.md))

## How to Connect Google Workspace

### Step 1: Access Settings

1. Log in to the admin portal
2. Navigate to **Settings** from the sidebar menu (bottom of the list)
3. You'll see the "Google Workspace Integration" section

### Step 2: Connect Your Account

1. Click the **"Connect Google Calendar"** button
2. You'll be redirected to Google's authentication page
3. Sign in with your Google Workspace account
4. Review the permissions requested:
   - **Google Calendar**: Create and manage calendar events
   - **Google Meet**: Create meeting spaces and track participants
5. Click **"Allow"** to grant permissions

### Step 3: Confirmation

After successful authentication:
- You'll be redirected back to the Settings page
- A success message will appear at the top
- The integration status will show as **"Connected"**
- You can now disconnect if needed by clicking **"Disconnect Calendar"**

## What This Enables

Once connected, the system can:

### ✅ Automated Class Scheduling
- Create Google Calendar events automatically
- Generate Google Meet links for each class
- Send calendar invitations to students

### ✅ Attendance Tracking
- Monitor when students join/leave Google Meet sessions
- Calculate session durations automatically
- Handle reconnections and network interruptions

### ✅ Session Management
- Track active sessions in real-time
- Generate AI-powered session summaries
- Link sessions to student billing

## Features Available After Connection

### For Admins:
- Schedule classes with automatic Meet links
- View real-time active sessions
- Monitor attendance across all classes
- Generate billing reports based on actual attendance

### For Tutors:
- Schedule their own classes (if multi-teacher OAuth is enabled)
- View their students' attendance
- Access automated session summaries

### For Students:
- Receive calendar invitations automatically
- Join classes via Google Meet links
- View their attendance history

## Troubleshooting

### Connection Failed
**Problem**: OAuth error during connection

**Solutions**:
1. Ensure your Google Cloud credentials are correct in the `.env` file
2. Check that the redirect URI matches: `http://localhost:8000/api/oauth/callback`
3. Verify the Google Cloud project has the required APIs enabled:
   - Google Calendar API
   - Google Meet API

### Already Connected
**Problem**: Need to reconnect with different account

**Solutions**:
1. Click "Disconnect Calendar" first
2. Wait a few seconds
3. Click "Connect Google Calendar" again
4. Choose a different Google account

### Permissions Denied
**Problem**: Accidentally denied permissions

**Solutions**:
1. Go to [Google Account Permissions](https://myaccount.google.com/permissions)
2. Remove the Musa LMS app
3. Try connecting again from Settings

## Security Notes

### What Gets Stored
- **OAuth Tokens**: Encrypted access and refresh tokens
- **Account Email**: Your Google account email
- **No Passwords**: Your Google password is never stored or accessed

### Token Security
- Tokens are stored in the database
- Only admins can connect Google Calendar
- Tokens are used only for authorized API calls
- You can revoke access anytime by disconnecting

### Data Privacy
The system only accesses:
- Calendar events it creates
- Google Meet participant data for classes
- No personal emails, files, or other Google services

## Managing the Connection

### To Disconnect:
1. Go to Settings
2. Click **"Disconnect Calendar"** 
3. Confirm the action
4. All future scheduling will be disabled until reconnected

### To Update Permissions:
1. Disconnect your account
2. Reconnect to re-grant permissions
3. This may be needed if we add new features

## Multi-Admin Support

Currently, only one admin account can be connected at a time. If you need to switch admins:

1. Current admin disconnects their account
2. New admin connects their account
3. All existing scheduled classes remain, but new ones use the new account

## Need Help?

If you encounter issues:

1. Check the browser console for error messages
2. Review backend logs: `docker compose logs -f app`
3. Verify your `.env` configuration
4. Consult [GOOGLE_CALENDAR_SETUP.md](GOOGLE_CALENDAR_SETUP.md) for detailed setup

## API Endpoints Used

For developers, these endpoints handle Google integration:

- `GET /api/oauth/connect` - Initiate OAuth flow
- `GET /api/oauth/callback` - Handle OAuth callback
- `GET /api/oauth/status/{email}` - Check connection status
- `POST /api/oauth/disconnect/{email}` - Disconnect account

See [API_REFERENCE.md](API_REFERENCE.md) for complete API documentation.
