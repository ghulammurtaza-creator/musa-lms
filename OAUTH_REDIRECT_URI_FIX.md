# OAuth Redirect URI Fix

## Error
```
Error 400: redirect_uri_mismatch
```

## Required Action

Add this exact redirect URI to your Google Cloud Console OAuth credentials:
```
http://localhost:8000/api/oauth/callback
```

## Step-by-Step Instructions

### 1. Open Google Cloud Console
Go to: https://console.cloud.google.com/apis/credentials

### 2. Find Your OAuth Client ID
Look for: `1004356259516-40on1fjbd5hmntf13kn1gpoqunv4c9mv`

### 3. Edit the OAuth Client

**If it's a "Desktop application":**
- You need to create a NEW one as "Web application" instead
- Desktop apps don't support redirect URIs properly

**If it's a "Web application":**
- Just click on it to edit

### 4. Add Authorized Redirect URI

In the OAuth client configuration, find the section **"Authorized redirect URIs"**

Click **"+ ADD URI"** and enter:
```
http://localhost:8000/api/oauth/callback
```

### 5. Save Changes

Click **"SAVE"** at the bottom of the page

### 6. Wait 1-2 Minutes

Google OAuth changes can take a minute to propagate

### 7. Test Again

Go back to your app and click "Connect Google Calendar" again

---

## If You Need to Create a New OAuth Client

1. Go to: https://console.cloud.google.com/apis/credentials
2. Click **"+ CREATE CREDENTIALS"** → **"OAuth 2.0 Client ID"**
3. Application type: **"Web application"**
4. Name: `Academy Management System`
5. Authorized redirect URIs:
   - Click **"+ ADD URI"**
   - Enter: `http://localhost:8000/api/oauth/callback`
6. Click **"CREATE"**
7. Copy the **Client ID** and **Client Secret**
8. Update your `.env` file:
   ```bash
   GOOGLE_CLIENT_ID=your-new-client-id
   GOOGLE_CLIENT_SECRET=your-new-client-secret
   ```
9. Restart the backend:
   ```bash
   docker-compose restart app
   ```

---

## Production Deployment Note

When you deploy to production, you'll need to add your production redirect URI as well:
```
https://yourdomain.com/api/oauth/callback
```

And update the `BACKEND_URL` environment variable in your production environment.
